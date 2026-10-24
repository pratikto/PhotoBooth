# P5 readiness and final Windows acceptance

Owner approved P4b Sandbox followed by P5 preparation, with manual tests at the
end. This package prepares regression/metadata/acceptance; **P5 commercial
certification is pending** actual Windows hardware, merchant Sandbox, privacy,
Drive retention and explicit release approval. No production activation or merge.

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
screenshots. Only one complete final regression is planned after source changes;
focused checks cover earlier stages. Offline QR screenshots are marked fixtures.

Checkpoints on `feature/portrait-kiosk-v2-next`:

| Source | Purpose |
| --- | --- |
| d6fb5d4 | Accepted visual/local-flow baseline before Sandbox imports |
| 37da798 | Unchanged QRIS service/client + 124 original tests |
| ce603c2 | Native Sandbox handoff, 195 focused PASS, reviewed two-size views |

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
