# Private-preview development UI

1 November 2026. Existing branch `feature/post-preview-qris-checkout` only.
**Partial software development aid, NOT_READY_FOR_PHYSICAL_UAT.**
The full PP payment/ticket/fulfillment/recovery/refund route is unfinished. This
launcher offers only isolated unpaid private capture/review/all-design preview.
Do not use it for customers or merchant acceptance.

Reuse: original portrait App/PhotoViews, branding/catalog/gallery, camera owner,
five-second deliberate countdown, mirrored live preview, PhotoJobs single-flight
worker and original JPEG/PNG journals. Default and legacy paid-first launchers
are unchanged. The dedicated subclass rejects PRINT, DRIVE, Sandbox and MOCK
checkout profile opt-ins. It constructs no payment/print/upload transport.

## Windows development launch

Use Python 3.12, the repository's existing virtual environment/dependencies and
webcam setup. No merchant credentials are required. From the repository root:

```powershell
git status --short
git branch --show-current
git fetch origin feature/post-preview-qris-checkout
git rev-parse HEAD origin/feature/post-preview-qris-checkout
# Preserve dirty files; do not switch/create branches or reset local records.
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:PHOTOBOOTH_V2_CHECKOUT_SANDBOX = '0'
$env:PHOTOBOOTH_V2_CHECKOUT_MOCK = '0'
$env:PHOTOBOOTH_V2_PRINT = '0'
$env:PHOTOBOOTH_V2_DRIVE = '0'
.\.venv\Scripts\python.exe tools/run_post_preview_private.py --private-root work\post-preview-private
```

The PowerShell commands are documented, not Windows-device acceptance. Python
dependency installation follows existing project requirements; no production
configuration or live Drive operation is authorized. On Linux use the equivalent
activated environment and `python tools/run_post_preview_private.py --private-root
work/post-preview-private`. The launcher reuses the checkout's original native
LaunchLease so another ordinary/merchant GUI launcher cannot run concurrently.

## Current observable behavior

1. Advertising -> normal tutorial -> existing 12-template gallery.
2. Select multiple designs/copies, choose MULAI FOTO and private photo consent.
3. Every design uses SIAP with the original five-second countdown; disconnect
   cancels rather than taking a shot. Original captures remain unmirrored;
   preview/review photo regions mirror. One selected-slot retake per design.
4. Approve each private preview, then LANJUT to the next design. No paper or
   public upload. After the last design, scroll through every final preview.
5. UBAH DESAIN / JUMLAH returns to the original gallery; retained designs preserve
   captures and consumed retake. Newly selected designs need their own three.
6. Payment button remains disabled. All-design preview does not freeze checkout
   automatically or mark the purchase/service paid/completed.
7. Minimize/explicit cancellation/exit to Ads after admission privacy-lock the
   old session. Late worker replies cannot restore private pixels. Restart holds
   unresolved ownership; it never automatically restores photos for another user.

**Current limitation:** safe unattended close/release and returning-customer
proof are unfinished. A locked development draft stays held; no reset/unlock/
customer-data deletion command is provided. For a separate synthetic-only test,
use a different explicit empty private root, leaving prior data intact. Never use
that as a way to bypass a real active booth/payment/print obligation. No commercial
flow is available in this profile. Adaptive inactivity/recovery policy, genuine
payment, CCP/vault, mandatory ticket concurrency, paid Drive/print, diagnostics and
refund state still need implementation/integration before full physical UAT.

## Software evidence and synthetic screenshots

```bash
python tools/run_kiosk_unittests.py test_post_preview_widgets
python tools/render_post_preview_private.py --width 800 --height 1280 --output-dir work/private-800
python tools/render_post_preview_private.py --width 452 --height 900 --output-dir work/private-452
```

Run screenshots in separate fresh processes; resizing a live software-GL window
can corrupt readback. These drivers use temporary storage and synthetic camera
pixels, never a real webcam, merchant, printer or cloud. Screenshots contain no
redeemable credentials. Native tests exercise the real UI/worker/disk path at both
portrait sizes plus disconnect/minimize and mixed-profile rejection.

See the [live implementation checkpoint](POST-PREVIEW-QRIS-IMPLEMENTATION-CHECKPOINT.md)
for tested source, exact results, CI and next action. A partial private-preview
screen is not evidence for the 112 complete new-order acceptance cases or the
future physical UAT runbook.
