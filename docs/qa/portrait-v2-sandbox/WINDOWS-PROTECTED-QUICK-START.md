# Windows protected Sandbox entry

10 November 2026: Windows is the immediate owner priority. Ubuntu launcher/
autostart packaging is deferred. This is an explicit merchant Sandbox integration
entry, not commercial release or a replacement for the original synthetic trial.

For the already-working camera trial with no merchant/Drive/paper, keep using
`Start-PostPreviewDeviceTest.ps1` and the [existing guide](PP07-PHYSICAL-QUICK-START.md).
It remains synthetic payment. Do not scan its mock QR with a banking app.

## Check the protected configuration

Use the existing `feature/post-preview-qris-checkout` Windows checkout. Close any
other kiosk. Preserve local modifications and original data before updating with
`git pull --ff-only origin feature/post-preview-qris-checkout`.

```powershell
.\Start-PostPreviewSandbox.ps1 -StorageRoot 'C:\MeongData' -Setup -CheckOnly
```

Use the SAME stable existing storage root on later runs; the example is not a
request to replace/recover old storage. Setup reuses the original Python3.12
venv/dependency helper in check-only mode, then checks this protected profile.
It does not open either GUI. Without setup, use `-CheckOnly` with the existing venv.

The protected loader reads complete pairs from secure environment OR the existing
ignored `photobooth/local_settings.py`: `MIDTRANS_SANDBOX_MERCHANT_ID` /
`MIDTRANS_SANDBOX_SERVER_KEY`, and `WEB_APP_URL` / `UPLOAD_TOKEN`. Environment
names are `MIDTRANS_MERCHANT_ID` / `MIDTRANS_SERVER_KEY` and
`PHOTOBOOTH_WEB_APP_URL` / `PHOTOBOOTH_UPLOAD_TOKEN`. Partial environment pairs
are rejected instead of mixed with file settings. Never put credentials in
arguments, chat, screenshots or repository files. Local settings are parsed as
literal fields without executing Python code. Reuse the deployed test Drive
account and original `data/printer_settings.json` or explicit printer environment
configuration; no route/device is guessed.

The canonical prior v2 merchant history is
`data/kiosk-v2-sandbox/<merchant>/<booth>/orders.sqlite` with its original
`visit.json`. Missing, foreign, unresolved or corrupt history holds startup.
The older v1 trial directory also holds until separately reconciled. **Do not
copy a synthetic root, create an empty DB/journal, edit a payment to CANCELLED,
or delete history to pass this check.** For a genuinely new booth with no original history, use explicit enrollment
below. Existing or partial history must stay preserved and held.

Success says **LOCAL CONFIGURATION/HISTORY VALID**. Custody/merchant/Drive
sharing/printer/camera remain **NOT_CHECKED**. It is not account/device acceptance.
The backend later requires actual Windows DPAPI custody and independent original
freeze/charge/device/Drive readiness. No replacement key or plaintext fallback.

## First install: explicitly enroll a genuinely new booth

Only if this is a NEW booth with no previous canonical legacy/payment/photo or
protected installation, use local-only enrollment. The source audits known roots
and configured external legacy paths; any old/partial history blocks. Never
delete it or choose a replacement root to pass. Keep the SAME selected storage.

```powershell
.\Start-PostPreviewSandbox.ps1 -StorageRoot 'C:\MeongData' -Setup -SetupOnly -EnrollNewBooth -SandboxOnly
.\Start-PostPreviewSandbox.ps1 -StorageRoot 'C:\MeongData' -CheckOnly
```

`-Setup` reuses dependency preparation; `-SetupOnly -EnrollNewBooth` is a separate
explicit LOCAL enrollment and never starts a GUI/backend/camera/printer/Drive or
provider request. Do not combine with CheckOnly or external run flags. It creates
non-secret original enrollment metadata and a dedicated original empty baseline,
not a fabricated legacy visit.json/order. Retrying completes only the same intact
intent; corrupt/foreign/nonempty/partial evidence stays held. Normal launch and
check-only NEVER initialize automatically. Enrollment cannot grant old photos,
payment or booth FREE. Backend custody and protected boot remain NOT_CHECKED.

## Explicitly run an owned Sandbox test

Only after local prerequisites and applicable account/paper/public-test-upload
authorization, use the original double consents for BOTH external effects:

```powershell
.\Start-PostPreviewSandbox.ps1 -StorageRoot 'C:\MeongData' -SandboxOnly `
  -EnableRealPrinter -AcceptRealPaper -EnableRealDrive -AcceptPublicTestUpload
```

This profile needs the real configured test printer and Drive for its original
paid-delivery readiness; it supplies no virtual substitute. Use only your own
test photographs. **Use the official Midtrans Sandbox simulator; never scan/pay
with a real banking/wallet app.** Default booth PB001 and window452x900; optional
`-BoothId PB001 -Size 800x1280 -CameraIndex 1` select the intended values. The
manual camera/audio setup reuses the original Windows trial helper and removes
inherited offscreen/dummy drivers. Face/palm triggers are disabled for this
bounded manual-entry candidate; their automatic activation is not qualified here.

Native screens are the original protected visits app: capture/all previews,
original private CCP, QRIS, mandatory original Recovery Ticket and automatic paid
output. Keep proof codes/QRs/private photos out of shared diagnostics. SUBMITTED
is not physical paper delivery and preserves the original OWED status.

Closing the window requests original private retirement. A held camera/file/
preview/health/backend worker keeps the SAME launcher/global lock alive until
actual exit; `SHUTDOWN HELD` is not permission to restart, force-kill or resend.
After a crash/unresolved boot, preserve original roots/custody and use supported
recovery only. Pre-ACK/orphan boot, legacy migration/reconciliation, refund/status
operations and final qualification remain separate unfinished work.
No production endpoint/default activation, real money/refund or deployment is
authorized by these source instructions. Existing owner smoke observations stay
credited; only new/unresolved Windows/profile observations need recording.

## Source-specific verification

Runtime119c321:897 backend/99 actual-X11 native/34 Apps Script local PASS.
CI42779790541 all four jobs SUCCESS (Windows376+521, native99, Ubuntu897),
zero failures/errors/skips, completed logs inspected. Actual new PowerShell
check-only returned the expected BLOCKED2 without account configuration. This
is not actual Windows GUI/hardware/merchant acceptance.
[Evidence and exact remaining source work](PP06-PROTECTED-LAUNCH-2026-11-10.md).

The local history result covers the selected original canonical legacy history
or an exact explicit new-booth enrollment baseline. Protected session boot is
checked separately by original backend startup; preflight does not certify a
restart. Never reset a held visit to open a fresh customer.

## Normal shutdown and restart after the L3-B increment

The protected Windows entry opts into original privacy retirement → PREPARE →
actual local worker receipt → independently verified backend ACK before final
handle/global close. It does not open a new visitor just to archive the old one.
An empty idle booth creates no fake customer release. Safe unpaid or original
paid/OWED visits retain their media/rights and verified release on the SAME root.
Restart starts protected Ads; accessing paid originals still requires the SAME
original CCP/Recovery Ticket and fresh independent settlement. Submitted ticket/
strips are never replayed. Save genuine customer proof as before.

A pending/unknown payment, financial discrepancy, uncertain paper or actual live
worker keeps **SHUTDOWN HELD**. This is not a successful release; do not force-kill
or restart a second instance. Actual process death before a valid original ACK
still leaves boot held pending supported recovery. Enrollment cannot repair it:
never use EnrollNewBooth against a prior protected install or switch storage roots.
Do not delete keys, DB/WAL/SHM, enrollment files, media or print jobs. The
first-install command only applies to genuinely new, audited history absence.

The owner confirms all three configurations are available on Windows. Their
actual readiness, paper/phone access and account qualification remain to be
observed on that PC; no secret values are needed in chat. Existing owner smoke
observations remain credited. See [the current source/evidence](PP06-WINDOWS-SETUP-RECOVERY-2026-11-10.md)
for exact qualification and known unsupported interrupted-boot cases.
