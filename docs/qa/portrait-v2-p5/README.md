# P5 readiness and final Windows acceptance

**P5 baseline scope.** The 688-test source `9433010` below is preserved as the
P5 checkpoint. The later read-only operator increment at `ea394e8` has 780 local
PASS, matching CI and its own eight-item form. Use the
[current ledger](../../test_checklist.md) for both; this P5 form/runbook remains
the new Windows/Sandbox integration acceptance package. Source work may continue
within approved scope while laptop checks wait.

Owner approved P4b Sandbox followed by P5 preparation, with manual tests at the
end. This package prepares regression/metadata/acceptance; **P5 commercial
certification is pending** actual Windows hardware, merchant Sandbox, privacy,
Drive retention and explicit release approval. No production activation or merge.

The inventory still performs no printer probe by default. For the new explicit
read-only UX-07 route evidence option and its Windows/Ubuntu limitations, use
[the device-evidence contract](../portrait-v2-sandbox/UX07-PRINTER-DEVICE-EVIDENCE.md).
Route observations never pass physical or purchased-payment acceptance.

## Start on Windows

Use the existing working Kivy environment, not a new project:

```powershell
git switch feature/portrait-kiosk-v2-next
git pull --ff-only origin feature/portrait-kiosk-v2-next
.\.venv-kivy\Scripts\Activate.ps1
python -m pip install -r requirements-qris.txt
python tools/check_portrait_v2.py
Start-Process docs/qa/portrait-v2-p5/windows-checklist.html
python tools/run_portrait_v2.py
```

Import `data/diagnostics/windows-readiness.json` in the checklist. It reads the
local Git HEAD/branch/dirty state, dependency versions, Windows primary physical
display/scaling and configured camera index. It never opens camera/audio/printer,
contacts a provider or lists secrets/customer paths. Verify the actual kiosk
monitor when multiple displays are connected. Camera model/speaker remain blank
until the operator supplies them. Dependency/configuration presence is not a
physical PASS. A dirty checkout, wrong branch, invalid index or conflicting modes
is flagged for attention; optional merchant dependencies are required when enabled.

Test local startup/media/game/photo first; then close it and run:

```powershell
python tools/run_portrait_v2_sandbox.py
```

This reuses the existing credential-isolated QRIS trial. Enter the Merchant ID
and hidden **Sandbox** Server Key locally, never in chat. Use only the official
Midtrans QRIS simulator shown in the terminal. Printer/Drive remain disabled in
this launcher. [Full payment/price/recovery contract](../portrait-v2-sandbox/README.md).
Game's local DEMO discount does not authorize merchant QRIS promo; explicit full
price/no-promo confirmation precedes every new Sandbox order.

[Open the 26-item checklist](windows-checklist.html). No items start checked.
Submit prepares a prompt for chat; copy/download/print and local persistence are
retained from the accepted existing form. It cannot send directly into chat.
Imported metadata does not pass tests. Blank means failed/not run, including
optional hardware items. The twenty cycles previously accepted remain preserved;
G01/G02 here concern the **new Sandbox integration** and require twenty new
completed integration cycles before they can be counted PASS.

## Remaining external gates

- Real merchant credentials + official simulator create/settle/cancel/restart
  and provider outage behavior; cloud fixtures cannot certify these.
- Windows kiosk touch/scaling/camera/speaker/video and prolonged use on the
  exact recorded source. Earlier owner acceptance stays historical at unknown HEAD.
- Physical printer batch and uncertain-job inspection (ordinary GUI operator
  opt-in only); no auto retry or automatic print in merchant trial.
- Actual Drive download/offline synchronization and **30-day cloud deletion**
  evidence (BUG-009 remains OPEN); privacy/operator signoff.
- Trusted backend game-promo contract remains absent from existing QRIS service.
  Existing MOCK discount works; no new trusted merchant promotion was invented.
- Merge, deployment, production configuration and release remain unapproved.

If a provider/device gate cannot be run, leave it blank and retain the evidence.
Do not delete payment/print journals, resend a charge, or replay capture to
force a checklist pass. RECOVERY intentionally requires operator reconciliation;
there is no unsafe “reset paid order” button.

## Regression and rollback

The existing `tools/run_kiosk_unittests.py` now also accepts optional module names,
preserving its full-discovery default and raw OS output. CI uses it for native
GUI/payment steps so Kivy cannot hide failures; reports are retained alongside
screenshots. One complete final regression was run after the P5 source changes;
focused checks cover earlier stages. Offline QR screenshots are marked fixtures.

Checkpoints on `feature/portrait-kiosk-v2-next`:

| Source | Purpose |
| --- | --- |
| d6fb5d4 | Accepted visual/local-flow baseline before Sandbox imports |
| 37da798 | Unchanged QRIS service/client + 124 original tests |
| ce603c2 | Native Sandbox handoff, 195 focused PASS, reviewed two-size views |
| 9433010 | Final P5 source, 688 full PASS, matching-source CI three-job SUCCESS |

Stop the trial before code rollback. Preserve `data/kiosk-v2-sandbox` databases,
visit journals and photo/print manifests; reconcile any active order first.
Use inverse source commits on the same authorized branch after inspection;
never force push, change master, erase journals or roll back payment data.
The ordinary v2 launcher remains available without enabling Sandbox.

## Final local evidence

- **688 full tests PASS**, zero failures/errors/skips, 211.646s, Linux Python
  3.12.14/Kivy 2.3.1/SDL offscreen + dummy PCM, with real bundled face/palm
  fixtures, synthetic video/photo/print/payment fixtures. [Full output](full-tests.txt).
- Command: `PHOTOBOOTH_TEST_GUI=1 PHOTOBOOTH_TEST_AUDIO=1 PHOTOBOOTH_TEST_VIDEO=1
  PHOTOBOOTH_PALM_TEST_ASSETS=<offline-assets> MEONG_CI_TEST_REPORT=<report>
  python tools/run_kiosk_unittests.py` using the prepared cloud environment.
- [Focused 10 PASS](focused-tests.txt) cover standalone camera redraw, five native
  Sandbox HTTP/photo handoff cases and four preflight guards. Missing STARTED ACK
  cannot begin countdown; retry acknowledges the same bound transaction.
- [Browser verification](browser-checks.txt): 26 initially empty items, metadata
  import leaves tests unchecked, twenty-cycle guard, partial Submit 2/26 with
  merchant unchecked, persistence and 360/452/800px bounds, no browser errors.
- [Tested source hashes](tested-source-sha256.json) bind the final working-tree
  code/tests/workflow/dependencies to its eventual source commit. Documentation
  evidence added afterward does not change those functional files.
- Earlier ce603c2 CI passed the payment step but exposed one standalone PhotoViews
  regression in the broader native suite. It is reproduced locally and corrected:
  the standalone preview uses its existing free-test behavior; the complete
  Sandbox app retains its durable admission guard. Final 688-test run includes
  the previously failing test. Native CI now preserves raw result reports.

These are automated source/fixture results, not real speaker, camera, paper,
merchant credential, privacy or 30-day Drive certification. BUG-009 remains OPEN.

Final functional source: **9433010faee04c58789e9778d2297308492b60c5**, pushed
and remote HEAD verified. [Clean-cloud inventory](cloud-readiness.json) reports
READY_FOR_MANUAL_TEST with all physical/provider acceptance still NOT_RUN;
Linux resolution/scaling/camera model/speaker remain unknown rather than invented.

For merchant keys, open the Midtrans **Sandbox** dashboard → Settings → Access
Keys; use Merchant ID and Sandbox Server Key, not Client Key/Production. This
follows the [existing QRIS trial runbook at the reused source](https://github.com/pratikto/PhotoBooth/blob/3cc8a8e360e8c2100a3077b755664eb61d0216ea/docs/QRIS_SANDBOX_TRIAL.md).
The local trial verifies provider status by polling. Public HTTPS webhook ingress
is a separate unrun gate requiring an approved endpoint; no tunnel or deployment
is created here. Original signed-callback/reconciliation tests remain in the
source regression, but fixtures do not prove real webhook delivery.

## Matching-source CI and screenshot review

[CI 40109206417](https://github.com/pratikto/PhotoBooth/actions/runs/40109206417)
on source **9433010**: all three jobs SUCCESS (navigation/audio, Linux native
GUI/payment/screenshots, Windows native dummy audio). [Job record](final-ci.json).
The preserved payment step runs **138 PASS / zero skips**; native GUI step runs
82 cases with **81 PASS / one optional palm-model-assets skip**. That real-model
case is covered by the final local 688-test run with the supplied offline assets;
CI's skip is retained, not relabelled. [Raw CI reports](ci-reports/).

All **109 PNGs** in artifact `12566490205` were checked against their reported
source, dimensions and SHA-256; artifact ZIP digest also matches GitHub's digest.
[Verification record](ci-screenshot-verification.json) paths refer to the downloaded
artifact tree. Ten native Sandbox PNGs are retained in [screenshots/](screenshots/).
[Sandbox contact sheet](sandbox-contact.jpg) and [gallery/photo/original-game
regression sheet](regression-contact.jpg) were visually reviewed at 800×1280 and
452×900: captions, amounts, QR, consent and actions remain within bounds; gallery
strip focus and left-anchored game player remain intact. Screenshot QR is an
**offline nonpayable fixture**, not an actual merchant QR/payment result.

No additional functional source edits followed the 688-test regression. The
source-hash manifest still matches the final commit. Evidence-only documentation
is pushed with CI skipped; no successful GUI workflow is rerun for documentation.

P4b source integration and P5 readiness package are ready for the owner's final
manual acceptance. **P5 commercial release certification remains pending** the
external gates above. There are no remaining failing automated tests. BUG-017 is
owner-reported PASS / monitoring; BUG-009 is still OPEN. Source rollback remains
d6fb5d4 / 37da798 as described, preserving all runtime journals.

## Owner preflight — 25 Oktober 2026

Owner ran `python tools/check_portrait_v2.py` in the Windows Kivy environment
and supplied HEAD **0dc6555d299cdab19d952e92df2ae660cdc4676d**, status
**READY_FOR_MANUAL_TEST**, with the local report path. [Record](owner-preflight-2026-10-25.json).
The JSON file contents/device metadata and completed P5 form have not been
submitted; no physical/provider items become PASS.

Sandbox is created on account registration and can be used for test transactions
while production approval is pending. Select Sandbox in the Midtrans dashboard
then Settings → Access Keys for Merchant ID and the Sandbox Server Key;
[official account/environment guide](https://docs.midtrans.com/docs/midtrans-account)
and [authorization guide](https://docs.midtrans.com/docs/api-authorization-headers)
were checked on 25 October. Actual account/payment-method availability still
depends on Midtrans. If Sandbox access is unavailable, leave merchant items
NOT_RUN and complete local GUI tests; do not invent keys or weaken validation.

GUI v2 is the intended future primary branch, with repository operations still
separate: [promotion plan](../../gui-v2-promotion-plan.md).
