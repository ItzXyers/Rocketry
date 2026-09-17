"""Owns the SRB igniter fire-output GPIO.

Mirrors the safety discipline of ../firmware/src/deployment.* (one-shot
latch, bounded on-time with a hard ceiling, two-step arm-then-fire window),
adapted for a Linux process instead of a microcontroller loop.

The physical arm switch lives in the igniter's own high-current path in
hardware (already designed, out of scope here) -- this module's arm-sense
reading is advisory/UI-only and can never by itself cause a fire; it is one
of several preconditions checked before the fire GPIO is ever driven.

Import-order safety note: `_fire_out` below is constructed at module import
time, before app.py builds the Flask app or opens any network socket, so
the pin is driven to its safe LOW state as early as this process can manage
it. Unlike a microcontroller, a Pi has many seconds of boot (bootloader,
kernel, systemd) before any userspace code -- including this module -- runs
at all, so the fire line MUST also have an external pulldown independent of
the Pi; that is a hardware requirement this module's safety story assumes
is already in place.
"""

from __future__ import annotations

import json
import logging
import os
import secrets
import threading
import time
from dataclasses import dataclass
from typing import Optional

from gpiozero import Button, DigitalOutputDevice

import config
import continuity

log = logging.getLogger("ignition")

_fire_out = DigitalOutputDevice(config.FIRE_PIN, active_high=True, initial_value=False)
# pull_up=None + active_state=True: the line is externally driven (no Pi
# internal pull resistor engaged), HIGH == arm switch closed. Confirm this
# polarity against the real firing-circuit schematic once it exists -- see
# config.ARM_SENSE_PIN.
_arm_sense = Button(
    config.ARM_SENSE_PIN,
    pull_up=None,
    active_state=True,
    bounce_time=config.GPIO_DEBOUNCE_S,
)


@dataclass
class ArmResult:
    ok: bool
    reason: str
    token: Optional[str] = None
    expires_in_s: Optional[float] = None


@dataclass
class FireResult:
    ok: bool
    reason: str


class IgnitionController:
    """Single instance, shared across all Flask request threads."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._token: Optional[str] = None
        self._token_expires_at: Optional[float] = None
        self._firing = False
        self._fired = self._read_latch()
        if self._fired:
            log.warning(
                "BOOT WARNING: fired-latch already set (%s) -- this channel "
                "has already fired since the latch was last cleared. Do not "
                "arm/fire again without an explicit operator reset via "
                "scripts/clear_fired_latch.py.",
                config.FIRED_LATCH_PATH,
            )

    # -- persisted one-shot latch -------------------------------------------------

    @staticmethod
    def _read_latch() -> bool:
        return os.path.exists(config.FIRED_LATCH_PATH)

    @staticmethod
    def _write_latch() -> None:
        path = config.FIRED_LATCH_PATH
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"fired_at_unix": time.time()}, f)
            f.flush()
            os.fsync(f.fileno())

    # -- read-only status ---------------------------------------------------------

    def has_fired(self) -> bool:
        return self._fired

    def is_firing(self) -> bool:
        return self._firing

    def arm_sense_closed(self) -> bool:
        return _arm_sense.is_active

    def continuity_ok(self) -> bool:
        return continuity.continuity_ok()

    def armed_remaining_s(self) -> Optional[float]:
        with self._lock:
            if self._token is None or self._token_expires_at is None:
                return None
            remaining = self._token_expires_at - time.monotonic()
            return max(0.0, remaining) if remaining > 0 else None

    # -- arm / fire -----------------------------------------------------------

    def request_arm(self) -> ArmResult:
        with self._lock:
            if self._fired:
                return ArmResult(False, "already_fired")
            if self._firing:
                return ArmResult(False, "fire_in_progress")
            if not self.arm_sense_closed():
                return ArmResult(False, "arm_switch_open")
            if not self.continuity_ok():
                return ArmResult(False, "continuity_failed")

            self._token = secrets.token_urlsafe(16)
            self._token_expires_at = time.monotonic() + config.ARM_WINDOW_S
            log.info("armed, window=%.1fs", config.ARM_WINDOW_S)
            return ArmResult(True, "armed", self._token, config.ARM_WINDOW_S)

    def request_fire(self, token: str) -> FireResult:
        with self._lock:
            if self._fired:
                return FireResult(False, "already_fired")
            if self._firing:
                return FireResult(False, "fire_in_progress")

            valid_window = (
                self._token is not None
                and self._token_expires_at is not None
                and time.monotonic() < self._token_expires_at
            )
            token_matches = valid_window and secrets.compare_digest(token or "", self._token)

            # Consumed either way -- a used or expired arm window never
            # carries over to the next attempt, mirroring
            # deployment_bench_fire()'s "consumes the arm either way".
            self._token = None
            self._token_expires_at = None

            if not valid_window:
                return FireResult(False, "arm_window_expired")
            if not token_matches:
                return FireResult(False, "bad_token")

            # Re-check both gates at the moment of fire, not just at arm
            # time -- an operator could open the arm switch or lose
            # continuity during the arm window.
            if not self.arm_sense_closed():
                return FireResult(False, "arm_switch_open")
            if not self.continuity_ok():
                return FireResult(False, "continuity_failed")

            self._firing = True
            self._fired = True
            _fire_out.on()
            try:
                self._write_latch()
            except OSError:
                log.critical(
                    "fired but FAILED to persist the latch to disk -- "
                    "in-memory latch still set for this process, but a "
                    "restart would lose it. Investigate immediately.",
                    exc_info=True,
                )
            log.warning("FIRE: gate energized, on_time=%.2fs", config.FIRE_ON_TIME_S)

            threading.Timer(config.FIRE_ON_TIME_S, self._deassert).start()
            # Independent failsafe timer -- always scheduled, unconditionally
            # turns the gate off no later than FIRE_MAX_ON_TIME_S regardless
            # of whether the timer above already ran. Idempotent.
            threading.Timer(config.FIRE_MAX_ON_TIME_S, self._hard_cutoff).start()

            return FireResult(True, "firing")

    def _deassert(self) -> None:
        with self._lock:
            _fire_out.off()
            self._firing = False
            log.info("fire gate de-energized at normal on-time")

    def _hard_cutoff(self) -> None:
        with self._lock:
            if _fire_out.value:
                log.critical(
                    "HARD CUTOFF: fire gate was still energized at "
                    "FIRE_MAX_ON_TIME_S=%.2fs -- normal de-assert timer did "
                    "not run. Forcing gate off now.",
                    config.FIRE_MAX_ON_TIME_S,
                )
            _fire_out.off()
            self._firing = False


controller = IgnitionController()
