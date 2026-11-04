# Meong Photobooth — GUI v2

> **5 November full simulation campaign IN PROGRESS:** [phase 1 evidence and exact next step](docs/qa/portrait-v2-sandbox/PP07-END-TO-END-SIMULATION-2026-11-05.md): phase 1 51 PASS; BUG-041 DEMO/gallery price mismatch repaired with N27 plus 16 existing checks PASS. Full all-opt-in simulation and matching-source CI still pending; owner UAT remains deferred.

> [Latest engineering continuation — 5 November: atomic original-proof admission, executed local regression and independent readiness blockers.](docs/qa/portrait-v2-sandbox/PP07-CONTINUATION-2026-11-05.md)

> **Current post-preview continuation — 4 November 2026:** Work stays on existing `feature/post-preview-qris-checkout`. Start with the [current device guide](docs/qa/portrait-v2-sandbox/POST-PREVIEW-DEVICE-TEST-START-HERE.md), [source-specific evidence and known limits](docs/qa/portrait-v2-sandbox/PP07-DEVICE-READINESS-2026-11-04.md), and [112-case / AR traceability](docs/qa/portrait-v2-sandbox/PP07-SOFTWARE-TRACEABILITY-2026-11-04.md). The later implementation and evidence record takes precedence over older status snapshots below; approved policy and dated history remain preserved. The owner pilot uses synthetic payment. Actual merchant Sandbox, protected cross-process recovery, physical acceptance and production are separate gates. No prior test root, uncertain print or PAID/OWED may be reset to bypass them.

> **Expanded customer-journey simulation (2 November 2026):** Beyond the earlier small P0 suite, [20 connected end-to-end synthetic test scenarios J01–J20](docs/qa/portrait-v2-sandbox/PP07-BROAD-SIMULATION-MATRIX-2026-11-02.md) now exercise all 12 templates, 36 captures, 3-design 2+1+3 print batches, provider outages and multiple late settlements, Drive tamper/outages, printer cross-dispatcher quarantine, A→B→A claim and 12 protected visits. First CI exposed two test-fixture assertion issues, corrected in `bd70593f`; matching-source [CI #41407613830](https://github.com/pratikto/PhotoBooth/actions/runs/41407613830) must be checked before declaring any new scenarios PASS. Physical/merchant/refund gates remain open.

> **Latest verified synthetic test snapshot (2 November 2026):** [CI #41404106134](https://github.com/pratikto/PhotoBooth/actions/runs/41404106134) at code `0548bc89`: **494 Windows + 494 Ubuntu + 54 native Kivy = 1,042 test executions PASS**, zero failures/errors/skips, 3/3 jobs SUCCESS. Covers QR3, uncertain paper, late original QR1/QR2 duplicate settlement and persistent SENDING model; **no real payment, paper, Drive, refund or physical acceptance**. [Full P0 fault report](docs/qa/portrait-v2-sandbox/PP07-ADVERSARIAL-GUI-FAULTS-2026-11-02.md).

> **PP-07 P0 checkout/print fault simulations (2 November 2026):** [Source-pinned adversarial GUI and journal test record](docs/qa/portrait-v2-sandbox/PP07-ADVERSARIAL-GUI-FAULTS-2026-11-02.md) covers QR1→QR3 terminal expiry/no QR4, partial/uncertain print quarantine, late old-QR1 settlement while QR2 is live, and a durable paid-strip SENDING crash-seam restart model. See that record for source-matched CI outcomes; none are proof of real Midtrans payment, POS80 paper, cloud upload or owner physical acceptance.

> **Latest automated pilot simulation — 2 November 2026:** Exact-source [GitHub Actions #41393795509](https://github.com/pratikto/PhotoBooth/actions/runs/41393795509) at `67dc3eb5` executed **493 Windows + 493 Ubuntu + 51 native Kivy = 1,037 successful test executions** (0 failures/errors/skips, 3/3 jobs SUCCESS).
> **Current automated pilot-simulation evidence (2 November 2026):** [PP-07 executed source-pinned GitHub Actions results](docs/qa/portrait-v2-sandbox/PP07-AUTOMATED-SIMULATION-2026-11-02.md) separate native Kivy/Ubuntu/Windows CI evidence from the 26 owner physical checks and the 112-case acceptance matrix. Do not infer live QRIS, paper, real Drive or production approval from the synthetic CI.

> **CURRENT IMPLEMENTATION STATUS — 2 November 2026 (supersedes historical DESIGN ONLY labels below):** Coding was explicitly authorized on 1 November and is underway **on this existing branch only**. PP-01..PP-05 have isolated synthetic implementations; PP-06 includes original protected Advertising, machine-fenced mock-only A/B admission and proof-gated original claimant return. PP-06R1 is a **pure, nonbinding refund assessment only** and cannot issue refunds. PP-07 has an opt-in Windows **synthetic-payment-only** pilot with optional explicitly authorized real POS80 and test Drive, plus a 26-case owner worksheet. Recent Windows CI surfaced a **test-only canonical path expectation** requiring exact-source rerun. Do **not** infer actual Midtrans Sandbox acceptance, refund availability, physical paper/Drive signoff, all 112 PP acceptance PASS or production readiness. See [implementation checkpoint](docs/qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-IMPLEMENTATION-CHECKPOINT.md), [Windows pilot](docs/qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-WINDOWS-PILOT.md) and [owner UAT](docs/qa/portrait-v2-sandbox/PP07-SUPERVISED-WINDOWS-UAT.md). Earlier documentation-only paragraphs below describe their historical dates and are **not current source status**.

> **LATEST owner-approved policy on `feature/post-preview-qris-checkout` (1 November 2026, DESIGN ONLY):** **All** previously agreed post-preview capture/retake/template/payment/Drive/CCP/Recovery Ticket/isolation/privacy/Meong Fly decisions remain binding. **The original Recovery Ticket must ALWAYS appear on-screen for 30 genuinely visible seconds + NEXT while the SAME original ticket is dispatched to the printer ONCE concurrently**, even on printer success. **Refund-first** is now the owner-approved *future* handling for independently verified irrecoverable **PAID merchant-service failures** (MVP preference: original FULL refund) and unambiguously excess duplicate-settled QRIS charges (refund excess only), but **only if merchant-specific Midtrans refund capability, worker safety, idempotency and legal controls are verified**. **Customer loss of a genuinely offered CCP/Recovery Ticket alone => NO_AUTO_REFUND_PROOF_LOST, no tokenless old-photo access**; Meong's failure to offer proof or separately deliver paid photos remains PAID/OWED/remedy and is NOT called customer negligence. Older unconditional NO_AUTO_REFUND and conditional-screen-only prose below is historical/current **legacy paid-first** scope, not new-order authority. **112 new PP tests NOT_RUN; refund API not proven active; no code/refund/production change.**
>
> **Canonical read order:** [Full no-loss owner decision ledger](docs/qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-COMPLETE-DECISION-LEDGER.md) · [refund and proof-loss RF-D01..26](docs/qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-REFUND-AND-LOST-PROOF-POLICY.md) · [new operational escalation](docs/qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-OPERATOR-AND-REFUND-ESCALATION.md) · [master PP flow](docs/qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-OWNER-APPROVED.md) · [state security](docs/qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md) · [PP-001..112 NOT_RUN QA](docs/qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md) · [future Codex handover](docs/qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-CODEX-HANDOVER.md).


## New post-preview checkout branch — approved DESIGN, not running code (1 November 2026)

The source instructions and test launchers below still describe the **current legacy paid-before-camera flow**, and their published CI evidence has not been rerun for the new flow. Dedicated branch **`feature/post-preview-qris-checkout`** now carries an owner-approved **documentation-only target**: per design 3 photos + at most 1 retake -> all previews -> frozen one-cart QRIS -> original post-PAID Recovery Ticket (**mandatory 30s onscreen QR/full code + ONE concurrent same-ticket paper print**) -> photo printing only after verified customer Drive URL. Pre-PAID private Checkout Claim Proof, scoped encrypted credential escrow, live-only QR expiry renewal, late-PAID private claim and safe isolation are part of this future version; 84 new PP tests **NOT_RUN**. Do not mistake this README's legacy Sandbox camera/Drive OFF state for shipped new behavior. **On this PP branch follow the [new staged Codex plan](docs/qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-CODEX-HANDOVER.md) only when implementation is separately authorized**, with all AR/UAH safety and legacy PAID recovery preserved. Master, parent branch and source unchanged.

[24 decisions + corrected flowcharts](docs/qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-OWNER-APPROVED.md) · [state/security](docs/qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md) · [84 acceptance cases](docs/qa/portrait-v2-sandbox/POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md).


31 October — Sandbox prints one recovery receipt after verified PAID, enters
camera directly, then prints approved photo strips. Drive remains OFF.
[Current print scope and verification](docs/qa/portrait-v2-sandbox/BUG027-PAID-TO-PHOTO.md).

Sandbox: [QR kedaluwarsa otomatis diganti; kedaluwarsa ketiga kembali iklan, tiket setelah bayar](docs/qa/portrait-v2-sandbox/UX07-LAPTOP-CHECK.md#jika-qr-pembayaran-kedaluwarsa-saat-l02).

Sandbox lama tanpa tiket pemulihan: [langkah arsip uji dengan PIN lokal](docs/qa/portrait-v2-sandbox/BUG025-LEGACY-NO-TICKET.md#final-verified-result--owner-retest-next). Pesanan/foto/hak lama tetap disimpan. Profil cetak Sandbox terbaru mengikuti BUG-027 di bawah.

[Interactive laptop checklist — 44 guided steps, expected results, notes and copy report](docs/qa/portrait-v2-sandbox/windows-checklist-ux07.html) (open the HTML locally).

Latest owner check: [UX-07 lifecycle laptop checklist](docs/qa/portrait-v2-sandbox/UX07-LAPTOP-CHECK.md). Offline fixture checks verified; actual devices/merchant and commercial acceptance remain separate.

Portrait Kivy photobooth with advertising, a tutorial, twelve original thermal
strip designs, three photos per selected design, one retake per design, local
results, and the original Meong Fly game in DEMO mode.

**Original implemented GUI v2 development branch: `feature/portrait-kiosk-v2-next`. New design-only branch: `feature/post-preview-qris-checkout` (no flow code yet).** GUI v2 is the owner's
intended future primary branch. GitHub's default remains `master`;
`python main.py` still launches v1. See the [promotion plan](docs/gui-v2-promotion-plan.md).

[Checklist gabungan: semua gate yang belum teruji (49 item + Submit)](docs/qa/portrait-v2-pending-acceptance/windows-checklist.html) ·
[Petunjuk dan batas pengujian](docs/qa/portrait-v2-pending-acceptance/README.md).

## Run GUI v2 on Windows

Use the existing checkout and Kivy environment. Preserve local changes before
switching or pulling; do not recreate the project or overwrite configuration.

```powershell
git switch feature/portrait-kiosk-v2-next
git pull --ff-only origin feature/portrait-kiosk-v2-next
.\.venv-kivy\Scripts\Activate.ps1
python tools/run_portrait_v2.py
```

First installation requires Python 3.11+ (recorded QA uses Python 3.12) and
`python -m pip install -r requirements.txt` in a virtual environment.

Local flow: **advertising → MULAI FOTO → tutorial → templates/copies → UJI FOTO →
consent → three photos → review/retake → result → advertising**.
There is no separate CARA PAKAI button on idle: MULAI FOTO and invitation
AYO FOTO already open the required tutorial for a new visit.
Quantity zero deselects a design; 1–9 selects identical paper copies from one
three-photo session. A zero-copy digital-only purchase is not implemented.
Printer and Drive require operator opt-in; the default output stays local.

## Select a test mode

**Platform clarification (27 October): Windows for development, Ubuntu mini PC
for deployment.** The ordinary launcher now prevents duplicate v2 launcher
processes per checkout. Optional watchdog startup reviews local journals before
opening devices; pending/uncertain work is held for operator review. Generate an
Ubuntu systemd user service from either platform with explicit Ubuntu paths;
generation never installs/enables it. Automatic restart remains off.
[Windows/Ubuntu commands, setup, recovery and rollback](docs/qa/portrait-v2-recovery/README.md).

| Mode | Launch | Boundary |
| --- | --- | --- |
| Local/default | `python tools/run_portrait_v2.py` | Explicit photo-test consent; production payments and receipt scanner disabled |
| Local MOCK checkout | Set `$env:PHOTOBOOTH_V2_CHECKOUT_MOCK='1'`, then use the ordinary launcher | Nonpayable QR, simulated confirmation and one-use game discount |
| QRIS Sandbox | Install `requirements-qris.txt`, then `python tools/run_portrait_v2_sandbox.py` | Isolated test merchant/backend; official simulator; no game promotion; one recovery receipt after verified PAID and approved photo strips print automatically; Drive OFF |

Close the app and clear the MOCK flag after testing:
`Remove-Item Env:PHOTOBOOTH_V2_CHECKOUT_MOCK -ErrorAction SilentlyContinue`.

The Sandbox launcher can read saved Merchant ID and Server Key from the ignored
`photobooth/local_settings.py`; add the Sandbox-specific fields without replacing
existing Drive values. Missing values retain local/hidden prompts.
[Saved-settings setup and precedence](docs/qa/portrait-v2-sandbox/LOCAL-SETTINGS.md).
Never send keys to chat or commit them. Use the official simulator shown in the
terminal. [Sandbox instructions and recovery](docs/qa/portrait-v2-sandbox/README.md).
Copy the Server Key exactly from the Sandbox dashboard: both `SB-Mid-server-`
and `Mid-server-` formats are accepted. The prefix does not select the environment;
provider requests remain fixed to Sandbox. [Key-format correction](docs/qa/portrait-v2-sandbox/KEY-FORMAT.md).
The v2 payment QR now reuses the centered Drive QR logo renderer with exact
decoded-payload checks. It retains the original image if branding cannot be
verified. [Logo scope and pixel evidence](docs/qa/portrait-v2-sandbox/QR-LOGO.md).
Production account approval and Sandbox access are separate; the
[official account guide](https://docs.midtrans.com/docs/midtrans-account)
describes the environments. Actual merchant acceptance remains pending.

On the QRIS Sandbox payment page, press **SALIN LINK QRIS**, then paste the
copied link into the [Midtrans QRIS simulator](https://simulator.sandbox.midtrans.com/v2/qris/index).
The button copies the current verified QR image URL; confirmation still comes
from the backend's status check. [Usage and checks](docs/qa/portrait-v2-sandbox/COPY-LINK.md).

## Automatic print and background Drive

27 October: customer uploads now take priority over chunk-yielding content and
bounded incremental reserve maintenance. Background snapshots no longer lock
result controls/footer. Latest owner correction: customer sessions upload FIFO,
with old retries/maintenance held while customer work remains. A verified
assigned-folder QR appears before upload completion, with a 30-minute check-back
suggestion. [Current behavior and evidence](docs/qa/drive-delivery-performance/CUSTOMER-PRIORITY.md).
[Timing, v1 comparison, actual test evidence and Windows/update instructions](docs/qa/drive-delivery-performance/README.md).


Use the existing v1 printer/Drive configuration and launch the explicit delivery
profile in your Windows Kivy environment:

```powershell
python tools/run_portrait_v2.py --print --drive
```

After approving the three photos, each design automatically sends one batch
with its selected copy count. Drive uploads/retries in the background and
resumes its current-profile queues on startup without a new photo visit. The result shows a
large download QR once the assigned folder is verified; uploads can still be pending. Uncertain prints are held for
inspection and never replayed automatically. Paper/phone/cloud acceptance is
separate from source tests; BUG-009 retention remains open.

New v2 photo areas are mirrored consistently in review, result, paper and the
digital strip. Template/text/logo/QR stay normal; original camera JPEGs retain
their original orientation/resolution. Existing saved strips are not rewritten.
[Mirror scope and acceptance](docs/qa/portrait-v2-mirrored-output/README.md).

For print-only testing use `--print`; for deliberate manual printing add
`--manual-print`. Default launch without operator opt-ins stays local. The
dedicated merchant Sandbox trial now prints one recovery receipt after verified PAID and
approved photo strips automatically (31 October BUG-027 scope); Drive stays OFF.
Prepare the existing printer configuration and paper before running that profile.
[Runbook, evidence and rollback](docs/qa/portrait-v2-print-drive/README.md) ·
[earlier eleven-item delivery form](docs/qa/portrait-v2-print-drive/windows-checklist.html).

The ordinary launcher now uses per-booth storage: 25 empty local reserves,
`Photobooth/PB001/Photo/00000001/{raw,bw,color}` in Drive, offline photo/print with deferred Drive binding and
verified global/local asset caches. Code.gs needs a manual update/setup and a
new version of the existing deployment; the cloud environment did not deploy it.
[Current Drive/QR repair](docs/qa/drive-photo-layout/README.md) · [Earlier setup and rollback](docs/qa/feat-004-storage/SETUP.md) ·
[12-item Submit checklist](docs/qa/feat-004-storage/windows-checklist.html).

If Drive is held by retention setup, run `python tools/check_drive_retention.py`.
It uses the existing v1 configuration and requests status only, saving a redacted
JSON without activation/upload/deletion. [BUG-009 activation guide and Submit
form](docs/qa/bug-009-retention/README.md) distinguish setup, missing trigger,
old deployment and access errors. Actual cloud expiry remains unverified.

## Operator Device Health

At idle advertising, press **F12** or hold the Meong header for **1.5 seconds**.
The original v1 panel/backend/worker are reused through small v2 adapters.
Six read-only observations and OS candidate inventory can be refreshed without
opening another camera or sending print bytes. Access is also available in
Sandbox RECOVERY and cannot interrupt active photo/game/payment work.

**SIMPAN LAPORAN LOKAL** saves redacted metadata to `data/diagnostics`.
READY describes a limited observation, not physical printer/provider/Drive
acceptance. **PILIH DEVICE** is disabled.
[Evidence and limits](docs/qa/portrait-v2-operator-health/README.md) ·
[eight-item operator form](docs/qa/portrait-v2-operator-health/windows-checklist.html).

**Operator retest follow-up:** the owner checked 8/8 but also reported an app
hang after pressing all health buttons rapidly. BUG-018 source `ebb53fd` adds
fresh-press/one-release admission and drops rapid duplicate commands/SFX; TUTUP
remains usable while a probe/report runs. The later owner retest reports **4/4
PASS, no issues**: BUG-018 is monitoring. Tested HEAD/device fields are unknown;
this does not certify exact source or external P5 gates.
[Four-item retest with Submit](docs/qa/portrait-v2-health-clicks/windows-checklist.html) ·
[reproduction and evidence](docs/qa/portrait-v2-health-clicks/README.md).

## Current checkpoint and remaining acceptance

**27 October FEAT-009 checkpoint:** recovery review, launch ownership and Ubuntu
startup generation are in source; final local regression runs **869 tests:
866 PASS, 3 optional palm-assets SKIP, zero failures/errors**. Windows development
and Ubuntu deployment are distinct acceptance targets. Documentation-first and
documentation-after-code are the primary rules in AGENTS/protocol.
[Current startup/recovery proof and manual checks](docs/qa/portrait-v2-recovery/README.md).

Earlier mirror source: **`fc26e3d`**; **808 local Python tests PASS, zero skips**.
V2 review/result/printed/digital photo areas mirror consistently; raw JPEGs and
template/text/QR stay original. Native captures were reviewed at 800×1280 and
452×900. [Current mirror proof and five-item form](docs/qa/portrait-v2-mirrored-output/README.md).
[Matching-source CI 40263151709](https://github.com/pratikto/PhotoBooth/actions/runs/40263151709)
succeeded in all three jobs; its optional model-assets skip is covered locally.

Earlier source **`887ba39`** has **807 local Python tests PASS, zero skips**,
plus **19 actual-Code.gs VM tests PASS**. BUG-009 now has corrected real-CLOCK
activation and a safe diagnostic/guide; Google-account activation/deletion
remains unverified. [Current proof](docs/qa/bug-009-retention/README.md).
[Matching-source CI 40255716011](https://github.com/pratikto/PhotoBooth/actions/runs/40255716011)
succeeded in all three jobs; one optional native model-assets skip is covered locally.

Earlier source `20453fe` has 800 local PASS. The entry refinement removes the separate CARA PAKAI button while
preserving the required tutorial. Twelve clean-source PNGs were verified;
idle/invitation/tutorial were reviewed at 800×1280 and 452×900.
[Current checks/screenshots and Windows spot checks](docs/qa/portrait-v2-photo-entry/README.md).
[Matching-source CI 40248962384](https://github.com/pratikto/PhotoBooth/actions/runs/40248962384)
succeeded in all three jobs; its optional palm-assets skip is covered locally.
Earlier Print/Drive source `266b2c8` has its own
[three-job successful CI](https://github.com/pratikto/PhotoBooth/actions/runs/40208966127)
and 133 verified PNGs. These are recorded source/fixture results.
[Current status](docs/FEATURE_STATUS.md) · [test ledger](docs/test_checklist.md).

P5 is **ready for acceptance**, with merchant Sandbox, current Windows integration,
physical printing, Drive/download/30-day retention (BUG-009), privacy and release
signoff still awaiting complete evidence. Existing owner reports remain valid
within their recorded limits. The preflight at HEAD `0dc6555` reported
READY_FOR_MANUAL_TEST; it did not certify hardware or a provider.

```powershell
python tools/check_portrait_v2.py
Start-Process docs/qa/portrait-v2-p5/windows-checklist.html
```

Import `data/diagnostics/windows-readiness.json`, complete actual checks, then
Submit to prepare a report for chat. Import does not pass tests or send a report.
The eight-item operator form is separate and adds no repeat photo/game cycle gate.

## Documentation

Start with the [documentation index](docs/README.md),
[roadmap](docs/portrait-kiosk-v2.md), [technical design](docs/portrait-kiosk-v2-technical-design.md),
[handover](docs/DEVELOPMENT_HANDOVER.md), [bug register](docs/bug_tracker.md),
[branch reference audit](docs/gui-v2-branch-audit.md), and [working rules](AGENTS.md).
The [storage/global-content target](docs/photobooth-storage-layout.md) records
the requested per-booth/25-reserve/Photo/raw-color-bw/offline-cache structure and
current implementation gaps. The `old` archive is excluded and untouched.
The [documentation reconciliation](docs/qa/documentation-consistency-2026-10-25.md)
records the cross-check and corrections.

Reuse working services, UI, renderers and assets. The latest lab dithering,
AI Background Studio, device selection and WhatsApp work on reference branches
are not automatically part of v2. Production QRIS, trusted QRIS game promotion,
real receipt/POS scanning, deployment, merge and release are not enabled by this
source checkpoint. [v1.0.0](docs/releases/v1.0.0.md) remains the immutable v1 source release.

