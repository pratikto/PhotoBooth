# Meong Photobooth — GUI v2

Portrait Kivy photobooth with advertising, a tutorial, twelve original thermal
strip designs, three photos per selected design, one retake per design, local
results, and the original Meong Fly game in DEMO mode.

**Development branch: `feature/portrait-kiosk-v2-next`.** GUI v2 is the owner's
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
| QRIS Sandbox | Install `requirements-qris.txt`, then `python tools/run_portrait_v2_sandbox.py` | Isolated test merchant/backend; official simulator; no game promotion; printer/Drive forced off |

Close the app and clear the MOCK flag after testing:
`Remove-Item Env:PHOTOBOOTH_V2_CHECKOUT_MOCK -ErrorAction SilentlyContinue`.

The Sandbox launcher requests Merchant ID and a hidden Sandbox Server Key
locally. Never send keys to chat or commit them. Use the official simulator
shown in the terminal. [Sandbox instructions and recovery](docs/qa/portrait-v2-sandbox/README.md).
Production account approval and Sandbox access are separate; the
[official account guide](https://docs.midtrans.com/docs/midtrans-account)
describes the environments. Actual merchant acceptance remains pending.

## Automatic print and background Drive

Use the existing v1 printer/Drive configuration and launch the explicit delivery
profile in your Windows Kivy environment:

```powershell
python tools/run_portrait_v2.py --print --drive
```

After approving the three photos, each design automatically sends one batch
with its selected copy count. Drive uploads/retries in the background and
resumes its current-profile queues on startup without a new photo visit. The result shows a
large download QR after file verification. Uncertain prints are held for
inspection and never replayed automatically. Paper/phone/cloud acceptance is
separate from source tests; BUG-009 retention remains open.

New v2 photo areas are mirrored consistently in review, result, paper and the
digital strip. Template/text/logo/QR stay normal; original camera JPEGs retain
their original orientation/resolution. Existing saved strips are not rewritten.
[Mirror scope and acceptance](docs/qa/portrait-v2-mirrored-output/README.md).

For print-only testing use `--print`; for deliberate manual printing add
`--manual-print`. Default launch without operator opt-ins stays local. The
dedicated merchant Sandbox trial keeps both transports off.
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

