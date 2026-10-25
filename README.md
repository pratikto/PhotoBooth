# Meong Photobooth — GUI v2

Portrait Kivy photobooth with advertising, a tutorial, twelve original thermal
strip designs, three photos per selected design, one retake per design, local
results, and the original Meong Fly game in DEMO mode.

**Development branch: `feature/portrait-kiosk-v2-next`.** GUI v2 is the owner's
intended future primary branch. GitHub's default remains `master`;
`python main.py` still launches v1. See the [promotion plan](docs/gui-v2-promotion-plan.md).

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
Quantity zero deselects a design; 1–9 selects identical paper copies from one
three-photo session. A zero-copy digital-only purchase is not implemented.
Printer and Drive require operator opt-in; the default output stays local.

## Select a test mode

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

Latest functional source: **`ebb53fd`**; **785 local tests PASS, zero skips**.
[Matching-source CI 40189694738](https://github.com/pratikto/PhotoBooth/actions/runs/40189694738)
succeeded in all three jobs. Its native report has one optional palm-model-assets
skip, covered by the local run. The evidence package verifies 119 PNGs;
required views were reviewed. These are recorded source/fixture results.
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
The [documentation reconciliation](docs/qa/documentation-consistency-2026-10-25.md)
records the cross-check and corrections.

Reuse working services, UI, renderers and assets. The latest lab dithering,
AI Background Studio, device selection and WhatsApp work on reference branches
are not automatically part of v2. Production QRIS, trusted QRIS game promotion,
real receipt/POS scanning, deployment, merge and release are not enabled by this
source checkpoint. [v1.0.0](docs/releases/v1.0.0.md) remains the immutable v1 source release.
