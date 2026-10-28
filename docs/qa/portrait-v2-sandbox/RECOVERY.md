# Sandbox session recovery

## Approved scope and review — 28 October 2026 (Asia/Jakarta)

The owner reports **PERLU BANTUAN OPERATOR** after closing and reopening the
application. The screenshot proves a RECOVERY page; the exact laptop HEAD and
interrupted capture step were not supplied. The owner then approves implementing
the discussed recovery controls and closing their identified failure windows.
This work is **Sandbox only**, on the existing
`feature/portrait-kiosk-v2-next` branch. Base local/remote source is
`89ea893463062d7a6383da6057ed106f889df55c`; the QRIS reference was refreshed
read-only at `3cc8a8e360e8c2100a3077b755664eb61d0216ea`.

This is a bounded addition to FEAT-020/FEAT-022, related to FEAT-007 recovery.
It does not enable production fulfillment, paid reprints, refunds, automatic
restart, printer/Drive transports, service installation, a new branch or a
merge/release. The dedicated merchant trial continues to force printer/Drive
off. Existing ordinary/MOCK flows and previously saved customer data are not
migrated or cleared.

Before implementation, reviewed AGENTS, the documentation index, protocol,
handover, architecture, technical design, decisions, feature status, bug register,
backlog and v2 specification, plus the existing Sandbox, P3 and FEAT-009 recovery
records. Followed the current copy-link and outstanding-acceptance guidance.
Older statements that RECOVERY has no resolution controls describe their dated
source; this approval adds scoped operator-controlled Sandbox resolution. The
read-only watchdog review remains an observation, not fulfillment authority.

## Bounded implementation plan — recorded before delivery

Reuse `KioskCheckout`, the authenticated backend/store/client, `PhotoTest`,
`TransactionStore`, native v2 widgets and their existing single-flight workers.
Extend those seams rather than creating a second payment or photo engine.
Changes cover the Sandbox launcher/operator credential, backend recovery API,
durable visit recovery state, exact local photo identity and native presentation.

1. Preserve the recovery reason and interrupted phase. Reconciliation must
   query the backend and obtain current provider evidence rather than returning
   the old RECOVERY snapshot or assuming a cached PAID status is fresh.
2. Require booth authentication plus a separate operator credential for recovery
   decisions. The planned launcher generates an eight-digit operator PIN for
   that local launch, prints it locally and passes it only to the backend child.
   The GUI accepts explicit entry; it does not inherit the PIN. Wrong attempts
   are bounded. Secrets never enter command arguments, journals or reports.
3. Inspect metadata before showing any old photo. Match the same merchant/booth,
   checkout key, order, grant and local transaction. No "latest folder" guess,
   cross-booth substitution or new transaction to replace an uncertain one.
4. Validate files against the manifest before restoring the same photo session:
   selected designs/copies, originals, current design, chosen retake and consumed
   retake quota. Missing, malformed, linked or ambiguous file/progress state
   stays held. Preserve files; never silently overwrite an orphan photo.
5. Continue only after explicit operator authorization and the backend's valid
   grant/service acknowledgment. Returning to capture always requires a fresh
   manual countdown; review/result may reuse validated saved outputs. Local
   composition and backend service completion remain separate checkpoints.
6. Supply a distinct audited **end Sandbox test** operation. It closes the test
   visit on the backend while preserving the real payment status, journal,
   grants and photo files; it must not manufacture PAID/COMPLETED, refund or
   erase a visit. Only after confirmed closure may the same booth begin a new
   test order. A late payment remains associated with the original order.
7. Persist recovery action identity and decisions before navigation. Duplicate
   taps, lost replies and a further restart repeat the same operation/result.
   Keep page revisions, worker busy gates and existing process/journal leases.

## Recovery decisions

| Evidence | Allowed direction |
| --- | --- |
| Current order remains unpaid and valid | Keep the same checkout/QR and ordinary status/cancel path |
| Verified paid permit, capture not allocated | Return to explicit photo consent using the existing permit |
| Same allocated session, validated incomplete originals | Resume that session after operator authorization; manual countdown only |
| Validated review/result files | Open that saved phase after authorization, preserving retake quota |
| Local photos complete, backend completion uncertain | Reconcile/acknowledge the same service; never infer completion from one local flag |
| Refund/review, identity mismatch, missing/ambiguous state or unavailable verification | Keep recovery held with a specific reason; no capture or replacement charge |
| Operator deliberately ends a Sandbox test | Record an audited backend disposition, preserve evidence, then allow a fresh visit |

Exact action labels, API fields and result evidence will be synchronized with
the implemented source. This pre-delivery plan is not a claim that a path or
verification result already exists.

Legacy sessions without a durable checkout-to-photo binding cannot be repaired
by selecting the newest folder. Keep those ambiguous sessions held; a deliberate
audited Sandbox disposition may end the test without deleting its evidence.
Existing retention deadlines are not extended by reopening or recovery.

## Verification and device acceptance

Use temporary profiles and synthetic photos/provider responses for source QA.
Exercise the following acceptance cases without a real charge, print or upload:

- Recovery inspection performs a real backend/provider reconciliation; stale,
  refunded, wrong-booth and unknown evidence cannot grant a resumed session.
- Bad/missing operator PIN and repeated wrong attempts cannot resolve a visit;
  PINs do not enter the GUI environment, journals, logs or evidence artifacts.
- Restart before allocation, after allocation/before binding, and after STARTED
  reuses the same identities or remains explicitly held; no duplicate session.
- Restart after one/two/three photos and before/after retake commit preserves
  validated progress/quota. Conflicting files/manifests fail closed unchanged.
- Multi-design recovery preserves completed designs/copies and resumes only the
  unfinished phase. Composition alone cannot silently complete the checkout.
- Lost recovery/completion/end-test replies and repeated taps are idempotent;
  the same booth can create a new visit only after durable audited closure.
- Previous photos remain hidden before authorization; disabled/stale callbacks,
  minimize, resize and close cannot issue a second recovery operation.
- Default/MOCK and production rejection remain tested. Dedicated Sandbox still
  creates no print or Drive jobs, including during recovery.

Run focused domain/HTTP/native checks, one complete regression on the final
functional source and existing push CI. Capture and inspect native recovery
pages at 800×1280 and 452×900. Bind results to exact source hashes/commit and
report PASS/FAIL/SKIP/NOT_RUN separately. Reuse the existing
[combined acceptance form](../portrait-v2-pending-acceptance/windows-checklist.html)
for source/device metadata and merchant/privacy reporting; do not import old
passes into the new recovery cases or impose another unrelated twenty-cycle
gate. Windows development and Ubuntu deployment require their own manual
keyboard/touch/camera/close/reopen checks. Source fixtures do not certify the
owner's merchant account or actual device restart behavior.

At plan time all new verification was NOT_RUN. The first backend increment now
has **128 focused protocol tests PASS**, zero failures/errors/skips (0.906s),
including 16 new operator/API recovery cases. Native integration, final full
regression, screenshots, CI and actual device/provider acceptance remain pending.
The backend route is disabled without its explicit independent operator PIN;
the native launcher/UI integration follows in the next increment.

## Update and rollback

Keep using `python tools/run_portrait_v2_sandbox.py` in the existing Kivy
environment, with keys kept in the current ignored local settings/environment.
Changing booth IDs is a temporary isolated-test workaround, not normal recovery.
Do not erase `visit.json`, edit payment/service states, reset counters, copy
another profile into this one or remove photos to clear a hold.

After reviewing the final source, rollback uses scoped inverse commits on this
same branch. Preserve all existing orders, action audits, grants, journals,
manifests, originals/retakes, outputs and transport state. Database changes must
remain backward-readable or receive explicit rollback instructions; no automatic
data downgrade/deletion, print replay or provider operation is authorized.
