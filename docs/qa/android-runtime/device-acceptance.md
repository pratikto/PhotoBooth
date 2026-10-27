# Android runtime device acceptance

Use this checklist for the **0.2.0 native runtime**, not the historical 0.1.0
offline preview. All items start **NOT_RUN**. Linux widget fixtures, a signed
APK and the verifier report cannot mark device/provider checks as passed.

## Record the tested installation

Record source commit, APK filename/SHA-256, verifier report, device model,
Android/API version, camera facing, printer model/VID/PID/dot width, test date
and result notes. Keep customer images, booth tokens and merchant keys out of
the report. Use synthetic test photos and the official Sandbox simulator.

Install the verified arm64 debug APK using `adb install -r` with the same signing
key as the existing installation. Preserve app-private photos, pending visits,
consumed game codes, counters and uncertain print jobs. Do not uninstall/clear
storage or change profiles to bypass recovery.

## Manual checks

| ID | Check | Expected behavior | Result |
| --- | --- | --- | --- |
| A01 | Inspect installation identity | Package `id.meong.meongpreview`, runtime 0.2.0; compatible arm64/API24+ device | NOT_RUN |
| A02 | Launch and browse both display orientations/sizes | Original ads, tutorial, twelve designs and Meong Fly are readable; no clipped required controls | NOT_RUN |
| A03 | Tutorial and consumed game code | Tutorial acknowledgement once per visit; code remains consumed after force-stop/relaunch | NOT_RUN |
| C01 | Deny camera permission, then grant it explicitly | Honest unavailable state; manual recovery without fabricated capture or a second camera owner | NOT_RUN |
| C02 | Front/back preview and still capture | Correct orientation; JPEG uses capture resolution, not bounded preview dimensions | NOT_RUN |
| C03 | Three photos and one selected-photo retake | One retake per design; originals retained; quantity means identical paper copies | NOT_RUN |
| C04 | Review/result orientation | Photo areas mirror consistently; original JPEG/detector input, frame/text/logo/QR remain normal | NOT_RUN |
| C05 | Back/Home/minimize during countdown or capture | Countdown cancels; no background capture; reopening waits for native closure | NOT_RUN |
| U01 | Select the exact printer and deny USB permission | No print success; opening settings/health sends no paper job | NOT_RUN |
| U02 | Grant USB and approve one design with two copies | One durable batch, two identical strips/cuts on actual paper; QR readable by phone | NOT_RUN |
| U03 | Disconnect during a send | Uncertain outcome held for inspection; no automatic replay/reopen or extra print after restart | NOT_RUN |
| M01 | Still/video/game audio transitions | Correct single audio owner; pause/resume and close leave no stray sound | NOT_RUN |
| M02 | Face invitation and optional palm | Real inference responds within acceptable device latency; manual shutter remains available if palm is unavailable | NOT_RUN |
| S01 | Configure reachable authenticated HTTPS Sandbox backend | Only booth credentials on Android; merchant key stays on backend; invalid TLS/auth cannot be bypassed | NOT_RUN |
| S02 | Wait before simulator settlement | No capture admission and no manual PAID override | NOT_RUN |
| S03 | Complete official simulator payment | Backend full-price quote/status/grant; STARTED ACK before countdown; one photo transaction | NOT_RUN |
| S04 | Lose connection/ACK, restart, cancel or expire | Same durable order/transaction recovered; no second charge/capture; unknown/paid state remains protected | NOT_RUN |
| S05 | Approve Sandbox photos with explicit USB opt-in | Real paper checked separately; COMPLETED ACK only after all designs; Drive remains off in this profile | NOT_RUN |
| D01 | Ordinary local photo/print while offline | Local results preserved; deferred upload only for explicitly Drive-intended visits | NOT_RUN |
| D02 | Ordinary-mode Drive on a distinct booth identity | Correct unique numbered folder, immutable file mapping, verified link and eventual file bytes; no print replay | NOT_RUN |
| D03 | Scan result QR signed out | Only the assigned customer folder accessible; early pending notice differs from completed upload | NOT_RUN |
| D04 | Retention setup and real expiry | Existing authorized account/setup/deployment and eligible synthetic expiry evidence required; BUG-009 stays OPEN otherwise | NOT_RUN |

Record failures with the exact tested source/APK and redacted diagnostics.
Resolve uncertain paper or payment against its existing journal/backend before
another fulfillment attempt. A partial checklist is a partial result; do not
relabel unrun cases PASS. Production payments, real POS/scanning, release/store
publication and cloud deployment remain separate operations.
