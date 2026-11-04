# Start here — supervised post-preview device testing

**Software candidate gate verified:** [CI 41826366906](https://github.com/pratikto/PhotoBooth/actions/runs/41826366906)
at source `0601354` completed 3/3 SUCCESS: Windows 533, Ubuntu 533, native Kivy
61 PASS, zero failures/errors/skips. Owner preflight and real observations are
still required. Readiness applies only to the supervised synthetic-payment
pilot described here, not actual merchant/restart/refund/production approval.

Updated 4 November 2026. Branch: `feature/post-preview-qris-checkout`.
Read the [current engineering evidence](PP07-DEVICE-READINESS-2026-11-04.md)
for the exact tested source and CI status before selecting a checkout.

## 1. What this candidate can test

This is the existing **synthetic-payment-only** owner pilot with a real webcam
and optional explicitly authorized POS80/test Drive. Its mock PAID action never
sends money. It exercises capture before payment, private proof, the mandatory
ticket screen, purchased output, safe A/B handoff and original in-process claim.
The original legacy paid-first application/launcher remains separate.

| Mode | Available path | Acceptance boundary |
| --- | --- | --- |
| Camera/touch/audio with virtual printer and fake Drive | Default pilot below | Owner physical observations required |
| Owned POS80 with synthetic payment | Two explicit paper flags | Inspect actual paper/cuts; SUBMITTED is only transport |
| Approved test Drive with synthetic payment | Two explicit upload flags | Creates public-link test photos; inspect phone access/file counts |
| Actual post-preview merchant Midtrans Sandbox | BLOCKED in this launcher | Do not reinterpret the mock QR as payable or turn on legacy flags |
| Actual refund / production / Android release | NOT_ENABLED / NOT_APPROVED | Separate provider, security, legal and release gates |

The existing backend has provider components, but the integrated post-preview
kiosk is deliberately restricted to mock payment and synthetic escrow. Genuine
merchant configuration and protected cross-process/platform escrow are not
supplied by this pilot. Do not remove these restrictions to obtain a green test.
Ubuntu OS-vault support remains unsupported by `platform_protector`; Windows
DPAPI device acceptance is separate from the pilot's ephemeral synthetic key.

## 2. Preserve source, environment and previous tests

Run from the repository root. First inspect `git status --short`,
`git branch --show-current`, `git rev-parse HEAD` and `git log -5 --oneline`.
Proceed only on the exact authorized existing branch, preserving all local edits.
If the branch differs, use the correct checkout; do not apply a blind switch,
pull, reset or branch creation to unrelated work. With a clean correct checkout,
`git pull --ff-only origin feature/post-preview-qris-checkout` preserves history.

Use Python 3.12 for parity with CI. Keep a working `.venv-kivy` or `.venv`;
create an environment only when neither exists. Record the selected interpreter
and source SHA. Do not copy local merchant secrets into scripts or bug reports.

### Windows PowerShell

```powershell
if ((git branch --show-current).Trim() -ne 'feature/post-preview-qris-checkout') {
    throw 'Wrong checkout. Preserve it and use the authorized existing branch.'
}
if (git status --porcelain) { throw 'Preserve local changes before updating.' }
git pull --ff-only origin feature/post-preview-qris-checkout
git rev-parse HEAD

if (Test-Path '.\.venv-kivy\Scripts\python.exe') {
    $meongPython = '.\.venv-kivy\Scripts\python.exe'
} elseif (Test-Path '.\.venv\Scripts\python.exe') {
    $meongPython = '.\.venv\Scripts\python.exe'
} else {
    py -3.12 -m venv .venv-kivy
    $meongPython = '.\.venv-kivy\Scripts\python.exe'
}
& $meongPython -m pip install -r requirements.txt -r requirements-post-preview.txt -r requirements-qris.txt
$env:PHOTOBOOTH_V2_CHECKOUT_SANDBOX = '0'
$env:PHOTOBOOTH_V2_CHECKOUT_MOCK = '0'
$env:PHOTOBOOTH_V2_PRINT = '0'
$env:PHOTOBOOTH_V2_DRIVE = '0'
& $meongPython tools/run_kiosk_unittests.py test_post_preview_pilot_preflight test_post_preview_pilot_early_root test_post_preview_pilot_launcher
& $meongPython tools/check_post_preview_pilot.py --json
```

Check each exit code. Preflight must report
`READY_FOR_SUPERVISED_SYNTHETIC_PILOT`; it does not certify a working camera,
printer, account, speaker, upload, secure vault or complete customer experience.

### Ubuntu desktop / intended mini PC

Use the same clean-branch/source checks and all three dependency files. Keep
an existing Linux environment or create one with `python3.12 -m venv .venv-kivy`.
The Windows environment cannot be copied as a Linux environment. Ensure a real
desktop session, camera permission and the existing printer setup are available;
CI's offscreen rendering does not replace an actual display test.

```bash
meong_python=.venv-kivy/bin/python
"$meong_python" -m pip install -r requirements.txt -r requirements-post-preview.txt -r requirements-qris.txt
export PHOTOBOOTH_V2_CHECKOUT_SANDBOX=0 PHOTOBOOTH_V2_CHECKOUT_MOCK=0
export PHOTOBOOTH_V2_PRINT=0 PHOTOBOOTH_V2_DRIVE=0
"$meong_python" tools/run_kiosk_unittests.py test_post_preview_pilot_preflight test_post_preview_pilot_early_root test_post_preview_pilot_launcher
"$meong_python" tools/check_post_preview_pilot.py --json
```

If using `.venv`, change only the interpreter path. Required desktop libraries
and connection-specific permissions depend on the installed Ubuntu version;
resolve the actual import/device error rather than disabling a safety check.
Refer to the [existing printer setup](../../printer-setup.md).

## 3. First physical smoke: camera, no paper, no cloud

Use a **new unused dedicated root**. Start from `-001`; choose `-002` for another
trial. The launcher rejects occupied roots and symlinked ancestors. Never remove
or reset an earlier root to make it pass: it may preserve OWED, encrypted proof,
uncertain paper and investigation evidence.

```powershell
& $meongPython tools/run_post_preview_checkout_pilot.py --synthetic-payment-only --private-root work\postpay-device-001
```

Ubuntu equivalent:

```bash
"$meong_python" tools/run_post_preview_checkout_pilot.py --synthetic-payment-only --private-root work/postpay-device-001
```

On the actual portrait touchscreen:

1. Inspect advertisements, both entry paths, audio and permitted existing
   operator/Device Health controls. Record unsupported controls as such; no
   operator setting may bypass protected ownership. No speaker PASS from a
   software playback state.
2. Start Photo, complete the fresh visit tutorial and select two designs with
   quantities 2 and 1. Expect two independent three-shot sessions, six initial
   photos and Rp25,000 total. Copies must not add captures.
3. Observe mirrored live preview and original raw JPEG orientation. Use one
   selected-slot retake per design. No second retake or quota reset by editing.
   Review/strip photo regions follow the approved v2 mirroring; QR/text stay normal.
4. Review all designs before checkout. Edits belong before the first durable
   provider-create intent; payment/poll/retry must not silently mutate the cart.
5. Save the privately offered CCP. It is distinct from the mock payment QR.
   Use `SIMULASI PAID` only; do not transfer money or scan it as actual Midtrans.
6. The same original Recovery Ticket must be legible as QR and full code for
   30 actually visible seconds, with NEXT available. Virtual receipt success
   must not skip the screen. Repeat in a fresh trial with early NEXT.
7. Confirm purchased three-photo strips and exact per-design quantities. Default
   Drive QR says `QR DEMO • BUKAN LINK DOWNLOAD`; failing to download from that
   fake URL is expected. Virtual SUBMITTED is not paper or fulfilled service.
8. Within the same running pilot, retire A to protected Advertising and start B.
   B must receive a fresh tutorial/cart, own photos and independent checkout
   only after exact safe ACK. A's original rights remain OWED/recoverable.
9. Returning original proof during live B must not take over B. From permitted
   protected Advertising use the masked original-proof field; valid proof/free
   booth can restore original in-process rights without new payment/capture.
   Wrong-role/invalid proof must not disclose photos or release anyone.

Use the full [26-case worksheet](PP07-SUPERVISED-WINDOWS-UAT.md). All owner rows
remain NOT_RUN until personally observed and recorded at the selected source.

## 4. Optional owned POS80 test

After the no-paper trial, configure the existing printer environment/settings
for the owned LAN/Wi-Fi/Windows queue/USB device, following the original setup.
Do not place credentials in a shared command transcript. Choose another new root
and append **both** `--enable-real-printer --accept-real-paper`.

Observe exactly one original ticket receipt plus the selected strip batches,
paper width/length, photo orientation, QR scan and cuts. Record separately:
transport state, actual paper count, partial output and customer receipt.

Do not deliberately jam, unplug or power-cycle a live production printer.
Synthetic fault coverage verifies software holds; controlled physical fault
injection needs test-only hardware and an onsite safe plan. On SENDING/UNCERTAIN,
stop and preserve the root/journal. Do not resend, fail over, force the next
batch, clear a lease or assume no paper emerged.

## 5. Optional authorized test Google Drive

Use an approved nonproduction account/booth and only your own test photographs.
Configure the existing deployed Apps Script URL/upload token securely using
`PHOTOBOOTH_WEB_APP_URL` and `PHOTOBOOTH_UPLOAD_TOKEN`. This guide does not deploy
or change the Web App. Use a fresh root and append **both**
`--enable-real-drive --accept-public-test-upload`.

This makes real cloud writes and may expose test photos to anyone with the
individual folder link. Precharge requires authenticated sharing health and
available READY capacity without consuming a visitor's binding. After synthetic
PAID, expect exact `Photobooth/PB001/Photo/NNNNNNNN/{raw,bw,color}` customer
binding under the installed contract. Purchased strips wait for that verified
viewer URL. The screen distinguishes real test Drive from a fake QR.

Open the link on a phone without the booth account. Check correct customer's
folder, no access-denied/login requirement, file contents and verified upload
counts. A verified URL can precede all bytes; pending upload must be labeled.
Disconnect network only in an authorized test: readiness/OWED/retry must remain
truthful without duplicate charge, folder or paper.

Actual 15-day local/30-day Drive deletion is a separate authorized synthetic
retention exercise. Dry-run/readiness or source publication is not deletion
evidence. Never use real customer data or enter `old` for this exercise.

## 6. Restart, long-run and financial limits

- Current synthetic escrow uses an ephemeral in-process key. The owner launcher
  refuses reopening a prior occupied root as a new customer. Do not force it
  open, discard records, persist plaintext keys or claim cross-process customer
  recovery from the same-process proof exercise.
- Existing process-kill tests independently reopen SQLite and prove durable
  SENDING/OWED. They do not prove a complete protected-key device restore,
  peripheral outcome, original worker relaunch or actual paper safety.
- A new root after a crash is a new isolated test, not restoration/fulfillment
  of an earlier paid claim. Preserve previous roots and document the boundary.
- J21 verifies 12 consecutive complete synthetic paid visits. N26 verifies all
  12 native previews. Neither establishes hours-long hardware/resource/power soak.
- Meong Fly still requires one ticket/attempt and backend-authorized promotion;
  a DEMO win does not authorize a real financial discount. Keep its separate
  game/QR eligibility and hardware acceptance gates.
- Actual post-preview Midtrans, merchant refund and production remain blocked
  until guarded integration, account capabilities, platform escrow, consumer
  policy and corresponding owner/provider evidence are independently satisfied.

## 7. Stop conditions and evidence

Stop on wrong-customer photos/folder, repeated charge/receipt/strip, unclassified
paper, corrupt media, failed isolation, vault/proof mismatch or unsafe account
status. Preserve the exact root, source SHA and redacted steps. Never bypass a
hold using operator PIN, guessed order number, forced reset or data deletion.

Record test ID, Asia/Jakarta timestamp, source SHA, OS, interpreter/dependency
versions, display size, camera, printer connection, virtual/actual Drive, expected
versus observed, PASS/FAIL/BLOCKED and safe follow-up. Redact all QR/proof codes,
merchant credentials, customer images and sensitive URLs. Physical results and
provider/account results must be separate from CI/component results.

Exit statuses remain independent: SOFTWARE_VERIFICATION, supervised synthetic
device candidate, actual merchant Sandbox, HARDWARE_ACCEPTANCE and production.
See [112-case software traceability](PP07-SOFTWARE-TRACEABILITY-2026-11-04.md)
and [the source-specific continuation report](PP07-DEVICE-READINESS-2026-11-04.md).
