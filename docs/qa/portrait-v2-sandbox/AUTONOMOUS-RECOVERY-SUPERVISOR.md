# AR-10 — bounded opt-in crash supervision

29 October 2026. Reviewed master/roadmap/operations/matrix, AR-09 release/fences,
original FEAT-009 watchdog/recovery runbooks, watchdog monitor/startup generators,
LaunchLease and dedicated Sandbox launcher. Existing branch only.

Contract before code: preserve observation-only default and never terminate a
hung process to infer worker quiescence. Add explicit dedicated-v2-only opt-in to
restart a GUI only after proven abnormal process exit, live backend, transport-off
Sandbox context, checked bounded journal and released checkout/launch kernel
leases. Persist restart budget before spawn: at most three within ten minutes,
5/10/20-second cooldown, clock rollback/malformed state fail closed. Do not retry
normal exit, operator interrupt or STARTUP_BLOCKED/RECOVERY_HOLD. Current boot
reconciliation/private claim/capture-intent rules run unchanged in each new GUI.
No automatic charge, photo, output, print, upload, data reset or process killing.
A still-running frozen worker stays observer-held for deliberate operator handling.

Use original launchers/leases, not a second camera/payment engine. No service is
installed. Windows development and Ubuntu graphical mini-PC startup remain their
own acceptance gates. Systemd Restart=no and ordinary watchdog defaults remain.

## Source and validation

Run only when desired: `python tools/run_portrait_v2_sandbox.py --restart-crashed-gui`.
Default dedicated launcher and existing ordinary watchdog retain no auto-restart.
The new option belongs only to the dedicated v2 wrapper; legacy trial does not
accept it. Parent validates transport-off context and bounded journal, commits
three-attempt/ten-minute budget before spawn, waits 5/10/20 seconds, checks live
backend and both existing kernel leases, then starts the original GUI command.
Child independently holds its original launch/payment leases and private recovery.
Crash budget corruption/clock rollback/unavailable ownership stops recovery; no
budget reset or journal mutation is used to get around the hold. Windows/Ubuntu
startup generators remain explicit target-path, no service installation and
systemd Restart=no. Android supervisor is not implemented/certified.

Focused **93 PASS / zero FAIL/ERROR/SKIP**:
`test_crash_supervisor test_qris_sandbox_launcher test_kiosk_v2_sandbox test_qris_saved_credentials test_kiosk_v2_watchdog test_kiosk_v2_recovery`.
Five new tests cover budget persistence/backoff, real loop with mocked exited child,
no kill, identical isolated environment, normal/hold/live-child denial, malformed
journal, delivery/production and clock rollback. Existing cross-process launch
leases/startup generation also pass. No actual device/native crash/merchant test.
A frozen live process remains held: safely killing it is not proven by liveness.
Rollback omits the opt-in flag; preserve budget and all customer state.
