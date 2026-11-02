# Supervised Windows pilot — synthetic payment, webcam, optional POS80

This is a **local supervised pilot**, not the full PP-07 customer UAT. Use
a **new empty** storage root for **each** trial. The launcher refuses a previously used/nonempty root, including a prior customer's encrypted credentials, payment journal or print jobs. The old visit remains privacy-fenced after shutdown; NEVER delete or reset that data to restart a test.

```powershell
git switch feature/post-preview-qris-checkout
git pull --ff-only origin feature/post-preview-qris-checkout
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
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
