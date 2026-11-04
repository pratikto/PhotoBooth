# Supervised Windows pilot — synthetic payment, webcam, optional POS80

> **Current post-preview continuation — 4 November 2026:** Work stays on existing `feature/post-preview-qris-checkout`. Start with the [current device guide](POST-PREVIEW-DEVICE-TEST-START-HERE.md), [source-specific evidence and known limits](PP07-DEVICE-READINESS-2026-11-04.md), and [112-case / AR traceability](PP07-SOFTWARE-TRACEABILITY-2026-11-04.md). The later implementation and evidence record takes precedence over older status snapshots below; approved policy and dated history remain preserved. The owner pilot uses synthetic payment. Actual merchant Sandbox, protected cross-process recovery, physical acceptance and production are separate gates. No prior test root, uncertain print or PAID/OWED may be reset to bypass them.

## 2 November 2026 — expanded test campaign before owner device work

[PP-07 broad test matrix](PP07-BROAD-SIMULATION-MATRIX-2026-11-02.md) tracks the additional **J01–J20** integrated capture/checkout/paid-delivery/abandonment cases, **N21–N24** Kivy GUI cases and **P01/P02** actual child-process exit/reopen cases. The Windows and Ubuntu backend J01–J20 suite ran 520/520 each and base Kivy 54/54 in [CI #41407613830](https://github.com/pratikto/PhotoBooth/actions/runs/41407613830); newer Kivy four native cases passed in [CI #41409614158](https://github.com/pratikto/PhotoBooth/actions/runs/41409614158). Hard-exit P cases are under separate corrected-source [CI #41409982930](https://github.com/pratikto/PhotoBooth/actions/runs/41409982930). Do not treat automated simulation as evidence of physical POS80, cloud permissions, real provider settlement or production suitability.

For physical testing keep an entirely new private root, default synthetic payment only, no-print/no-Drive first, then explicitly gated opt-in actions with redacted evidence. In particular, if one purchased strip or ticket has **SENDING/UNCERTAIN** paper outcome, do not bypass the hold or forcibly trigger the next batch; original PAID/OWED remains until safe manual classification.

## 2 November — final P0 native/Windows/Linux adversarial simulation evidence

The newest `feature/post-preview-qris-checkout` code at `0548bc89` has **matching-source [CI #41404106134](https://github.com/pratikto/PhotoBooth/actions/runs/41404106134) 3/3 SUCCESS**: **494 Windows + 494 Ubuntu + 54 native Kivy test executions PASS**, zero failures/errors/skips. The [adversarial scenario report](PP07-ADVERSARIAL-GUI-FAULTS-2026-11-02.md) details QR1→QR3 no QR4, uncertain A print blocking B, late old QR1 PAID while QR2 is pending without a second entitlement, and persisted `SENDING` restart-state no replay. A failed first native test at `7f018dba` was corrected as a test-only private QR assertion and reverified at `0548bc89`.

This verified **automated synthetic** evidence does not activate real merchant Midtrans, POS80 paper, Drive sharing/retention or refund. The owner's 26-case physical checklist remains **NOT_RUN** and real process-kill/peripheral failure recovery remains distinct. Existing safety flags, dedicated new root and dual opt-in for real test paper/cloud remain mandatory.

## 2 November — P0 test conditions added after the first 1,037 PASS baseline

Review [adversarial QR3 / uncertain print record](PP07-ADVERSARIAL-GUI-FAULTS-2026-11-02.md) before running optional real-paper checks. The newer pilot source `c86a8e64` removes customer QR4 after verified third expiry and quarantines all remaining purchased print batches when any original job is `SENDING/UNCERTAIN`. Matching-source [CI #41402925221](https://github.com/pratikto/PhotoBooth/actions/runs/41402925221) has **native 53/53 PASS** and Ubuntu **493/493 PASS**; Windows result not yet verified in this record. The existing 26-case physical worksheet remains separate from automated coverage and requires owner observation.

Do not simulate printer faults by unplugging an actively printing POS80 unless you have isolated test hardware, authorized test-only images, safe access to paper/cutter and a technician plan. An uncertain job cannot be reset/printed again merely because the next template is ready. Never reuse the same `--private-root` for a new customer or trial.

## 2 November 2026 — automated test evidence and exact owner preflight order

[Automated PP-07 simulation report](PP07-AUTOMATED-SIMULATION-2026-11-02.md): at `b071a5cc`, 490 Windows + 490 Ubuntu + 51 native Kivy tests PASS with zero failure/error/skip. A subsequent source-hardening release adds stronger dependency/profile checks and explicit synthetic Drive QR labels; its matching-source [CI run 41393795509](https://github.com/pratikto/PhotoBooth/actions/runs/41393795509) is now VERIFIED 493 Windows + 493 Ubuntu + 51 native PASS, with 3/3 jobs SUCCESS; no physical acceptance is implied.

Before running `tools/check_post_preview_pilot.py`, explicitly set **all four** legacy profile flags to `0`; otherwise preflight now correctly says BLOCKED instead of falsely claiming READY. It checks the actual interpreter for Kivy/Pillow/numpy/requests/cryptography/FastAPI/httpx/Pydantic/qrcode/OpenCV/ffpyplayer, alongside the authorized branch and required files. Reuse an existing `.venv-kivy` rather than replacing the environment.

```powershell
$env:PHOTOBOOTH_V2_CHECKOUT_SANDBOX='0'
$env:PHOTOBOOTH_V2_CHECKOUT_MOCK='0'
$env:PHOTOBOOTH_V2_PRINT='0'
$env:PHOTOBOOTH_V2_DRIVE='0'
.\.venv-kivy\Scripts\python.exe -m pip install -r requirements.txt -r requirements-post-preview.txt -r requirements-qris.txt
.\.venv-kivy\Scripts\python.exe -m unittest tests.test_post_preview_pilot_preflight tests.test_post_preview_pilot_early_root -v
.\.venv-kivy\Scripts\python.exe tools/check_post_preview_pilot.py
```

**Important UI distinction:** with default synthetic Drive, the paid output QR is a renderer fixture and the screen labels it `QR DEMO • BUKAN LINK DOWNLOAD`. It **cannot** be opened to retrieve photographs. With the separate double-consent `--enable-real-drive --accept-public-test-upload` test mode, the display instead labels the original verified test folder `DRIVE TEST • BAYAR SIMULASI`. In both cases payment remains synthetic; no real Midtrans transaction is possible in this launcher. A verified real test folder URL still does not prove photo upload completion or public-share acceptance until independently checked.

## 2 November 2026 — PP-07 reject symlinked parent test roots

The supervised, **synthetic-payment-only** pilot now rejects any symbolic link in the selected data-root's full existing ancestor chain, not merely a symlink at the final leaf. A fresh-looking directory underneath a symlink cannot redirect capture/payment/receipt journals into unrelated or previously owned filesystem data. Validation still occurs before Kivy/device runtime imports, and no occupied root is reset. See `tools/run_post_preview_checkout_pilot.py` `validate_private_root`.

`tests/test_post_preview_pilot_early_root.py` now includes a regression using a symlink parent, asserting the target is not mutated. On Windows where ordinary users cannot create symbolic links, that single test SKIPs rather than claiming PASS; the production check still applies. At the original earlier checkpoint the new commits had not yet been run. Subsequent source-pinned [CI 41404106134](https://github.com/pratikto/PhotoBooth/actions/runs/41404106134) verified Windows/Linux/native **3/3 SUCCESS**, but the owner physical tests remain **NOT_RUN**. The local runtime cannot clone GitHub because external DNS/network access is unavailable, so test execution is deferred to an authorized checkout/CI environment. Existing PP-001..112 complete acceptance remains NOT_RUN; genuine merchant QRIS/refunds and production remain unavailable.

**Next action:** run `python -m unittest tests.test_post_preview_pilot_early_root tests.test_post_preview_pilot_preflight -v`, then matching-source CI, inspect any Windows-specific failures, and continue independent PP-06/PP-07 pilot QA. Never infer real POS80 or Google Drive acceptance from synthetic tests.

## 2 November 2026 — PP-07 early fail-closed pilot-root safety

The supervised synthetic pilot `tools/run_post_preview_checkout_pilot.py` now calls the **existing strict** `validate_private_root` before Kivy, camera, launcher lease or checkout-fixture imports. Occupied prior customer folders, file paths, unsafe parent/archives and symlinks are rejected before device-runtime initialization. No directory is created or old PAID/OWED journal touched by this validation; it is not an allowance to reset any previous test. Existing dual-opt-in printer/Drive flags and the synthetic-only payment gate remain unchanged. New `tests/test_post_preview_pilot_early_root.py` tests assert both an occupied customer root and a file path fail with exit 2 and original bytes remain intact. Changes micro-pushed to **this branch only**, not master.

**Historical evidence at initial code creation:** initial remote source writes were verified but tests were NOT_RUN at that time; later matching-source [CI 41404106134](https://github.com/pratikto/PhotoBooth/actions/runs/41404106134) executed Windows/Linux/native regression with **3/3 SUCCESS**. Run `python -m unittest tests.test_post_preview_pilot_early_root tests.test_post_preview_pilot_preflight -v` in the owner's environment before physical UAT. Do not mistake this safe-startup increment for proof that camera, printer, real Drive, original customer return, refund, actual Midtrans or all PP-001..112 are accepted. Continue the 26-case [supervised owner worksheet](PP07-SUPERVISED-WINDOWS-UAT.md) after an appropriate matching-source CI pass.

## 2 November 2026 — safest continuation from your existing Windows checkout

**Do not recreate an already working virtual environment.** The earlier example below using `py -3.12 -m venv .venv` applies **only if that environment does not exist**. If you already use `.venv-kivy`, retain it and run its Python executable. First preserve any local source edits; do not overwrite them with `git switch` or `git pull`. A separate test data root is mandatory on each run, but is **not** a new code branch.

From PowerShell, after confirming `git status --short` is clean or preserving local changes:

```powershell
git branch --show-current
git status --short
git pull --ff-only origin feature/post-preview-qris-checkout
.\.venv-kivy\Scripts\python.exe -m pip install -r requirements.txt -r requirements-post-preview.txt -r requirements-qris.txt
.\.venv-kivy\Scripts\python.exe -m unittest tests.test_post_preview_pilot_preflight -v
.\.venv-kivy\Scripts\python.exe tools/check_post_preview_pilot.py
```

If using `.venv` instead, replace `.venv-kivy` in every command with `.venv`. The preflight is **read-only**: it checks branch, required project files, Python version and installed modules; it does not contact Midtrans, send paper, access Drive, open a webcam, create a session or validate a real customer experience. The report `READY_FOR_SUPERVISED_SYNTHETIC_PILOT` means only static preparation passed. If BLOCKED, correct the stated source/environment problem before launching.

For the **first no-paper/no-cloud trial**, with a **new empty root** and payment still mocked:

```powershell
$env:PHOTOBOOTH_V2_CHECKOUT_SANDBOX='0'
$env:PHOTOBOOTH_V2_CHECKOUT_MOCK='0'
$env:PHOTOBOOTH_V2_PRINT='0'
$env:PHOTOBOOTH_V2_DRIVE='0'
.\.venv-kivy\Scripts\python.exe tools/run_post_preview_checkout_pilot.py --synthetic-payment-only --private-root work\postpay-owner-trial-001
```

For each later attempt increment `-001` to `-002`, etc. **Never delete an old root** to make the new test pass: it may hold original customer recovery proof, PAID/OWED or uncertain printer state. Do not include raw CCP/ticket QR, keys or identifiable customer photographs in logs/screenshots. Real POS80 output and public test Drive uploads are opt-in with **two independent flags each**, as documented below. This launcher **never makes a real Midtrans payment or refund**.

**Evidence boundary:** The independent new preflight tests and Windows walkthrough need GitHub Actions and actual-owner execution at the containing source SHA. Added source files alone are not proof of a passing CI or device UAT. The full PP-001–112 matrix is not automatically completed by this short pilot.

This is a **local supervised pilot**, not the full PP-07 customer UAT. Use
a **new empty** storage root for **each** trial. The launcher refuses a previously used/nonempty root, including a prior customer's encrypted credentials, payment journal or print jobs. The old visit remains privacy-fenced after shutdown; NEVER delete or reset that data to restart a test.

```powershell
git switch feature/post-preview-qris-checkout
git pull --ff-only origin feature/post-preview-qris-checkout
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-post-preview.txt -r requirements-qris.txt
$env:PHOTOBOOTH_V2_CHECKOUT_SANDBOX = '0'
$env:PHOTOBOOTH_V2_CHECKOUT_MOCK = '0'
$env:PHOTOBOOTH_V2_PRINT = '0'
$env:PHOTOBOOTH_V2_DRIVE = '0'
.\.venv\Scripts\python.exe tools/run_post_preview_checkout_pilot.py --synthetic-payment-only --private-root work\postpay-pilot-001
```

Walk through Ads → gallery → selected designs and copies → three original
camera photos and one retake each → all-design preview → checkout claim proof
→ synthetic PAID button → 30 genuinely visible seconds of Recovery Ticket
(with NEXT) → original paid Drive-QR/photo-strip screen. The URL is a **fake**
synthetic Drive folder, so it **cannot** download photos; no external payment
or Drive upload occurs. Confirm that the same frozen photos appear in the
strip and that the UI never creates another provider order.

To test **actual printer paper**: set the usual explicit `PHOTOBOOTH_PRINTER_*`
settings for your owned POS80 and append **both**
`--enable-real-printer --accept-real-paper`. This activates the receipt and
purchased strips with the shared thermal printer lane. A transport SUBMITTED
status is *not* proof that paper exited; visually inspect. Never auto-retry
an UNCERTAIN print. Do not reuse a previous held customer root just to clear it;
each supervised test uses a separate fresh root and preserves previous data.

NOT tested: actual Midtrans QRIS Sandbox, Apps Script / real public Drive ACL,
upload completeness, customer proof recovery, booth auto-isolation, refund,
reboot or long-run hardware reliability. Neither this driver nor its
synthetic CI tests give approval for production payments.

## Optional real Google Drive test (synthetic payment only)

A local test can use the **existing real Apps Script storage-v2 Web App** with
real test photos while continuing to simulate QRIS. This intentionally creates
customer-like files under the selected PB001 Drive folder: do not upload other
people's photographs without permission and do not run against production
records. Use a fresh local private root and a nonproduction test Drive account
or explicitly approved test booth.

```powershell
$env:PHOTOBOOTH_WEB_APP_URL = 'https://script.google.com/macros/s/YOUR_DEPLOYMENT/exec'
$env:PHOTOBOOTH_UPLOAD_TOKEN = '<configured upload token>'
.\.venv\Scripts\python.exe tools/run_post_preview_checkout_pilot.py --synthetic-payment-only --private-root work\postpay-drive-test-001 --enable-real-drive --accept-public-test-upload
```

The booth worker first attempts to reserve 25 real READY folders. Payment
readiness is **blocked** until the existing Web App reports authenticated API,
public sharing and READY capacity; this may require waiting for asynchronous
folder creation before retrying the same original checkout. No synthetic
Drive URL is allowed in this opt-in route. When simulated PAID, the exact
original transaction is bound to a real Drive folder and photo upload
is handled through `BoothDriveWorker` with resumable checksums; view QR
is a real folder URL only after confirmed binding. A verified link **is not**
a guarantee upload has finished; inspect the UI verified-file counts.

For camera + physical paper + real Drive in the SAME supervised test, append
`--enable-real-printer --accept-real-paper` and configure the owned POS80
as described above. Actual Midtrans remains fully simulated; original
customer return-claim and refunds remain separate software readiness gates.

Important: turning on this option makes **real cloud writes**. No external
upload is performed by GitHub CI or by these documentation instructions.

## Supervised synthetic A/B handoff and original proof (new pilot)

The owner-only synthetic launcher now adds `PUNYA TIKET PEMULIHAN • SIMULASI`
to Advertising. Scan or paste the entire genuine CCP/Recovery Ticket into
the **masked entry**; raw codes must not be put in terminal logs or screenshots.
After a privacy-retired visit, Advertising is shown while the original
backend occupancy remains protected. A new Photo or Meong Fly tap performs
the original in-process PREPARE → ACK before allowing a new visit. A current
visitor is never preempted; PENDING/UNKNOWN, worker, uncertain print or Drive
conflicts leave new admission blocked.

A ticket holder returning while B is genuinely using the booth receives
WAIT; after safe isolation of a protected old visit the same original PAID
and OWED service may be reclaimed without another charge or capture.
This is still synthetic proof/financial authority in the existing process,
not a production scanner or real Midtrans recovery. Physical paper/Drive,
restart, rate limits and refund require their separate supervised gates.

## Formal pilot checklist

Follow [PP07-SUPERVISED-WINDOWS-UAT.md](PP07-SUPERVISED-WINDOWS-UAT.md) for
the numbered 26-case owner's local test worksheet, safe test-root hygiene,
device-specific expectations and redacted evidence. The pilot is **synthetic
payment only** even with real printer and real Drive enabled.
