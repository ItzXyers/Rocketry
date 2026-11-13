#pragma once

// Owns the WiFi AP + HTTP status/arm interface used by a ground-support
// Raspberry Pi to check status, perform the wireless-arm step, and download
// flight logs from internal flash. Read-only except for the gated /arm action
// and ground-only log deletion. The board fires nothing (no deploy channel since 2026-10-19).
//
// No interlock switch any more (SW2 dropped 2026-10-19): the AP comes up on
// every boot and stays up until a successful /arm or a confirmed BOOST
// (flight_state.cpp) latches it off for the rest of this power cycle.
//
// Routes:
//   GET  /             browser ground console (web_ui.h): status, arm, logs
//   GET  /info         identity JSON (was "/" before the console)
//   GET  /status       live status JSON      GET /config   build constants JSON
//   GET  /logs         plain-text log list   GET /logs.json  same, as JSON
//   GET  /log?n=<nnn>  FLIGHTnnn.CSV download
//   POST /log/delete?n=<nnn>  delete a log (never this boot's file)
//   POST /arm          re-zero + latch the radio off; buzzer plays
//                      ARM_CONFIRM once, or ARM_REJECTED
//
// Join WIFI_AP_SSID from a phone/laptop and open http://192.168.4.1/

// Registers HTTP routes and builds the static /config JSON payload. Does
// NOT bring up the radio -- the first wireless_update() does, so the AP
// never overlaps setup()'s sensor/flash init. Call once from setup(), after
// flight_state_init() so /status has real self-test/baseline data from the
// AP's first reachable moment.
void wireless_init();

// Services the HTTP server, AP power-up, and any pending deferred
// shutdown. Call every loop() iteration, after buzzer_update() so this
// module can never starve it.
void wireless_update();

// True while the AP is up. For the bench-serial STATE command.
bool wireless_radioActive();

// Schedules the AP/radio to be disabled and permanently latches it off for
// the rest of this power cycle -- idempotent, safe to call more than once.
//   immediate=false (default; used by a successful /arm): waits
//     WIFI_ARM_SHUTDOWN_GRACE_MS so the HTTP response has time to actually
//     reach the Pi before the AP disappears; wireless_update() keeps
//     servicing handleClient() during that window.
//   immediate=true (used only by flight_state.cpp's confirmed-BOOST
//     kill): drops the radio on the next wireless_update() call with no
//     grace window -- there's no in-flight HTTP response to protect at
//     that point.
void wireless_requestShutdown(bool immediate = false);
