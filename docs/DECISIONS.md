# Meong Photobooth - Owner decision record

## Current scope decision - 2026-10-20

**DEC-021 - FEAT-020 full-auto QRIS audit remediation.** The owner explicitly approved the audit recommendations and asked for execution until the feature can be tried in the main GUI, without repeated continuation requests. Implementation, tests, relevant documentation and sequential small pushes are authorized on **feature/qris-payment only**. The selected merchant model is individual business; the development path is explicit offline mock followed by Midtrans Sandbox verification.

**Not authorized:** merge to master, rewriting v1.0.0, live production payments, public deployment, merchant account actions, cloud deletions or declaring Windows/printer acceptance without physical evidence. These require their own approval and validation. This decision does not approve other backlog features.

This supersedes only the older FEAT-020 scheduling deferral in DEC-006 and related dated statements. It does not change approved pricing, ads/tutorial order, audio ownership, camera mirroring, photo/QR printing requirements, Drive delivery policy or separate branch approvals. Remote provider-QR paper-slip support is an explicitly recorded implementation gap, not cancellation of the original requirement.

All earlier DEC-001 through DEC-020 records are preserved verbatim in [DECISIONS.pre-qris-20261020.md](DECISIONS.pre-qris-20261020.md) and remain binding except where the explicit current scope above supersedes QRIS deferral. They are requirements, not proof of implementation. Current implementation/evidence: [feature status](FEATURE_STATUS.md), [trial](QRIS_TRIAL.md), [tests](test_checklist.md).
