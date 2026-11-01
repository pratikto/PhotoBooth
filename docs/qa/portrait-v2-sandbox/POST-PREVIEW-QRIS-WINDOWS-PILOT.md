# Supervised Windows pilot — synthetic payment, webcam, optional POS80

This is a **local supervised pilot**, not the full PP-07 customer UAT. Use
a fresh storage root: the old visit remains privacy-fenced after shutdown.

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
