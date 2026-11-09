# Post-preview child host / protected native continuation

9 November 2026. Work ONLY on feature/post-preview-qris-checkout.
Commercial target: Ubuntu mini PC; retain Windows. Production: **NOT_READY**.
This is an implementation checkpoint, not completion of the owner's whole task.

## Exact published source

| Commit | Delivered increment |
| --- | --- |
| ebbad73 | Stable original merchant/booth ledger/media and independent backend kernel ownership |
| 7f612a4 | Credential-isolated child bootstrap, loopback API, original restart and truthful HTTP/worker shutdown |
| 8398b53 | Backend-owned original protected CCP presentation and typed native display client |
| f098c05 | Original readiness collector stop/admission fence, including existing-ACK recovery |
| c096504 | Deterministic native blocked-receipt fixture, strict just-before/exact30s privacy checks |

Latest runtime/test source: **c096504ed87259cd49c5aacd9cab73906a6b5646**;
last production-runtime change f098c05. Each increment committed, pushed to the
same authorized branch and remote-verified. No new branch, force push, merge,
default change, excluded-old inspection or operational journal reset.

## Actual verification and limitations

At f098c05: **672 backend PASS (292.753s), 74 native PASS (210.320s), 34 Apps
Script VM PASS**, zero failures/errors/skips. The original registered workflow
commands were used. Native ran in an actual local Xvfb display with Kivy2.3.1,
software GL and device opt-outs. Official Debian display tools were extracted
under local work/ because this executor has no sudo/package helper; Kivy home
was local. Debian cloud is NOT target Ubuntu mini-PC acceptance.

CI42579045180 at f098c05 completed: Windows672 PASS (765.252s), Ubuntu672 PASS
(231.130s), native74 FAIL (two portrait subtest assertions in ONE clock method,
151.359s). All three logs inspected. Windows actual child/socket/DPAPI and owner
setup/check-only pass; A1's earlier WinError32 fixture cleanup is corrected.
Native failure was a floating-point fixture boundary; production timer unchanged.
Corrected exact method at c096504: **1 PASS /both portrait sizes,6.364s**,
retains card at29.999s and requires wipe at30.000s while receipt is SENDING.

[Current CI42580705346](https://github.com/pratikto/PhotoBooth/actions/runs/42580705346)
at exact c096504 is **COMPLETED SUCCESS in all three jobs**: Windows672 PASS
(648.690s), Ubuntu672 PASS (171.647s), native74 PASS (149.791s), each zero
failures/errors/skips. All three completed logs inspected; Windows/Linux owner
check-only and original native screenshot steps succeeded. This does not prove
physical paper, Drive ACL, merchant or target mini-PC acceptance. Documentation
HEAD is later; runtime/test hashes are unchanged. No unchanged local rerun.
[Source hashes, commands and exact status](provider-bootstrap-2026-11-09/final-verification.json).

Focused scopes overlap, not acceptance percentages: A1 96, A2 105, B1 88,
collector69 PASS. A retrospective two-method collector run against prior8398b53
failed both assertions as expected (zero errors); current regression passes.
Provider/Drive/Linux key lookup in child tests are explicitly synthetic. Actual
Linux custody primitive/daemon restart evidence from a748db2 is retained; no
claim of new actual Ubuntu login/reboot/keyring/merchant/device acceptance.

## Finite status

| State | Concrete scope |
| --- | --- |
| DONE for declared software scope | Stable original host ownership; credential isolation/private socket transfer; actual child/API/client original settlement/restart/lost POST response; no force-kill on stop=False; backend CCP original ciphertext/offer/visible/retire; typed renderer offer adapter; collector lifetime fence in original isolation/admission |
| NOT CONNECTED | Full protected native provider facade/profile; Recovery Ticket screen/one physical receipt and purchased Drive/strip/upload/claim/release over genuine backend authority; real refund/status and final operating package |
| NOT VERIFIED | Complete supported Ubuntu worker/restore startup, login/PAM/protected unlock, cold boot/reboot/encrypted custody backup; actual camera/touch/audio/POS80/cutter/Drive ACL/retention; full PP/UAH acceptance; completed final-source2h simulation and separate4h device qualification |
| EXTERNAL ACCESS ABSENT | No merchant/Drive secret bindings, configured owned printer route or mini-PC devices in this executor; merchant QRIS/refund capability/legal approval and production authorization remain separate |

The NOT CONNECTED rows are source work, NOT hardware blockers. The owner launcher
and PrivateCheckoutService/OriginalMockClaim/Isolation/PilotAdmission retain their
mock-only guards. No new merchant launch command is exposed. Backend health still
says fulfillment_enabled=False. Eleven prior owner-reported checks are preserved;
do not ask for an unchanged full retest. Prior R4 1,848.279s is only an interim
record; its process/root is absent here, not a finished2h qualification.

## Exact next source action

1. Current c096504 CI is fully verified; do not rerun that successful baseline.
   Continue the first unfinished native protected ticket increment below.
2. Extend original backend protected presentation to OriginalRecoveryTicketService
   using the SAME actual PostPreviewPayments/protector/ledger. Add authenticated
   original-owner scoped offer/visible/dismiss/retire and connect the existing
   native PrivateRecoveryTicketCard/VisibleTicketWindow. Do not construct a dummy
   provider in the GUI or relax PrivateCheckoutService's mock constructor.
3. Wire original exactly-once receipt and paid Drive/strip/upload authority over
   the same protected backend/native worker seam. Preserve original SENDING
   before I/O, exclusive receipt/strip lane,30 genuinely visible seconds/NEXT,
   individual verified Drive URL, exact approved bytes/copies and automatic
   purchased strips. Keep the profile disabled until the whole paid path is safe.
4. Bind the exact original readiness collector into that native profile's release
   coordinator. stop=False must hold PREPARE/ACK/reset/claim and retain ownership.
   A stopped capability cannot restart; a new visit needs a fresh private bridge.
   Verify stale callbacks/generations, WAIT while busy and original fresh PAID
   proof recovery, including late/duplicate settlement and crash outcomes.
5. Complete actual refund/status/source operating package, supported Ubuntu
   restore and secure configuration; then final measured2h software campaign,
   followed separately by actual account/device4h acceptance and final approval.

Review the relevant original contracts/source before each increment, reuse
working UI/renderers/services first, focus-test and push safe stages immediately.
Do not rerun a748db2 baseline or completed native A→B→A merely for onboarding.
Start with this next unfinished source action, not another general audit.

## Resources, rollback and cross-account handoff

No local test/qualification/backend/keyring process is active at this checkpoint.
CI above is remote and has completed successfully. Local untracked work/ includes synthetic
logs/drivers, Debian display packages/Kivy cache and earlier lab artifacts; none
is backed up through GitHub. No safely completed runtime source remains unpushed.
A different executor must reconstruct its own test tools; do not assume local
processes, fixture roots or mounted OS custody move with the account.

No actual charge/refund/paper/cloud publication/deletion/deployment occurred.
Rollback only scoped inverse source commits after review. Preserve original
ledger/WAL/SHM, host context, keyring/ciphertext, approved media, PAID/OWED,
SENDING/UNCERTAIN, Drive binding and print journals. Do not create replacement
roots/keys/proofs, replay uncertain output or cross-migrate DPAPI to Ubuntu.

Detailed reports: [host/bootstrap](PP04-CHILD-BACKEND-BOOTSTRAP-2026-11-09.md),
[protected CCP](PP04-PROTECTED-PRESENTATION-2026-11-09.md),
[collector fence](PP06-READINESS-COLLECTOR-FENCE-2026-11-09.md),
[countdown fixture/full regression](PP07-COUNTDOWN-FIXTURE-2026-11-09.md),
[prior Ubuntu custody](PP03-UBUNTU-VAULT-2026-11-09.md),
[approved customer flowchart](POST-PREVIEW-QRIS-OWNER-APPROVED.md),
[security contract](POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md),
[commercial completion gates](PRODUCT-READINESS-STAR.md).
