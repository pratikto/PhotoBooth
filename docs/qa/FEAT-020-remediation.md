# FEAT-020 audit remediation - 2026-10-20

Owner approval: implement the reviewed audit recommendations on `feature/qris-payment`, with small sequential pushes. No merge, release, production payment or public deployment is authorized. Baseline: `4b35735d27f850413a5e479a8ddf119877aa6c1c`.

## Step 1 - executable backend quality gate

The previous run 39351919821 stopped at an unrelated printer test import (`cv2` missing); later backend suites did not execute. The backend job now names every required backend test module, includes the missing `requests` dependency, rejects skipped mandatory tests, and preserves the tested commit, dependency versions, complete report and tracked-source snapshot as a seven-day CI artifact. QR printing and Kivy/hardware remain separate regression gates; they are not declared passed by this backend job.

Validation before push: YAML parsed locally and the explicit module list checked against the audit's known test modules. Actual CI execution/result must be recorded after the push; no successful run is claimed here.

## Approved remaining sequence

1. Verify the backend gate and add failing regression cases for the audit findings.
2. Durable checkout idempotency, recoverable session grants, lifecycle/expiry, provider reconciliation and late-payment isolation.
3. Strict HTTP validation, bounded streaming, off-thread provider calls, event evidence and safe error handling.
4. Integrate an explicitly labelled Sandbox GUI flow, preserve DEMO/ads/Drive QR/photo behavior and validate failure paths.
5. Run integration and applicable GUI regression; merchant Sandbox and physical Windows tests require real evidence.

Historical isolated PASS claims without execution evidence are not acceptance criteria. The source remains a Sandbox prototype until the above gates are evidenced. Rollback is a reviewed revert of scoped feature-branch commits, never a reset or modification of `master` or `v1.0.0`.
