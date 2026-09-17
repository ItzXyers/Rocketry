"""Exercises ignition.py's state machine against gpiozero's MockFactory
(forced on in conftest.py) -- no real GPIO hardware involved, runs on any
machine. Covers the safety properties this module exists for: arm
preconditions, the arm->fire token window, the hard on-time cutoff, and the
one-shot latch (including that it survives a fresh IgnitionController
instance, standing in for a process/systemd restart).
"""

import os
import time

import config
import continuity
import ignition


def _reset_pins():
    ignition._arm_sense.pin.drive_low()
    continuity._continuity_sense.pin.drive_low()
    ignition._fire_out.off()


def _make_controller(tmp_path, monkeypatch, **config_overrides):
    monkeypatch.setattr(config, "FIRED_LATCH_PATH", str(tmp_path / "fired.latch"))
    for key, value in config_overrides.items():
        monkeypatch.setattr(config, key, value)
    _reset_pins()
    return ignition.IgnitionController()


def test_arm_rejected_when_arm_switch_open(tmp_path, monkeypatch):
    c = _make_controller(tmp_path, monkeypatch)
    continuity._continuity_sense.pin.drive_high()  # continuity OK, arm switch still open

    result = c.request_arm()

    assert not result.ok
    assert result.reason == "arm_switch_open"


def test_arm_rejected_when_continuity_bad(tmp_path, monkeypatch):
    c = _make_controller(tmp_path, monkeypatch)
    ignition._arm_sense.pin.drive_high()  # arm switch closed, continuity still open/bad

    result = c.request_arm()

    assert not result.ok
    assert result.reason == "continuity_failed"


def test_arm_succeeds_and_issues_a_token(tmp_path, monkeypatch):
    c = _make_controller(tmp_path, monkeypatch)
    ignition._arm_sense.pin.drive_high()
    continuity._continuity_sense.pin.drive_high()

    result = c.request_arm()

    assert result.ok
    assert result.token


def test_fire_rejected_with_wrong_token_and_never_touches_the_gate(tmp_path, monkeypatch):
    c = _make_controller(tmp_path, monkeypatch)
    ignition._arm_sense.pin.drive_high()
    continuity._continuity_sense.pin.drive_high()
    arm = c.request_arm()
    assert arm.ok

    fire = c.request_fire("not-the-real-token")

    assert not fire.ok
    assert fire.reason == "bad_token"
    assert not ignition._fire_out.value


def test_fire_rejected_after_arm_window_expires(tmp_path, monkeypatch):
    c = _make_controller(tmp_path, monkeypatch, ARM_WINDOW_S=0.05)
    ignition._arm_sense.pin.drive_high()
    continuity._continuity_sense.pin.drive_high()
    arm = c.request_arm()
    time.sleep(0.1)

    fire = c.request_fire(arm.token)

    assert not fire.ok
    assert fire.reason == "arm_window_expired"


def test_fire_rechecks_arm_switch_at_fire_time_not_just_at_arm_time(tmp_path, monkeypatch):
    c = _make_controller(tmp_path, monkeypatch)
    ignition._arm_sense.pin.drive_high()
    continuity._continuity_sense.pin.drive_high()
    arm = c.request_arm()
    assert arm.ok

    ignition._arm_sense.pin.drive_low()  # operator opens the arm switch mid-window
    fire = c.request_fire(arm.token)

    assert not fire.ok
    assert fire.reason == "arm_switch_open"
    assert not ignition._fire_out.value


def test_successful_fire_energizes_gate_then_normal_timer_deasserts_it(tmp_path, monkeypatch):
    c = _make_controller(tmp_path, monkeypatch, FIRE_ON_TIME_S=0.05, FIRE_MAX_ON_TIME_S=0.3)
    ignition._arm_sense.pin.drive_high()
    continuity._continuity_sense.pin.drive_high()
    arm = c.request_arm()

    fire = c.request_fire(arm.token)

    assert fire.ok
    assert ignition._fire_out.value  # energized immediately, synchronously
    assert c.has_fired()
    assert os.path.exists(config.FIRED_LATCH_PATH)

    time.sleep(0.15)
    assert not ignition._fire_out.value  # normal on-time timer turned it back off


def test_hard_cutoff_forces_gate_off_independently_of_the_normal_timer(tmp_path, monkeypatch):
    c = _make_controller(tmp_path, monkeypatch)
    # Simulate the normal de-assert timer having failed to run for some
    # reason -- the gate is still energized -- and confirm the failsafe path
    # alone is enough to turn it off.
    ignition._fire_out.on()
    c._firing = True

    c._hard_cutoff()

    assert not ignition._fire_out.value
    assert not c.is_firing()


def test_cannot_rearm_or_refire_after_already_fired(tmp_path, monkeypatch):
    c = _make_controller(tmp_path, monkeypatch, FIRE_ON_TIME_S=0.02, FIRE_MAX_ON_TIME_S=0.05)
    ignition._arm_sense.pin.drive_high()
    continuity._continuity_sense.pin.drive_high()
    arm = c.request_arm()
    fire = c.request_fire(arm.token)
    assert fire.ok
    time.sleep(0.1)

    rearm = c.request_arm()
    assert not rearm.ok
    assert rearm.reason == "already_fired"

    refire = c.request_fire("anything")
    assert not refire.ok
    assert refire.reason == "already_fired"


def test_latch_persists_across_a_fresh_controller_instance(tmp_path, monkeypatch):
    # Stands in for a systemd restart of this service: has_fired() must
    # still read True even though this is a brand new IgnitionController
    # (and thus a brand new in-memory _fired flag) reading the same latch
    # path off disk.
    c1 = _make_controller(tmp_path, monkeypatch, FIRE_ON_TIME_S=0.02, FIRE_MAX_ON_TIME_S=0.05)
    ignition._arm_sense.pin.drive_high()
    continuity._continuity_sense.pin.drive_high()
    arm = c1.request_arm()
    c1.request_fire(arm.token)
    time.sleep(0.1)

    c2 = ignition.IgnitionController()

    assert c2.has_fired()
