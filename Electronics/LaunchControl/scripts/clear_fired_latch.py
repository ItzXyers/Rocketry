#!/usr/bin/env python3
"""Clears the one-shot fired-latch after a real firing (or a bench test).

Deliberately a console script, NOT a webapp endpoint or HTTP route -- the
one-shot latch existing at all is a physical-safety property (no accidental
or remote re-arm of an already-fired channel), so clearing it requires
someone at the Pi's own console, typing a command, having physically
inspected the igniter/channel first.

Run on the Pi: `python3 scripts/clear_fired_latch.py`. Stop the
launchcontrol.service first if it's running -- clearing the file while the
service is up doesn't un-set its in-memory latch (that only clears on
process restart), so a stale in-memory latch would still block a
subsequent /arm.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import config  # noqa: E402


def main() -> int:
    path = config.FIRED_LATCH_PATH
    if not os.path.exists(path):
        print(f"No latch file at {path} -- nothing to clear.")
        return 0

    confirm = input(
        f"About to clear the fired-latch at {path}.\n"
        "Only do this after physically inspecting the igniter/channel and "
        "confirming it's safe to re-arm. Type YES to continue: "
    )
    if confirm != "YES":
        print("Aborted.")
        return 1

    os.remove(path)
    print("Latch cleared. Restart launchcontrol.service to pick this up:")
    print("  sudo systemctl restart launchcontrol.service")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
