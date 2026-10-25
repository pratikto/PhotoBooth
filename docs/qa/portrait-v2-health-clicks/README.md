# BUG-018 — repeated operator button input

Owner report, **25 October 2026**, on required branch
`feature/portrait-kiosk-v2-next`: the eight operator boxes were all checked, but
the issue note says repeated Device Health button clicks hang the entire app.
The owner clarified: **all buttons were pressed in rapid succession**.
[Recorded report](owner-report-2026-10-25.json).

Raw checked count **8/8 is preserved**, not treated as clean acceptance. H03/H04
responsiveness/lifecycle require targeted retesting; tested HEAD, OS/display and
device metadata were blank and remain unknown. Previous photo/game twenty-cycle
reports stand; no additional twenty-cycle run is imposed here.

## Scope and baseline

Base **f36ebad85a2b3ba5bc93b14a9bb7f3a7f88e723f**, after fast-forwarding the same
authorized branch's three newer documentation commits. Functional baseline is
ea394e8. Fix only the native v2 operator input adapter; preserve the original v1
health UI/backend/worker and existing single-flight report/probe services.
Remote `feature/device-health` was checked read-only: still dbbe055.
No watchdog, driver/device switching, settings write, production/provider action,
automatic restart, second camera, print payload or upload is introduced.

## Reproduction and correction

Three new regressions failed on the unchanged adapter:

- One press followed by repeated releases produced **32 total probe calls**
  instead of initial observation plus one requested refresh.
- A burst of 100 clicks with immediately completed observations performed
  **100 refreshes**, instead of dropping repeated input.
- A press made while disabled, released after the probe finished, ran a new
  probe despite never being a permitted new press.

[Before-fix output](before-tests.txt) preserves all three failures. These prove
input amplification/obsolete-release acceptance; they do **not** reproduce or
establish the exact native Windows freeze stack. No owner log/HEAD was supplied.

The adapter now requires its own fresh permitted press, consumes it once and
drops same-button repeats within 0.75 seconds without queuing work or click SFX.
A press rejected while disabled/cooling down stays rejected after re-enabling.
Existing callbacks claim/disable their controls before the native audio cue.
The gate is per control: **TUTUP remains usable during refresh/save**, and the
next fresh ordinary click works. Closed/minimized/retired controls remain inert.
The renderer/operator tests now synthesize complete press/release clicks, matching native
input instead of bypassing the new guard with release-only dispatches.

Five added regressions cover duplicate releases, fast-completion refresh/save
bursts, disabled-held releases, fresh input after cooldown, and actual native
mixed pointer input through the Kivy event loop. The mixed case sends 120 pointer
clicks over REFRESH/SIMPAN/PILIH DEVICE while report I/O is held: the heartbeat
continues, only one refresh/report is accepted, TUTUP closes immediately, and a
late save cannot update the reopened panel. The disabled PILIH DEVICE stays inert.

## Validation and rollback

[Final focused run](focused-tests.txt): **37 PASS / 0 failures/errors/skips**,
36.547s, covering original-source provenance, health adapters, all sixteen native
operator cases and all twelve unchanged checkout behavior checks. The full
regression follows the final test-helper change; no concurrent renderer runs.

The first full run completed 785 cases in 291.598s with one timeout in the
unchanged MOCK checkout widget fixture's three-second settle limit; the remaining
784 cases passed, none skipped. Screenshots were being rendered concurrently.
[Raw first run](first-full-tests.txt) is preserved rather than relabelled PASS.
The complete unchanged checkout widget module then passed **12/12** in isolation
([output](checkout-tests.txt)). A second full serial run also had the same timeout (298.399s), so renderer
contention alone was not established ([second output](second-full-tests.txt)).
A diagnostic [269-case prefix](prefix-tests.txt), through that exact test with all
modules discovered, passed in 110.697s. The test had a last-frame boundary gap:
results completed during its last native frame were not polled before checking
busy. [Deterministic boundary experiment](checkout-boundary-tests.txt) reproduces
that false rejection; a final poll accepts only the completed result and still
rejects an unfinished worker. Only the test helper receives that final poll;
its three-second budget, assertions and all checkout/payment runtime stay
unchanged. Final affected/full validation follows this fixture correction.

[Browser checks](browser-tests.txt): four fresh unchecked items, safe metadata
import without automatically passing tests, partial Submit 1/4, persistence,
download and no horizontal overflow at 360/452/800px, zero browser errors.
[Form hash/results](form-verification.json). Ten local fixture PNGs, five states
at each required size, were dimension/hash checked and reviewed
([contact sheet](local-contact.jpg), [verification](local-screenshot-verification.json)).
They were rendered before commit with the recorded f36ebad/dirty state; their
operator/render files match the [228-file final source manifest](tested-source-sha256.json).
[Fourteen v1 runtime files](v1-runtime-unchanged.json) remain byte-identical.
All probes/report I/O in tests use fixtures, software GL and dummy audio;
Windows responsiveness and audible speaker acceptance remain pending.

[Fresh four-item Submit form](windows-checklist.html) covers this correction
only. Use F12 or hold the idle Meong header for 1.5 seconds; save available HEAD/
display metadata via the existing safe report/import. Do not fill missing fields
from older reports. Unchecked items remain failed/not run.

Rollback: inspect and apply scoped inverse commits on this same branch back to
the functional behavior of **ea394e8** / pre-fix docs baseline **f36ebad**; do not
reset/recreate payment journals, photo/print manifests, reports or customer data.
The original input-amplification bug would return. No merge/default/release or
production operation is part of this correction.
