# Codex handover — owner-approved post-preview QRIS

**Date:** 1 November 2026. **Branch:** `feature/post-preview-qris-checkout`; branched from `feature/portrait-kiosk-v2-next` at `97a6c1574f0692d8a3db8b3a4d94778f87937e18`. **Documentation-only approval: NO CODE / SCHEMA / TEST IMPLEMENTATION YET.** Read [main owner decision, 24 approved rules and 11 diagrams](POST-PREVIEW-QRIS-OWNER-APPROVED.md) → [state/security contract](POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md) → [72 NOT_RUN acceptance cases](POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md) → root AGENTS.md, docs/DEVELOPMENT_PROTOCOL.md, docs/DECISIONS.md, docs/FEATURE_STATUS.md, docs/next_step.md, docs/DEVELOPMENT_HANDOVER.md and original AR/UAH/BUG evidence.

## Contract and precedence
New order flow: **select designs/copies → each design 3 photos + one retake maximum → approve all previews → final edit only before QRIS → freeze original quote/artifacts → one logical checkout and original pre-PAID Checkout Claim Proof → QRIS1/2/3 only for verified unpaid expiry while active → provider-verified PAID → original Recovery Ticket once (30s screen fallback on receipt uncertainty) → verified Drive customer URL → exact paid paper strips and background upload → safe completion.** Versioned legacy PAID-before-photo orders remain on original recovery; do not remove historical capture PAID checks globally.

Owner agreed: secure CCP before settlement for returning late-paid customers, encrypted scoped credential escrow, verified URL required for final strip in MVP, adaptive genuine-inactivity warnings without interrupting active photo work, edit-before-QRIS with consumed retake preserved. Keep unrelated original rules: unattended automatic isolation only if verified safe, user responsibility if genuinely offered original proof was lost, no new visitor takeover of paid/unknown booth, no print UNCERTAIN replay, no auto refund, AR-00..13 safety highest priority.

## Actual source seams to inspect when explicitly authorized to code

| Module | Gap to close |
| --- | --- |
| photobooth/kiosk_v2/flow.py | Add new versioned unpaid draft/final-preview/checkout navigation and inactivity policy |
| photobooth/kiosk_v2/photos.py | Durable prepayment private photo staging, retake ancestry, separate compose versus paid completion, no public Drive before PAID |
| photobooth/kiosk_v2/photo_views.py | Prevent existing compose-triggered photo auto-print on unpaid draft, gated QR visibility |
| photobooth/kiosk_v2/sandbox_views.py | QRIS after all approved preview, separate current vs late claim, old legacy route intact |
| photobooth/kiosk_v2/sandbox_checkout.py / photobooth/qris_session.py | One logical purchase, original CCP, QRIS attempt journal, active QR renewals vs abandoned cancellations |
| photobooth/checkout_backend.py / checkout_store.py | Frozen original draft/payment binding, immutable group, single grant/OWED, fresh provider evidence and idempotent attempts |
| photobooth/payment_quote.py / fulfillment_contract.py | Server quote and exact artifact digest/retake/copy/version; reconcile native max nine copies vs backend max ten |
| Original checkout_release / isolation workers | Exact fence, local receipt, backend ACK/archive, protected Ads and same original claim |
| Original printer and recovery_receipt | Ticket-vs-photo job ownership, once send, uncertain print quarantine, 30s original screen fallback |
| Original booth_storage / booth_sync / Drive | No anonymous reserve consumption or public unpaid photo, verified URL paid binding/upload checksum |
| New OS-specific protected vault | Original encrypted CCP/ticket, proof-gated retrieval, no boot display and no plaintext secret sidecar |

## Planned code stages (all NOT_STARTED; requires separately authorized implementation)

**Branch-specific execution priority:** on `feature/post-preview-qris-checkout`, PP-00..PP-07 is the planned development workstream. **AR-00–13/UAH financial, privacy, provider, ticket, release and legacy-prepaid safeguards remain higher-priority nonnegotiable dependency/regression gates**, not a competing instruction to resume and push arbitrary old AR steps to the parent branch. On `feature/portrait-kiosk-v2-next`, the original owner AR order remains authoritative. Never treat the latest dated docs banner as authorization to edit source.

| Stage | Deliverable | Unit / integration exit evidence |
| --- | --- | --- |
| PP-00 | Read latest source and original AR/UAH/UX07/Midtrans/Drive contracts; verify provider retry/idempotency uncertainty, create versioned draft/payment/occupancy model | Freeze architecture and failing synthetic tests, historical evidence unchanged |
| PP-01 | Private unpaid 3+1/template draft, durable retake/edit lineage, camera/privacy worker fencing | PP-001..010 and isolated PP-059..061/063/069; zero public media or photo print |
| PP-02 | Multi-template final preview/edit, frozen pre-create revision/quote, two-stage readiness incl nonconsuming READY observation | PP-011..020, PP-081 target unit fixtures |
| PP-03 | **Credential-vault interface, original CCP issuance/presentation/verifier, crash/expiry/rate-limit model and isolated synthetic fixture** BEFORE accepting claims | PP-033..034, PP-038..040, PP-043..046 (unit-only; no payment-claim acceptance yet) |
| PP-04 | One logical purchase, immutable CREATE_PREPARED, exact same-order provider reconciliation; QR1/2/3 **expiry only**; USER_CANCEL vs suspend/abandon, duplicate PAID and guarded claim/payment mapping | PP-021..032 + PP-073..076/083; live cross-component claim still NOT_RUN |
| PP-05 | PAID->same draft grant/OWED, original post-PAID receipt once + 30s fallback, unique verified Drive folder, paid print journal + background upload | PP-041..058, PP-077..081 when dependencies exist; no UNCERTAIN replay |
| PP-06 | End-to-end **original** CCP/ticket claim, PAID_UNCLAIMED, free-booth wait/defer, safe machine PREPARE/fence/ACK/archive, reboot and legacy prepaid compatibility | PP-033..046 and PP-059..072 + PP-077..080/084 integrated; full legacy UAH/AR regression |
| PP-07 | Full synthetic faults/CI/native physical acceptance with existing Windows + Ubuntu targets, POS80, configured Midtrans Sandbox, Drive, OS escrow and merchant policy | PP-001..084 actual tracked outcomes; distinct external release gates and AR-13 CONDITIONAL until separately approved |

**Dependency rule:** a PP-03 vault unit test does not mean post-PAID claimant flow is working; a PP-04 simulated settlement does not grant paper/photo access until PP-05; full claimant ownership/release only passes after PP-06. Historical AR/UAH and legacy Sandbox source/CI evidence is not transferable; the current proposed PP matrix has **84 NOT_RUN scenarios**. Treat checkouts with actual Drive OFF as **legacy Sandbox only**; new purchased-flow synthetic tests must use an isolated verified-URL fake (no live publication, no false hardware evidence). Existing server Core QRIS provider idempotency-header support is **unverified**: always preserve original provider order ID and reconcile on timeout/404; never assume a provider retry guarantee from an internal idempotency key.

## Implementation discipline
No code changes in this documentation-only audit/correction. Before any later code, verify the active branch is `feature/post-preview-qris-checkout`, read the canonical 84-case suite and all source/AR/UAH contracts, add focused failing regression tests, implement minimal versioned features without changing legacy grants, run focused and applicable full regressions, then update docs with exact source SHA/CI/device limits per microcommit. Push only to this existing branch. Never merge/master/default branch, change merchant production or webhook, execute real charge/refund, delete cloud photos, alter existing customer media, migrate prior paid records, or inspect `old` without explicit permission.

## Details for QA/UX follow-up
CCP must be an independently distinguishable QR/code on the checkout screen, not the payment QR or post-PAID Recovery Ticket. No proof presentation after A has departed; record evidence of genuine offer, keep OWED for never-offered cases. Idle thresholds are pilot recommendations only (gallery 60–90s, capture/review ~120s, final preview 90–120s). Drive URL must be verified before paid strip regardless of upload completion; no fake QR. Secure vault implementation candidates (Windows DPAPI, Ubuntu TPM/secret service, Android Keystore) need real supported-device evaluation, expiry/key loss tests, and least-privilege authorization; don't claim platform acceptance from synthetic tests. Future stable Meong resolver URL is out of MVP.

**STATUS:** Design owner-approved; all 84 new PP tests NOT_RUN; source unchanged; prior AR/UAH historical evidence remains as recorded.