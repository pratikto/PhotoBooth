# UX-07 lifecycle — owner laptop check

30 October 2026. Automated lifecycle fixtures are separate from these **NOT_RUN**
manual checks. Record the actual source/device below; do not import old passes.
The dedicated Midtrans Sandbox still keeps printer and Drive OFF. The purchased
print host is an unmounted offline fixture, not a customer-facing commercial GUI.

## Update without overwriting local work

In your existing Windows checkout and Kivy environment:

```powershell
git branch --show-current
git status --short
```

Expected branch: `feature/portrait-kiosk-v2-next`. Preserve any local edits before
pulling; do not reset/clean or copy the old cloud workspace patch over this branch.

```powershell
git pull --ff-only origin feature/portrait-kiosk-v2-next
git rev-parse HEAD
python tools/run_portrait_v2_sandbox.py
```

Use only your existing Sandbox credentials/local settings and the official
Midtrans simulator. Keep the original recovery ticket privately available;
it is a photo-access secret. Do not share QR/ticket payloads, keys or operator PIN.
Never pay a test QR with a real banking/wallet application.

## Laptop/device observations — all initially NOT_RUN

- [ ] **Record device/source:** actual SHA and dirty state, Windows version,
  Python/Kivy/OpenCV versions, display resolution/scaling and camera model.
- [ ] **Payment page:** the original pending QR and Sandbox copy-link work with
  the official simulator. A restart checks the same pending order, not another
  charge. Keep the recovery ticket for this visit.
- [ ] **Paid camera:** after simulated settlement and explicit consent, capture
  one/two photos. Each capture waits for the deliberate countdown. Confirm copies
  and selected design stay unchanged through the following steps.
- [ ] **Minimize/restore:** background the app, then return. Old photo/strip,
  payment QR and typed recovery input must be hidden. No countdown/shutter,
  print or upload starts automatically.
- [ ] **Invalid proof:** try an invalid recovery ticket without changing stored
  files or database. Remain on the private claim page; no photos or extra payment.
- [ ] **Original proof:** enter the original valid ticket. The same session is
  found; old photos appear only after deliberate continuation. Capture count,
  retake allowance and selected copies remain correct. No repeated photos/charge.
- [ ] **Close/reopen:** repeat after a partial capture and after a retake/result.
  Resume the original visit with the original ticket and deliberate continuation.
  Saved originals/output remain unchanged; no automatic effects.
- [ ] **Protected release/return:** use the existing recovery operator control
  and private PIN printed by the launcher to prepare/isolate/acknowledge release.
  The new-visitor page must appear only after confirmed isolation/ACK/archive.
  Start another test visit: its screen must not expose the previous photos.
  The old ticket cannot take over an active new visit. Once the booth is free,
  the original ticket can reclaim only its own retained session.
- [ ] **Responsiveness/layout:** repeat relevant controls at 800×1280 and 452×900
  where your display permits; record any size unavailable on the laptop rather
  than passing it. Check mouse/touch/keyboard, camera reconnect and fast repeats.

If any step fails, record the exact step, SHA, displayed state and sanitized error.
Keep journals, counters, manifests, payment/claim records and original media.
Do not delete/change them, switch booth IDs or pay again to clear an uncertain
visit. Never infer refund/physical printing/completion from occupancy release.

## Printer and purchased-print limits

The automated l2b fixture uses a synthetic printer **separate** from the bound
transport-off photo worker. It verifies SENDING/UNCERTAIN holds, drained worker
isolation, lost ACK/restart, durable archive and original return. It does not
prove that paper emerged or supply a mounted commercial paid-print journey.

For a separately chosen **ordinary local device test**, existing
`python tools/run_portrait_v2.py --print` uses the saved printer configuration.
Record copies/orientation/QR and inspect actual paper. This is not a paid Sandbox
acceptance or a reason to enable transports in the dedicated merchant trial.
Do not intentionally interrupt an uncertain real print and then resend it.

PAY-22 Legacy provider creation contract and WEB-01–08 public infrastructure
remain BLOCKED. Actual merchant, Ubuntu mini-PC, paper, phone, Drive/deletion,
privacy operations/support/compensation, commercial host mounting and release
approval remain separate gates. A laptop pass does not close those gates.
Whole UX-07 and AR-13 are not declared complete by the fixture tests.

## Result to paste back (without secrets/private images)

```text
Source SHA / dirty:
Windows / Python / Kivy / OpenCV:
Display / scaling / camera:
Launch command:
Checks passed:
Checks failed + exact step:
Checks NOT_RUN + reason:
Visible error/state and redacted evidence:
```
