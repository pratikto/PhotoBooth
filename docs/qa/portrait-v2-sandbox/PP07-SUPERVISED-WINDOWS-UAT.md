# PP-07 supervised Windows owner test — photo-before-QRIS kiosk

> **2 November update:** Exact-source automated [CI simulation evidence](PP07-AUTOMATED-SIMULATION-2026-11-02.md) is not owner UAT. New preflight checks the **actual active interpreter** for Kivy/QRIS test-client/QR/rendering dependencies and rejects `PHOTOBOOTH_V2_CHECKOUT_SANDBOX=1`, `PHOTOBOOTH_V2_CHECKOUT_MOCK=1`, `PHOTOBOOTH_V2_PRINT=1` or `PHOTOBOOTH_V2_DRIVE=1`. Set these four flags to `0` before preflight and only run the launcher on a fresh private root. In default mock Drive mode, the results QR must visibly say `QR DEMO • BUKAN LINK DOWNLOAD` and is **not** a real customer download link. The separately opted-in real test Drive route must visibly identify test Drive while payment remains simulated. These display/preflight changes have distinct pending CI at `67dc3eb5` and may not be cited as PASS from older CI.

> **2 November preflight addition:** Before PILOT-01, on the checked-out authorized branch run `python -m unittest tests.test_post_preview_pilot_preflight -v` and `python tools/check_post_preview_pilot.py` using the **same Python interpreter that will launch Kivy** (your pre-existing `.venv-kivy` is acceptable; don't recreate it). Static `READY_FOR_SUPERVISED_SYNTHETIC_PILOT` is not an owner PASS and does not test live devices. If code, branch, or dependency status is BLOCKED, stop before acquiring the camera; preserve all previous test roots. See [reconciled Windows guide](POST-PREVIEW-QRIS-WINDOWS-PILOT.md). The new unit tests and the 26 owner steps are distinct evidence tracks; do not promote test creation to test execution.

**Scope:** `feature/post-preview-qris-checkout`, versioned post-preview checkout, **synthetic payment only**. This is an owner execution worksheet and **all rows below start NOT_RUN**. GitHub CI on fake camera/payment/printer/cloud cannot establish physical PASS. The legacy paid-before-photo app remains separate.

## 1. Safety and preparation (do not skip)

Use your own webcam, POS80 and approved test Google Drive account. No actual Midtrans charge or refund is possible from this launcher; the `SIMULASI PAID • TANPA TRANSFER` control marks **the in-process mock provider** as settled.

Before each trial:
- Check out the authorized branch; never switch/merge to `master` for these tests.
- Preserve old folders and old tests. Always choose a fresh, previously unoccupied `--private-root`. The launcher **refuses a reused nonempty path** to prevent cross-customer session/ledger overwrites.
- Use only your own synthetic selfie/test images. Real Drive uploads may be publicly viewable by anyone with the folder link.
- Do not send raw Recovery Ticket, CCP, merchant credentials, user photos or URL tokens in bug reports. Blur/mask QR and sensitive content.
- Keep a manual stop switch at the operating system level. If paper delivery is UNCERTAIN, never blindly repeat print or re-run the same original root.

### 1.1 Clean, no-paper, no-cloud smoke

From the repository root in Windows PowerShell:

```powershell
git switch feature/post-preview-qris-checkout
git pull --ff-only origin feature/post-preview-qris-checkout
git rev-parse --short HEAD

py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-post-preview.txt -r requirements-qris.txt
$env:PHOTOBOOTH_V2_CHECKOUT_SANDBOX = '0'
$env:PHOTOBOOTH_V2_CHECKOUT_MOCK = '0'
$env:PHOTOBOOTH_V2_PRINT = '0'
$env:PHOTOBOOTH_V2_DRIVE = '0'
.\.venv\Scripts\python.exe tools/run_post_preview_checkout_pilot.py --synthetic-payment-only --private-root work\postpay-owner-trial-001
```

For another trial change the suffix to `-002` etc. **Do not delete prior data**.

### 1.2 Optional POS80 physical paper

Only after the no-paper smoke PASS, configure **your own device** via existing `PHOTOBOOTH_PRINTER_LAN_HOST`, `PHOTOBOOTH_PRINTER_WINDOWS_NAME`, or supported USB environment settings. Then append both flags:

```powershell
--enable-real-printer --accept-real-paper
```

This sends one private ticket and purchased photo strips to the actual printer. The original copy count is applied per design. A returned `SUBMITTED` means transport submitted data, **not** paper physically emerged. Inspect paper/cuts directly. If uncertain, **stop**; do not reprint automatically.

### 1.3 Optional real Google Drive

Use a **nonproduction test Drive account or explicitly authorized booth**; this writes files and may expose photos to anyone holding the shared folder URL. Set the existing deployed Apps Script URL and upload token through the owner's secure Windows environment, then append **both** `--enable-real-drive --accept-public-test-upload`. The backend must see a genuinely shared individual folder and enough of the 25 READY slot pool before synthetic checkout admission. Do not place tokens into Git commits or support logs.

Combine the real Drive and real POS80 flags only after each has been tested independently. The physically observed customer link must load without requesting the customer's personal Google Drive login. A verified folder URL alone does **not** prove all JPEG/PNG files have uploaded; check verified file counts.

## 2. Owner smoke/UAT matrix

| ID | Scenario | Expected result | Initial result |
| --- | --- | --- | --- |
| PILOT-01 | Start without `--synthetic-payment-only` | Launcher refuses; no real QRIS charge | NOT_RUN |
| PILOT-02 | Use old/nonempty/symlink private root | Launcher refuses without resetting previous data | NOT_RUN |
| PILOT-03 | Ads -> Mulai Foto -> tutorial -> templates | Correct portrait UI and responsive gestures | NOT_RUN |
| PILOT-04 | Select 2 different designs with 2/1 copies | 2 independent photo sessions; one combined total | NOT_RUN |
| PILOT-05 | Take 3 photos/template with real webcam | Preview mirrors; saved original does not mirror unexpectedly | NOT_RUN |
| PILOT-06 | Use exactly 1 retake/template | Only selected frame changes; source lineage intact | NOT_RUN |
| PILOT-07 | Review all purchased designs before QRIS | All previews shown; edit/cart permitted before freeze | NOT_RUN |
| PILOT-08 | Freeze checkout and display CCP | Original private QR/code visible; no raw proof in logs | NOT_RUN |
| PILOT-09 | Begin synthetic QRIS and press SIMULASI PAID | Exactly 1 mock payment; original photos remain private | NOT_RUN |
| PILOT-10 | First PAID → Recovery Ticket | Original QR/code genuinely visible 30s, independent printer | NOT_RUN |
| PILOT-11 | NEXT at 5 seconds vs full countdown | Exactly one dismissal; no token redisplay/reissue | NOT_RUN |
| PILOT-12 | Ticket/receipt print with POS80 option | At most one ticket send; actual paper manually inspected | NOT_RUN |
| PILOT-13 | Mock paid photo result | Correct 3 photos + original folder QR; no second shutter | NOT_RUN |
| PILOT-14 | Purchased strip with POS80 option | One batch per design; selected copy count and QR correct | NOT_RUN |
| PILOT-15 | Virtual Drive fixture | Clearly synthetic URL, never represented as downloadable | NOT_RUN |
| PILOT-16 | Real Drive opt-in and public viewer | Correct original folder, verified link and upload progress | NOT_RUN |
| PILOT-17 | Disconnect printer/network in test | Uncertain output is held, no blind automatic print replay | NOT_RUN |
| PILOT-18 | A privacy-locks/abandons; Ads shown | Prior photos/QR gone, old PAID/OWED remains | NOT_RUN |
| PILOT-19 | B taps Mulai Foto while old session protected | PREPARE→ACK; no new purchase until old safely released | NOT_RUN |
| PILOT-20 | A returns while B is active | WAIT/defer, no camera takeover or old media display | NOT_RUN |
| PILOT-21 | A returns with original CCP/ticket when free | Exact old paid group/media/grant restored, no new mock charge | NOT_RUN |
| PILOT-22 | Invalid/DEMO/QRIS ticket used for old recovery | Generic denial without private data/renewed ticket | NOT_RUN |
| PILOT-23 | Original PENDING/UNKNOWN payment on old visit | New checkout refused until original financial reconciliation | NOT_RUN |
| PILOT-24 | Restart process mid-print or upload | No duplicate send; old journal and original rights preserved | NOT_RUN |
| PILOT-25 | Actual Midtrans Sandbox paid QRIS | **BLOCKED**: not provided by this synthetic-payment-only launcher | BLOCKED |
| PILOT-26 | Actual merchant refund/duplicate-charge resolution | **BLOCKED**: account-specific refund provider capability unverified | BLOCKED |

**UAT boundary:** PILOT-01–24 require owner execution/observations. The 112 canonical PP acceptance IDs remain NOT_RUN unless independently executed and referenced to the exact source SHA. Real Midtrans Sandbox, actual merchant payment, automatic refund and production release are explicitly **not authorized** by this worksheet.

## 3. Capture evidence without private tokens

For each test record: test ID, local date/time, laptop OS, commit SHA, webcam/printer mode, simulated vs actual Drive, PASS/FAIL/BLOCKED, redacted screenshot or printer output description, exact failure step and whether a prior transaction exists. Never include raw recovery proof or full Midtrans secret. For paper issues record `SUBMITTED` vs physically printed separately. For Drive record folder-link opening and verified file counts separately.

A FAIL caused by duplicate provider charge, cross-customer photo leak, wrong original folder, invalid printer replay, or ambiguous worker fence is a **stop condition**: do not rerun an old `--private-root`; preserve it for diagnosis and use a separate new root after a software fix.

## 4. Engineering exit gates

- [ ] All source-pinned GitHub CI jobs SUCCESS (Linux, Windows, native UI).
- [ ] No rollback of AR/UAH/legacy paid-before-photo safety regressions.
- [ ] Owner Windows synthetic UAT PILOT-01–24 documented with truthful result.
- [ ] Separate real POS80 80mm-paper evidence, including uncertain output inspection.
- [ ] Separate real Drive public folder/readiness/upload/retention acceptance.
- [ ] Original B busy WAIT and A original claim verified on physical GUI.
- [ ] Only then can real Midtrans Sandbox admission be considered for a separately gated engineering milestone.
- [ ] Full PP-001–112 acceptance and AR-13 operational/merchant readiness are **not** presumed from this pilot.

See [pilot startup guide](POST-PREVIEW-QRIS-WINDOWS-PILOT.md) and [implementation checkpoint](POST-PREVIEW-QRIS-IMPLEMENTATION-CHECKPOINT.md).
