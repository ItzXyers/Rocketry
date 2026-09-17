"""RSP4 launch control webapp.

Two independent things this process talks to, kept independent on purpose
(see the plan notes / README.md):
  - the SRB igniter firing circuit, over local GPIO (ignition.py, continuity.py)
  - the flight computer's own wireless ground-support AP, over WiFi (fc_client.py)

Run directly for bench testing (`python app.py`); systemd runs this under
waitress in production -- see systemd/launchcontrol.service.
"""

from __future__ import annotations

import logging

from flask import Flask, jsonify, render_template, request

import config
import fc_client
import ignition

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
log = logging.getLogger("app")

app = Flask(__name__)

# Started at import time (not inside main()) so it runs whether this process
# is launched via `python app.py` (bench testing) or `waitress-serve app:app`
# (systemd, production) -- see systemd/launchcontrol.service.
fc_client.client.start()


@app.get("/")
def index():
    return render_template("index.html")


# -- flight computer (WiFi station link) -------------------------------------


@app.get("/api/fc/status")
def fc_status():
    s = fc_client.client.cached_status()
    return jsonify(
        {
            "reachable": s.reachable,
            "last_success_unix": s.last_success_unix,
            "last_error": s.last_error,
            "data": s.data,
        }
    )


@app.post("/api/fc/arm")
def fc_arm():
    outcome = fc_client.client.post_arm()
    return jsonify(
        {
            "ok": outcome.ok,
            "ambiguous": outcome.ambiguous,
            "reason": outcome.reason,
            "data": outcome.data,
        }
    ), (200 if outcome.ok else 409)


# -- SRB launch control (local GPIO) -----------------------------------------


@app.get("/api/ignition/status")
def ignition_status():
    return jsonify(
        {
            "fired": ignition.controller.has_fired(),
            "firing": ignition.controller.is_firing(),
            "arm_sense_closed": ignition.controller.arm_sense_closed(),
            "continuity_ok": ignition.controller.continuity_ok(),
            "armed_remaining_s": ignition.controller.armed_remaining_s(),
        }
    )


@app.post("/api/ignition/arm")
def ignition_arm():
    result = ignition.controller.request_arm()
    body = {"ok": result.ok, "reason": result.reason}
    if result.ok:
        body["token"] = result.token
        body["expires_in_s"] = result.expires_in_s
        log.warning("SRB ARM requested from %s", request.remote_addr)
    return jsonify(body), (200 if result.ok else 409)


@app.post("/api/ignition/fire")
def ignition_fire():
    token = (request.get_json(silent=True) or {}).get("token", "")
    result = ignition.controller.request_fire(token)
    log.warning(
        "SRB FIRE requested from %s -> ok=%s reason=%s",
        request.remote_addr,
        result.ok,
        result.reason,
    )
    return jsonify({"ok": result.ok, "reason": result.reason}), (
        200 if result.ok else 409
    )


def main() -> None:
    # threaded=True: fine for a closed hotspot serving one or two phones.
    # systemd uses waitress instead for anything more sustained -- see
    # systemd/launchcontrol.service. Either way, this MUST stay single-
    # process: the arm token and ignition.IgnitionController's state live in
    # this process's memory, not shared storage. A future move to e.g.
    # `gunicorn -w 4` would silently give each worker its own token and its
    # own idea of whether the channel has fired.
    app.run(host=config.WEB_HOST, port=config.WEB_PORT, threaded=True)


if __name__ == "__main__":
    main()
