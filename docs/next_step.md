# Meong Photobooth - Unified feature execution board

## Current approved scope, 2026-10-20

Stable IDs are unchanged. The owner's explicit FEAT-020 approval supersedes its earlier P3 scheduling deferral. This branch records that scope and its dependencies; it does not revoke approvals or overwrite work in other branches. **No master merge or production payment release is approved.**

The complete previous intake, dependency, risk, compatibility and parking-lot details are preserved verbatim in [next_step.pre-qris-20261020.md](next_step.pre-qris-20261020.md). That is a dated requirements archive, not a second active execution queue. The board below is the current ordering for this record. Each future task still needs a fresh branch/source review before execution.

| Order / stream | ID | Current scope, readiness and boundary |
| --- | --- | --- |
| Safety gate before release | BUG-001/007, BUG-009, monitored BUG-011 | Existing audio/Drive retention and physical fulfillment evidence remain independent. QRIS mock tests do not close these defects. |
| Current owner-selected work | FEAT-020 | **APPROVED; main-GUI mock trial implemented and synthetic QA verified.** Next: owner Windows trial and real merchant Sandbox acceptance. Provider reconciliation, minimum payment recovery and scoped booth authentication were prerequisites within this approval. |
| FEAT-020 production gate | FEAT-007 (limited dependency) | Stable visit/grant and conservative interrupted-session hold implemented for this QRIS scope. Full operator recovery/refund tooling, actual print fulfillment accounting and broader paid recovery remain incomplete; no unrestricted FEAT-007 release approval. |
| Independent device stream | FEAT-008 | Device-health work and its separate approval remain untouched. Do not merge or change feature/device-health as part of QRIS. |
| Next reliability candidate | FEAT-009 | Windows startup/watchdog recovery; review device-health dependencies and obtain scope approval. |
| Following reliability candidates | FEAT-012, FEAT-010 | Structured diagnostics and per-machine configuration. QRIS auth/events are limited prerequisites, not complete remote configuration or a fleet diagnostics delivery. |
| Media/retention stream | FEAT-004 + BUG-009 | Offline-first Drive ad sync and separately verified photo cleanup; keep cloud deletion/deployment approval separate. |
| Presentation candidates | FEAT-006, FEAT-014, FEAT-017 | Themes, branded frames and event media; no new pricing or payment bundles implied. |
| Accepted core; regression only | FEAT-001, FEAT-003, FEAT-011 | Existing template/copy pricing, camera mirror and Floyd/dither work retain owner-reported acceptance and its limits. Do not unnecessarily rewrite the stable photo/print path. |
| After proven fleet need | FEAT-018 | Fleet monitoring; requires device identity/health/diagnostics and real operational need. |
| Deferred promotions | FEAT-002A, FEAT-005A, FEAT-013 | Demo receipts/order handoff and promotion reporting; QRIS approval does not approve these features. |
| Deferred paid extensions | FEAT-016, FEAT-015 | Paid reprints and digital upsells need their own transaction/delivery/consent scope and evidence. |
| Research only | BIZ-001 / FEAT-019 | Hardware/subscription/ad-slot business model; no billing, licensing enforcement or collections implementation approved. |
| Blocked on real partners | FEAT-002B, FEAT-005B | Real POS/receipt/ordering integration requires partner agreements and actual API evidence. |

### FEAT-020 remaining gate order

1. Run the main-GUI mock trial on the owner's Windows booth and record the exact tested SHA/device behavior. Printing is opt-in.
2. Verify actual Midtrans Sandbox merchant responses, simulator payment, phone QR scan, polling and HTTPS webhook behavior; credentials remain server-side.
3. Complete provider QR-slip printing and a supported operator partial-session recovery/refund procedure before claiming unattended commercial readiness.
4. Verify ingress/security/monitoring/backups, resolve or risk-accept independent blockers, and request explicit release/merge approval. There is no automatic production rollout.

[Trial instructions](QRIS_TRIAL.md) / [evidence](test_checklist.md) / [current owner decision](DECISIONS.md). Submission order does not determine priority; re-rank when genuine new evidence or owner priorities change.
