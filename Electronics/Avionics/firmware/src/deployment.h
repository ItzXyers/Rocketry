#pragma once

// Owns the burn-wire deployment GPIO (see PIN_DEPLOY in config.h). This
// drives a striker pin into a pressurized CO2 cartridge, not just a buzzer
// chirp — every function here is written with that in mind.

// digitalWrite(LOW) -> pinMode(OUTPUT) -> digitalWrite(LOW), so the gate is
// never left floating/undefined while still configured as an input. MUST be
// the literal first call in setup(), before Serial.begin() — see main.cpp.
void deployment_init();

// Starts the non-blocking firing sequence (sets the gate HIGH, records the
// start time). Returns false and does nothing if this power cycle has
// already fired (one-shot latch — see deployment.cpp). Never blocks;
// deployment_update() must be called every loop() iteration afterward to
// actually turn the gate off again.
bool deployment_fire();

// Services the on-timer and the hard safety cutoff. MUST be called every
// loop() iteration, unconditionally, regardless of flight state — this is
// what guarantees the gate never stays HIGH past DEPLOY_MAX_ON_TIME_MS no
// matter what else the firmware is doing.
void deployment_update();

bool deployment_hasFired();

// True while the gate is currently energized — between deployment_fire()/
// deployment_bench_fire() starting and deployment_update() turning it back
// off (whether via the normal on-time or the hard safety cutoff). Used by
// logger.cpp to guarantee SD writes are never attempted while the
// burn-wire coil is drawing current.
bool deployment_isFiring();

// Bench-test path, deliberately independent of flight self-test/arming
// state so the channel can be tested on bare, partially-wired hardware.
// Two-step ARM -> FIRE gate: bench_arm() opens a
// DEPLOY_BENCH_ARM_TIMEOUT_MS window; bench_fire() only succeeds inside
// that window, and consumes the arm either way. Both routes go through the
// same one-shot latch and safety cutoff as a real flight fire — there is no
// separate "test" firing path with weaker safety behavior.
bool deployment_bench_arm();
bool deployment_bench_fire();
