# Start the physical trial

Use the existing `feature/post-preview-qris-checkout` repository checkout on the actual Windows device. This is the supervised **real-camera, synthetic-payment** trial. Paper and real test Drive stay off unless separately enabled. Start with manual capture buttons; this helper disables automatic face/palm triggers. No actual QRIS transfer or refund is part of this trial.

## 1. Update and check once

Close any running kiosk first. In PowerShell, from the repository folder:

```powershell
if ((git branch --show-current).Trim() -ne 'feature/post-preview-qris-checkout') {
    throw 'Wrong checkout; preserve it and use the authorized existing branch.'
}
if (git status --porcelain) { throw 'Preserve local changes before updating.' }
git pull --ff-only origin feature/post-preview-qris-checkout
if ($LASTEXITCODE -ne 0) { throw 'Update failed; stop here.' }
.\Start-PostPreviewDeviceTest.ps1 -Setup -CheckOnly
```

The setup reuses `.venv-kivy` or `.venv`, creates `.venv-kivy` only when no usable environment exists, installs the three current requirements files and runs `pip check`. A broken existing `.venv-kivy` is preserved for repair. New environments require Python 3.12. The check must finish with `READY_FOR_SUPERVISED_SYNTHETIC_PILOT`. Setup installs software; the subsequent check-only phase opens no devices and creates no trial folders.

If Windows policy blocks local PowerShell scripts, use the direct Python route below. Do not change system policy just for this test.

## 2. Open the camera trial

```powershell
.\Start-PostPreviewDeviceTest.ps1
```

The helper selects the same environment, enables the real camera/audio only in the child process, clears inherited offscreen/dummy test drivers, and creates a unique unused trial identity. It prints the private test-folder location and a separate local `session.json` location. Both are ignored by Git. It never deletes or reopens a previous trial. Run it again for a new isolated trial; preserve old folders, especially after a crash or uncertain paper.

Default initial size is **452x900** for a laptop. Use a display with enough usable height, or resize the native window so the entire card/buttons remain visible. A clipped claim card must hold checkout, not pretend proof was offered. For the portrait touchscreen:

```powershell
.\Start-PostPreviewDeviceTest.ps1 -Size 800x1280
```

If the intended USB camera is not index 0, close the trial and select its known index, for example `-CameraIndex 1`. Close other camera applications and enable the operating system's desktop-camera permission. The static preflight does not certify camera frames, speaker sound or a usable display.

## 3. First complete observation

1. Open Photo from Ads, finish the tutorial and select two different designs with copies **2 and 1**.
2. Take three photos per design. Optionally retake one selected frame per design; a second retake must be refused. Copies must not add capture sessions.
3. Inspect all previews. Total must be **Rp25,000**, consistently through the frozen checkout. Save the privately offered CCP; it is not the payment QR.
4. Use **SIMULASI PAID • TANPA TRANSFER**. Do not transfer money or scan the mock payment as a real merchant QRIS.
5. Inspect the mandatory original Recovery Ticket QR/full code. It remains visible for 30 real visible seconds or until NEXT; virtual receipt success must not skip it. In a separate fresh trial, observe early NEXT.
6. After the ticket closes and the customer folder URL is verified, observe automatic purchased-strip dispatch for the **2+1** copy plan; there is no customer print button. An uncertain receipt/strip holds remaining batches, without resend. Default QR says **QR DEMO • BUKAN LINK DOWNLOAD**; it is intentionally not a working cloud link. Virtual SUBMITTED is not paper and does not close the original OWED liability. [9 November implementation/evidence](PP05-AUTOMATIC-PAID-PRINT-2026-11-09.md).
7. On the paid results page, observe its separate 30-second countdown and automatic return to Ads. Do not close the app; no new finish button is needed. Status refresh must not restart the timer. Confirm old photos/QR disappear; the original order remains preserved. See [BUG-046 retest](BUG046-RESULT-AUTO-RETURN.md).
8. Complete same-process A/B privacy, busy WAIT and original-proof recovery observations using the [26-case owner worksheet](PP07-SUPERVISED-WINDOWS-UAT.md). Neither the helper's exit code nor session record marks an owner case PASS.

Record source SHA, platform, layout, camera, expected/observed and PASS/FAIL/BLOCKED in the worksheet. Keep proof codes/QRs/private photographs out of shared logs or screenshots. The local session JSON records profile, source HEAD, timestamps and exit state only; it is not a clean-tree attestation, hardware result or financial receipt.

## 4. Add owned POS80 paper after the camera trial

Reuse the existing configured printer route from [printer setup](../../printer-setup.md): `PHOTOBOOTH_PRINTER_WINDOWS_NAME`, LAN/Wi-Fi host or supported USB settings. The name/address must be your actual owned test printer. No route is guessed or installed by this helper.

```powershell
.\Start-PostPreviewDeviceTest.ps1 -CheckOnly -EnableRealPrinter -AcceptRealPaper
.\Start-PostPreviewDeviceTest.ps1 -EnableRealPrinter -AcceptRealPaper
```

Both flags are mandatory. Expect one original ticket receipt and automatic purchased-strip batches with selected copies after the ticket stage and verified URL. Inspect actual paper, QR, orientation and cuts. Transport SUBMITTED is not physical delivery. On uncertain output, stop and retain the original journal; do not resend, reset a root or unplug/jam an active production printer.

## 5. Add approved test Drive independently

Only use your own test photos and an approved test account/booth. Reuse the already deployed Apps Script URL/token securely through `PHOTOBOOTH_WEB_APP_URL` and `PHOTOBOOTH_UPLOAD_TOKEN`; do not paste tokens into shared commands or reports. This is real upload/public-link publication and needs its own scoped approval. No cloud service is deployed by setup.

```powershell
.\Start-PostPreviewDeviceTest.ps1 -CheckOnly -EnableRealDrive -AcceptPublicTestUpload
.\Start-PostPreviewDeviceTest.ps1 -EnableRealDrive -AcceptPublicTestUpload
```

Both flags are mandatory. Verify the original customer's folder and file counts from a signed-out phone, truthful upload pending and correct verified URL. Test printer and Drive separately before combining their four flags. Actual deletion/retention is a separate scoped exercise.

## Direct Python route / Ubuntu

Reuse the active local environment that already has all three requirements files installed. Windows example:

```powershell
.\.venv-kivy\Scripts\python.exe -m pip install -r requirements.txt -r requirements-post-preview.txt -r requirements-qris.txt
.\.venv-kivy\Scripts\python.exe tools/start_post_preview_device_test.py --check-only
.\.venv-kivy\Scripts\python.exe tools/start_post_preview_device_test.py
```

Use `.venv` instead if that is the working environment. On Ubuntu with a real desktop session and camera permissions:

```bash
.venv-kivy/bin/python -m pip install -r requirements.txt -r requirements-post-preview.txt -r requirements-qris.txt
.venv-kivy/bin/python tools/start_post_preview_device_test.py --check-only
.venv-kivy/bin/python tools/start_post_preview_device_test.py --size 800x1280
```

The Python entry accepts the original double-consent flags in kebab case, e.g. `--enable-real-printer --accept-real-paper`. It does not install a missing interpreter or change branches. Ubuntu platform-protected restoration remains unsupported; fresh-root physical trials do not certify it.

## Stop conditions and remaining acceptance

Stop on wrong-customer images/folder, duplicate charge/paper, unsafe isolation, corrupt media, unreadable proof, failed camera or unclassified printer state. Preserve the root, source and redacted steps. Never bypass ownership, vault or print guards.

This helper does not enable occupied-root restart recovery, actual post-preview merchant QRIS, refund or production. R2 verifies a separate Windows protected mock service restore after already committed local ACK; the owner pilot still uses ephemeral synthetic escrow. Full pre-ACK original-worker/device/reboot/Ubuntu recovery, actual merchant/refund capability, commercial/legal review and long-duration qualification remain separate. These do not prevent the fresh-root supervised physical trial described above. See [software readiness evidence](PP07-PHYSICAL-TEST-READINESS-2026-11-05.md).
