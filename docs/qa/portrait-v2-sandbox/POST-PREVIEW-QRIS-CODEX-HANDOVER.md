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

## Planned code stages (all NOT_STARTED; future separate authorization required)

| Stage | Deliverable | Exit evidence |
| --- | --- | --- |
| PP-00 | Detailed source/contract audit, versioning schema and failure-first tests | All older AR/UAH assertions preserved |
| PP-01 | Unpaid private draft/capture/retake durability and fence | PP-001–010, PP-059–061 |
| PP-02 | Multi-design final preview/edit/freeze, two-stage readiness | PP-011–020 |
| PP-03 | Logical checkout, CCP, same-group QR1/2/3 and abandonment/late-paid | PP-021–040 |
| PP-04 | Protected credential vault, original post-PAID Recovery Ticket/fallback | PP-041–046 plus OS-specific review |
| PP-05 | Paid exact draft binding, valid Drive URL gate, print jobs/partial uncertainty | PP-047–058 |
| PP-06 | Safe auto-isolation, returning claimant, reboot and legacy PAID capture | PP-059–072 plus relevant UAH |
| PP-07 | Full native/Windows/Ubuntu/POS80/official Midtrans/Drive/escrow/security acceptance | All new PP and external gates; AR-13 remains conditional until separate release |

## Implementation discipline
No code changes in the present documentation delivery. Before later code, verify current branch HEAD and local modifications, review all linked authoritative docs, add failing regression tests for chosen scope, implement minimal isolated features with exact version guard, run focused and full relevant tests, then update docs with source SHA/CI/device limits in each microcommit. Push only to this existing branch. Never merge/master/default branch, change merchant production or webhook, execute real charge/refund, delete cloud photos, alter existing customer media, migrate prior paid records, or inspect `old` without explicit permission.

## Details for QA/UX follow-up
CCP must be an independently distinguishable QR/code on the checkout screen, not the payment QR or post-PAID Recovery Ticket. No proof presentation after A has departed; record evidence of genuine offer, keep OWED for never-offered cases. Idle thresholds are pilot recommendations only (gallery 60–90s, capture/review ~120s, final preview 90–120s). Drive URL must be verified before paid strip regardless of upload completion; no fake QR. Secure vault implementation candidates (Windows DPAPI, Ubuntu TPM/secret service, Android Keystore) need real supported-device evaluation, expiry/key loss tests, and least-privilege authorization; don't claim platform acceptance from synthetic tests. Future stable Meong resolver URL is out of MVP.

**STATUS:** Design owner-approved; all 72 new tests NOT_RUN; source unchanged; prior AR/UAH historical test evidence remains as recorded.