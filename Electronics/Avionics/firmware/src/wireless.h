#pragma once

// Owns the WiFi AP + HTTP status/arm interface used by a ground-support
// Raspberry Pi to check status and perform the wireless-arm step. Strictly
// read-only except for the single, gated /arm action. Never touches
// PIN_DEPLOY — wireless FIRE is explicitly out of scope; see deployment.*
// for the only path that can energize the burn-wire, which remains
// USB-serial-bench-only.
//
// The AP is only powered while the SW2 arm-interlock switch
// (PIN_ARM_INTERLOCK) is physically closed, and only before real flight —
// once flight_state.cpp confirms BOOST, the radio is latched off for the
// rest of this power cycle regardless of SW2. SW2-open at boot behaves
// exactly like today's firmware (radio off).

// pinMode()s the interlock input, registers HTTP routes, and builds the
// static /config JSON payload. Does NOT bring up the radio -- that only
// happens from wireless_update() once the interlock reads closed. Call
// once from setup(), after flight_state_init() so /status has real
// self-test/baseline data from the AP's first reachable moment.
void wireless_init();

// Services the HTTP server, the SW2-follow AP power lifecycle, and any
// pending deferred shutdown. Call every loop() iteration, after
// deployment_update()/buzzer_update() so this module can never starve
// them.
void wireless_update();

// Debounced reading of the SW2 arm-interlock switch. Exposed for the
// bench-serial STATE command and the /status JSON.
bool wireless_armInterlockClosed();

// Schedules the AP/radio to be disabled and permanently latches it off for
// the rest of this power cycle (regardless of what SW2 does afterward) --
// idempotent, safe to call more than once.
//   immediate=false (default; used by a successful /arm): waits
//     WIFI_ARM_SHUTDOWN_GRACE_MS so the HTTP response has time to actually
//     reach the Pi before the AP disappears; wireless_update() keeps
//     servicing handleClient() during that window.
//   immediate=true (used only by flight_state.cpp's confirmed-BOOST
//     kill): drops the radio on the next wireless_update() call with no
//     grace window -- there's no in-flight HTTP response to protect at
//     that point.
void wireless_requestShutdown(bool immediate = false);
