# Owned Windows Sandbox acceptance entry

10 November 2026. Authorized existing post-preview branch only. Goal: let the
owner BEGIN supervised normal-flow acceptance with their Windows account,
camera, POS80 and approved test Drive using the ALREADY IMPLEMENTED protected
entry. This is not commercial release or proof that all fault acceptance passes.

## Bounded contract BEFORE source

Reuse Start-PostPreviewSandbox.ps1 / tools/run_post_preview_sandbox.py and the
original configuration/history/global owner/consent guards. Do not change the
GUI provider, default health, admission, payment, receipt or print authority.
Add a thin Windows acceptance entry with passive preflight, original run,
allowlisted owner observation recording and redacted report display.

Passive preflight must not open a camera, printer, backend, merchant/Drive
connection, create/enroll replacement history or provision/replace OS keys.
Check exact authorized source/branch/interpreter/dependencies, original secure
configuration/local history and current-account Windows DPAPI self-test using
an ephemeral NON-worker test nonce in memory. The original strict printer
validator must not mint an unused worker key merely to read settings.
Success means LOCAL_PREREQUISITES_PASS, never account/device/paid/print/cloud
acceptance. Original protected startup and its actual kernel/history checks
still must succeed at run time. Original default fulfillment health stays False.

Run requires the preflight session from the same unchanged source and original
root/account/booth, plus ALL original explicit Sandbox/paper/Drive consent flags.
Delegate to the original launcher without inventing a profile/provider or
automatic enrollment. Do not execute owned effects from the Codex cloud lab.

Reports live only under the ignored local data/post-preview-acceptance folder.
Never collect credentials, plaintext/ciphertext capabilities, photos, QR/proof
codes, provider references, URLs, absolute storage/user paths or free-text notes.
Use source SHA, static case/result/status codes, UTC observation times and a
non-authorizing local scope digest. Owner results are explicitly OWNER_REPORTED,
not independently verified backend evidence. Retain earlier observations;
recording/showing must not mutate original customer journals or release a booth.
Source changes require a new acceptance session; old sessions stay preserved.

Normal owned cases cover actual camera/capture/previews, original CCP-before-
QRIS, official Sandbox simulator/independent paid status, same Recovery Ticket
screen+receipt, original copies/Drive phone access, privacy return, customer
change and normal same-root shutdown/restart/proof return. Interrupted boot,
power loss, uncertain-output remedy/refund and complete commercial acceptance
remain BLOCKED/NOT_RUN until their original software/account gates are finished.
Do not force physical faults, reset a held root or replay uncertain paper.
The eleven already credited owner smoke observations remain credited.

Test passive/no-effect orchestration, original consent/scope/source guards,
actual Windows DPAPI on Windows CI, fixed/redacted diagnostics, append-only
owner reports, forged/malformed report refusal and unchanged default guards.
Use public configuration and fake external effects in tests only. Windows CI
must run the actual PowerShell preflight/record/show entry without GUI/devices.
Micro-commit/push/verify every safe increment, then source-matched full checks.

## Implemented micro-checkpoint

Start-PostPreviewAcceptance.ps1 delegates Run to the SAME original protected
entry only after same-source/scope validation and ALL original explicit consent
flags. tools/run_post_preview_acceptance.py provides preflight/record/show.
Preflight is passive and current-account DPAPI uses only an ephemeral NON-worker
nonce in memory. Original settings now use the existing pure printer validator,
never minting an unused worker key. First regression reproduction ERROR0.294s
when worker key creation was refused; corrected PASS0.304s. This was unused
validation capability, not an issued replacement key or customer incident.

Local29 focused acceptance/settings/original-entry methods PASS1.561s, zero
failures/errors/skips.12 new acceptance methods plus one settings method extend
the complete backend registry967->980 without duplicate imported test classes.
Windows CI will exercise actual DPAPI plus PowerShell preflight/record/show and
missing-consent refusal with public fixture settings; that result is PENDING.
Full final regression/CI pending; this is not owner hardware/account acceptance.

Reports contain no free text, credentials, URLs, absolute paths or private proof.
Manifest and observations are exclusively written/fsynced, bounded and checked
for malformed/extra/linked content. Owner observations are append-only and remain
OWNER_REPORTED_NOT_INDEPENDENTLY_VERIFIED. Even all normal-case PASS values do
not make commercial_ready true. Runtime source changes hold further recording/
run validation. Uncommitted documentation-only edits do not block preflight;
changing the Git checkout revision requires a new report session, preserving
earlier observations. Never replay a payment/uncertain print to recreate a report.

## Start here on the owner's Windows PC

This worksheet starts supervised NORMAL-flow acceptance. It is not permission
to serve paying customers or to force power/network/printer failures. The
original interrupted-boot recovery and remedy gates remain unfinished.

1. Preserve local changes and original data, close any other kiosk, and update
   the existing authorized checkout with `git pull --ff-only origin
   feature/post-preview-qris-checkout`. Never reset or change branches to make
   a preflight pass. Use Python3.12 and the same Windows account as the booth.
2. Keep the existing secure Midtrans Sandbox, POS80 and Apps Script settings.
   Do not put keys/tokens in commands or chat. Use the SAME original StorageRoot
   every time. `C:\MeongData` below is an example, not a new recovery directory.
3. Run passive preflight (dependency setup only on the first run):

```powershell
.\Start-PostPreviewAcceptance.ps1 -Action Preflight -StorageRoot 'C:\MeongData' -Setup
```

Later preflight runs can omit `-Setup`. It does not start a GUI/backend, open a
camera/printer, send paper, contact Midtrans/Drive, enroll a booth or create a
replacement ledger. Windows/current-account DPAPI uses an ephemeral self-test
nonce only. `LOCAL_PREREQUISITES_PASS` means local source/dependency/settings/
history/custody prerequisites passed; actual protected startup and all physical/
account observations still remain NOT_CHECKED. Reports are local under the
ignored `data/post-preview-acceptance` directory.
The DPAPI self-test does not prove original customer-credential decryption,
backup/restore, reboot or power-loss recovery. Runtime source checks concern
tracked runtime files; they are not a complete OS/package integrity audit.

If original history is missing on a genuinely NEW booth, use ONLY the existing
[explicit new-booth enrollment instructions](WINDOWS-PROTECTED-QUICK-START.md#first-install-explicitly-enroll-a-genuinely-new-booth),
then repeat preflight with the SAME root. Existing/partial/unresolved history
must be preserved and reconciled. Do not enroll over it or select a replacement
storage root. A missing dependency/source/configuration check is not fixed by
deleting a customer journal. Runtime source changes require review; uncommitted documentation
changes and ignored local settings/reports do not block that check.

4. Copy the generated `ACCEPTANCE_SESSION=<32 hex characters>` into a variable.
   The session ID is local report metadata, not a customer proof:

```powershell
$MeongAcceptanceSession = 'paste-the-generated-32-character-session-id'
```

5. Only with your OWN test images, approved test Drive and printer, explicitly
   consent to the original external effects and start the original protected GUI:

```powershell
.\Start-PostPreviewAcceptance.ps1 -Action Run -StorageRoot 'C:\MeongData' `
  -Session $MeongAcceptanceSession -SandboxOnly `
  -EnableRealPrinter -AcceptRealPaper -EnableRealDrive -AcceptPublicTestUpload
```

All consent flags are mandatory. Run first rechecks the SAME source/root/account/
booth session, then delegates to Start-PostPreviewSandbox.ps1. The original
global/native/backend ownership, history, worker, proof, finance and device
checks remain mandatory. No dummy provider/device or fallback history is used.
Optional `-BoothId PB001 -Size 800x1280 -CameraIndex 1` are forwarded to the
original launcher; use the SAME booth ID as preflight. Use the official Midtrans
Sandbox simulator ONLY. Never scan/pay this test QR with a real bank/wallet app.
Test uploads may be public to anyone with their individual link.

## Observe and record actual normal-flow results

Do not record PASS merely because the launcher/preflight exited0. Record only
what you actually saw on this Windows PC/account/device. Use two designs with
copies2+1 for the first owned visit; copies do not create extra capture sessions.
The eleven previously reported owner smoke observations remain credited, but
their synthetic-payment result does not certify this new real Sandbox profile.

| Case | Action and required observation |
| --- | --- |
| WN02 | Original protected Ads starts; the actual selected camera provides a fresh frame. |
| WN03 | Three photos per design, maximum one retake PER design, all selected final previews before frozen checkout. For two designs/copies2+1 this is six original captures, not nine. Frozen artwork/amount/copies agree with the final preview. |
| WN04 | The original private CCP is genuinely offered BEFORE any QRIS charge. Save it privately; do not paste it into the report. |
| WN05 | While the original QRIS is visible, press F8 to copy its current Sandbox image URL locally. Paste it into the official simulator as described below. Independent status becomes PAID for the same frozen order, without another charge/order. |
| WN06 | SAME original Recovery Ticket gets30 genuinely visible seconds OR your NEXT, with the same receipt sent once concurrently. Printer success does not skip the screen opportunity. Inspect actual paper. |
| WN07 | The actual verified individual Drive link opens the correct OWN test photographs on your phone, including expected variants. A backend/upload acknowledgement alone is not phone acceptance. Never put the URL/photos into the report. |
| WN08 | Actual paper contains the selected original artwork/designs and exactly the original copies2+1. No uncertain/submitted status is taken as proof of physical delivery. |
| WN09 | Paid result returns to Ads after its own30 seconds; old photo/proof/QR disappears and refresh does not renew the deadline. |
| WN10 | Next owned visitor B cannot see A. A's return requires A's original private proof and independently verified legitimate PAID, with no charge/print replay. |
| WN11 | After all normal operations finish, close normally, wait for actual shutdown, and run the SAME acceptance session/root again. Old paper/charge is not replayed; old images still require original proof. |

### WN05: use the official simulator with the actual current QR

Keep the kiosk window visible and open the [official QRIS Sandbox simulator](https://simulator.sandbox.midtrans.com/v2/qris/index)
alongside it. Do not minimize/suspend the kiosk to switch windows: original
privacy retirement remains active. Save the original CCP privately FIRST.
When the actual payment QRIS is displayed, press **F8** in the kiosk window.
The console prints only SANDBOX_SIMULATOR_QR_COPIED or a fixed COPY_HELD code.
Paste the local clipboard into the simulator's **QR Code Image Url** field and
choose **Scan QR**. Check that the displayed amount matches the original frozen
checkout and complete only that official simulated payment. The original app
then observes the independent provider GET; use PERIKSA STATUS if needed.

The F8 handoff exists only when Run validates this owned acceptance session.
Ordinary original launch without that session does not install it. It does not
mark PAID, make a provider call, write a URL to a report/log, or copy customer
CCP/Recovery Ticket content. If QRIS changes/expires, obtain the CURRENT value
again; do not simulate an unrelated/old order. Never send a real bank transfer.
On exit it clears only its own unchanged clipboard value, preserving a later
owner-copied private proof. Do not paste the clipboard into chat/shared reports.

In a second PowerShell window, append one observation at a time:

```powershell
.\Start-PostPreviewAcceptance.ps1 -Action Record -Session $MeongAcceptanceSession -Case WN02 -Result PASS
.\Start-PostPreviewAcceptance.ps1 -Action Record -Session $MeongAcceptanceSession -Case WN07 -Result FAIL
.\Start-PostPreviewAcceptance.ps1 -Action Show -Session $MeongAcceptanceSession
```

Choose PASS/FAIL/BLOCKED for the actual case; the examples are not instructions
to fabricate these outcomes. Repeat Record after a new observation if needed;
the earlier result remains in the append-only event history. Reports contain
only fixed codes/checks, source/session IDs, times and a non-authorizing scope
digest. There are no notes/credential/photo/proof/URL fields. Share only this
generated Show output when asking for diagnosis, never the customer data tree,
private settings, screenshots of a proof or raw operational logs.

All case PASS values mean PASS_OWNER_REPORTED for NORMAL flow only, explicitly
NOT_INDEPENDENTLY_VERIFIED. They never set commercial_ready true, update money/
fulfillment, release a booth or bypass original readiness. If runtime code has
changed, Show retains old observations with SOURCE_CHANGED_RETEST_NEEDED; create
a new preflight session for the new revision, preserving the SAME customer root.

## Stop and preserve on a hold

If startup or shutdown says BLOCKED/SHUTDOWN HELD, stop the acceptance sequence
and record BLOCKED for the relevant case. Preserve keys, original roots, DB/WAL/
SHM, proof, photos, print jobs and worker witnesses. Do not force-kill a live
worker, delete a root, edit payment state or resend uncertain paper. Unknown
payment/output still needs its original reconciliation/operational handling.

Power loss, pre-ACK/orphan restart, forced printer/network failures and automatic
refund are NOT ready for deliberate owner fault acceptance in this candidate.
Their tests stay BLOCKED/NOT_RUN until C2c3/C3/remedy/account gates are completed.
This worksheet does not replace the original112 PP/26 PILOT acceptance ledger,
relabel old observations or grant production/real-money/deployment approval.

## Simulator handoff contract BEFORE source

Read-only public inspection on10 November confirms the existing official URL
from tools/run_qris_sandbox.py (`https://simulator.sandbox.midtrans.com/v2/qris/index`)
returns a QR Code Image Url input and Scan QR action. No merchant/account data
or payment submission was sent. The original protected GUI displays QR pixels,
but normal owned UAT also needs that current image URL for the official simulator.

Add an explicit acceptance-session-only F8 clipboard handoff, validated against
the SAME original owner/settings/source/scope before native startup. Bind only
to the original accepted ProtectedVisitsApp; pass no manager/config/key/provider
into GUI. Read only the current accepted, visible, active original payment view,
with matching original lease/group/generation, pending Sandbox status and the
existing strict sandbox_qr_url validator. Never copy a CCP/ticket, old/hidden/
retired view, non-Sandbox/foreign URL or select another provider order.

F8 is an explicit local owner action, not an automatic clipboard overwrite.
No URL goes to stdout/log/report; clipboard data remains local and is cleared
on close only if it still contains this bridge's value. Do not erase a later
owner-copied private proof. No DB/network call on GUI thread, payment mutation,
fake PAID control or authority flag. Original official simulator and independent
GET still determine settlement. Original launcher without the acceptance-session
argument remains unchanged. Test fake OS clipboard/external provider transport
only in fixtures, plus genuine original native freeze/CCP/pending journey.

### Simulator handoff implementation checkpoint

Owned acceptance Run now privately passes the validated session to the SAME
original protected entry. It revalidates under its actual pre-start global owner
without a nested lock. Only that session installs the F8 bridge on the original
accepted ProtectedVisitsApp. It uses the existing strict sandbox_qr_url policy,
current original service/payment object, same public binding and privacy epoch.
No database/network/worker-key/config/provider operation runs on the GUI thread.
Late privacy after clipboard copy clears only that still-owned value; clipboard
close preserves later owner-copied text. Console output is static status only.

31 acceptance/settings/original-entry tests PASS1.491s;2 actual-native original
Windows-factory/handoff tests PASS29.221s, zero failures/errors/skips. New native
case exercises genuine original freeze/CCP/pending response, F8, foreign URL/
hidden view/late privacy refusal, no charge/entitlement/paper mutation from copy,
then independent GET settlement and original automatic2+1 delivery. External
clipboard/provider effects are fake in tests ONLY. First native probe ERROR
5.719s because its zero-output fixture counter file did not yet exist; corrected
fixture asserts absence before first send, without weakening production guards.
Corrected isolated case PASS16.631s.

Prior sourcebd763a4 full local980 backend PASS464.250s,100 native PASS318.983s,
34 Apps Script PASS. CI42830743614 ALL FOUR SUCCESS, all completed logs inspected:
Windows457 PASS483.007s +523 PASS734.501s=980, Ubuntu980 PASS363.059s, native100
PASS301.921s. Actual Windows PowerShell passive preflight/record/show, current-
account DPAPI and missing-consent hold succeeded; no physical/account PASS claim.
This is prior pre-F8 verification, not final simulator-handoff source evidence.
Final source now expects982 complete backend and101 native; full checks pending.

## Full local checkpoint — sourcef4b8c07

982 complete local backend PASS453.586s,101 actual-X11 native PASS322.262s,34
offline Apps Script PASS. Zero failures/errors/skips. CI42835198124 Windows
core459 PASS506.754s, Ubuntu982 PASS522.296s, native101 PASS315.239s; completed
logs inspected, all15 new backend methods and the native original F8 case
explicitly observed. Windows delivery129895436413 remains PENDING at this
checkpoint. FIRST inspect its completed log and actual PowerShell step; do not
claim all-four PASS yet or rerun the passing baseline for documentation.

[Machine-readable source/failure/verification evidence](evidence/pp06-owned-windows-acceptance-2026-11-10.json).
Original software source hashes unchanged after final local functional tests.
No source/test WIP or active local app/backend/test; private raw logs, venv/cache
and lab Xvfb remain local artifacts. Old superseded privacy stash must not apply.
This is a candidate to BEGIN owned NORMAL-flow Sandbox acceptance after original
guards pass, not an executed owner result or commercial/fault/recovery approval.
