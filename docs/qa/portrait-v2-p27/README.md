# P2.7 local lifecycle and responsive evidence — 2026-10-21

Pre-change rollback: `5fced9d5985d72bb89e046b2b0fe93f7cd247709` (published remote HEAD verified).
Linux Python 3.12.14 / Kivy 2.3.1 / SDL offscreen / software GL / dummy audio.

45 portrait tests PASS, zero skipped (tests.txt). Real Kivy input dispatch at
800×1280 and 452×900 enters the tutorial; its fourth illustration becomes visible
at the bottom scroll position. All page CTA targets are on-screen and at least
48dp high. Old tutorial buttons and gallery swipes cannot alter a later visit.
Suspend blocks touches and browsing timeout; resume starts a fresh idle period.
Expiration clears only prototype visit/cart state. Tutorial-to-template music
continuity remains covered by the fake-provider suite.

Native SoundSDL2 dummy-device smoke PASS: tutorial music, template handoff,
effect playback, suspend/resume, game-preview silence and cleanup. This exercises
the installed native provider and bundled WAVs, **not speaker audibility**.

Twelve new raw screenshots plus SHA-256 hashes are preserved. Re-inspected the
compact invitation/tutorial after increasing small CTA heights to 48dp.
Transitions remain immediate (NoTransition); there is no looping foreground
animation to leave running across retired pages. No game code was integrated.

GitHub exact-SHA CI and downloaded screenshot-artifact inspection remain required.
The API hostname is denied by the running network proxy; api.github.com was added
to the environment draft without changing package-manager presets. Existing
GH_TOKEN is present; no new credential has been requested or copied.
Windows physical touch/speaker acceptance remains open. This evidence does not
close the P2.8 gate or certify production services.
