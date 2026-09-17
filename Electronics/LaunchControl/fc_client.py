"""WiFi-station client to the flight computer's wireless.cpp HTTP API.

Two behaviors here are non-obvious from wireless.cpp's HTTP surface alone
and are specifically handled below:

- handleArm() blocks roughly 4-5.5s on the ESP32 (pad-baseline recapture +
  velocity-estimator reset) before responding -- FC_ARM_HTTP_TIMEOUT_S gives
  real margin over that.
- A successful /arm deliberately drops the AP ~500ms later
  (WIFI_ARM_SHUTDOWN_GRACE_MS is the ESP32-side constant). A
  connection-reset/timeout that happens immediately after receiving a 200,
  or instead of ever receiving a body, is EXPECTED there, not a failure --
  see post_arm() below.

Runs a background poll thread that keeps a cached FlightComputerStatus
so app.py's request handlers never block on the flight computer being slow
or offline (e.g. SW2 open, out of range).
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import requests

import config

log = logging.getLogger("fc_client")


@dataclass
class FlightComputerStatus:
    reachable: bool = False
    last_success_unix: Optional[float] = None
    last_error: Optional[str] = None
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class ArmOutcome:
    ok: bool
    ambiguous: bool  # True: AP likely dropped right after success, per design
    reason: str
    data: dict[str, Any] = field(default_factory=dict)


class FlightComputerClient:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._status = FlightComputerStatus()
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _poll_loop(self) -> None:
        while not self._stop.is_set():
            self._poll_once()
            self._stop.wait(config.FC_STATUS_POLL_INTERVAL_S)

    def _poll_once(self) -> None:
        try:
            resp = requests.get(
                f"{config.FC_BASE_URL}/status", timeout=config.FC_HTTP_TIMEOUT_S
            )
            resp.raise_for_status()
            with self._lock:
                self._status = FlightComputerStatus(
                    reachable=True, last_success_unix=time.time(), data=resp.json()
                )
        except requests.RequestException as exc:
            with self._lock:
                self._status = FlightComputerStatus(
                    reachable=False,
                    last_success_unix=self._status.last_success_unix,
                    last_error=str(exc),
                )

    def cached_status(self) -> FlightComputerStatus:
        with self._lock:
            return self._status

    def get_config(self) -> dict[str, Any]:
        resp = requests.get(
            f"{config.FC_BASE_URL}/config", timeout=config.FC_HTTP_TIMEOUT_S
        )
        resp.raise_for_status()
        return resp.json()

    def post_arm(self) -> ArmOutcome:
        try:
            resp = requests.post(
                f"{config.FC_BASE_URL}/arm", timeout=config.FC_ARM_HTTP_TIMEOUT_S
            )
        except requests.RequestException as exc:
            # The AP is designed to drop ~500ms after a successful /arm, so a
            # reset/timeout here is ambiguous, not necessarily a failure --
            # the request may well have succeeded on the ESP32 side. Report
            # it as such rather than a hard error.
            log.warning("post_arm: connection dropped (%s) -- ambiguous, AP may have gone down as designed", exc)
            return ArmOutcome(
                ok=False,
                ambiguous=True,
                reason="connection_dropped_ambiguous_may_have_succeeded",
            )

        if resp.status_code == 200:
            return ArmOutcome(ok=True, ambiguous=False, reason="armed", data=resp.json())

        try:
            data = resp.json()
        except ValueError:
            data = {}
        return ArmOutcome(
            ok=False,
            ambiguous=False,
            reason=data.get("reason", f"http_{resp.status_code}"),
            data=data,
        )


client = FlightComputerClient()
