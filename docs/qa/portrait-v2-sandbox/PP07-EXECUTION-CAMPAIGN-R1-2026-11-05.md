# PP-07 execution campaign R1 — 5 November 2026

**IN PROGRESS.** Authorized branch: `feature/post-preview-qris-checkout`.
Remote baseline independently verified as `291d5227f1bc7bc050cd0ad1028c3af1b2d1c8ca`.
The unrelated clean `/workspace/PhotoBooth` checkout remains on `work` at
`27f3801b235d81dc0a49ab201f3e143b62314413`. A separate existing-branch clone
excludes `old` before checkout. No reset, merge, branch creation or deployment.

[Execution evidence](evidence/pp07-execution-r1-2026-11-05.json) and
[versioned 188-case register](evidence/pp07-execution-register-r1-2026-11-05.csv)
preserve the original blank/historical register. All full acceptance outcomes
remain NOT_RUN/BLOCKED. Four newly mapped IDs have **partial** software evidence;
14 AR gates retain their actual original definitions, with no blanket PASS.

## Increment A — BUG-043: clipped private proof incorrectly counted as offered

The native visibility callback checked window bounds and ancestor opacity,
but ignored stencil clipping (including ScrollView viewports). A card entirely
inside the window, with valid textures and opacity, could have its QR/full code
clipped and still record `CCP_OFFERED` or `TICKET_QR_VISIBLE` in the real ledger.
This violated the genuine-opportunity requirement and could authorize checkout
without a usable CCP. The defect is reproduced in native synthetic fixtures;
no owner layout failure or actual customer loss is asserted.

The shared original card now checks every stencil ancestor before acknowledging
visibility. It reuses the existing code/QR checks, callback and original ledger;
no new credential, financial authority, timeout or refund is introduced.

Three new connected regressions observe actual native callbacks and journals:

- Clipped CCP leaves `offered_at` empty and produces zero offer events/charges;
  exposing the complete card later permits exactly one original charge.
- Clipped paid ticket retains NOT_OFFERED, no receipt send and original OWED.
- An explicitly injected historical/out-of-band receipt SUBMITTED without any
  rendered ticket does not create screen-offer evidence or discharge OWED.
  Unclipping permits its first lawful screen without resending the receipt.
  Current sender already refuses this out-of-order ACK path; the injection is
  an abnormal-state fixture, not a claimed reachable transport reproduction.

Two original regressions initially **FAIL** (2 run, zero errors/skips, 2.023s).
After repair, the affected native/payment/ticket/classifier scope runs
**68 PASS**, zero failures/errors/skips, 31.265s. Three new methods are distinct
from 68 executions, which include existing imported fixture tests. Partial
mapping: PP-033/040/087/088. PP-040/087 currently gain prevention evidence;
connected late-PAID/remedy classification remains unfinished. No full row PASS.

Test source is baseline plus the exact source/test digests in the evidence JSON;
the commit containing this increment identifies the resulting source. Final
source-matched full regression and CI remain required after runtime work.

```text
python tools/run_kiosk_unittests.py test_ccp_view test_post_preview_ticket_view test_post_preview_checkout_ticket test_post_preview_payments test_post_preview_refund_assessment
```

Environment: fresh task-only Python 3.12.14 venv, Debian 13, Kivy 2.3.1,
SDL offscreen/Mesa software GL, dummy audio. Initial network-restricted shell
runs stalled without a summary and were terminated; no PASS is assigned.
Network-enabled execution resolved the in-process HTTP fixture operations.
TLS/proxy and all application delivery guards remain enabled. Raw logs remain
in task scratch; only redacted observations and checksums are committed.

## Increment B — connected never-offered PAID remedy assessment

Increment A pushed and remote-verified at `808a8dc28ce8907a277f21902b4e5031186bd3f2`.
The existing pure refund classifier lacked an original-journal offer integration.
`assess_proof_loss_from_journal` now reads original purchase/merchant/amount,
exact verified settled attempts, CCP offer event and ticket presentation/dismissal
events in one transaction. It does not read secrets/ciphertext or mutate rows.
It only narrows the nonbinding classifier; no endpoint, financial transport,
protected-media access or occupancy change is enabled.

Absent/incomplete genuine offer evidence yields `PAID_OWED_REMEDY`. A receipt
SUBMITTED never supplies screen evidence. The first visible frame alone does
not finish the mandatory opportunity: the original trusted dismissal journal
must also exist before the narrow lost-proof-only label can apply. Independent
merchant failure/financial conflicts still require review (BUG-042 preserved).
Old revoked/expired proof can still have been genuinely offered; this historical
offer assessment does not make the old proof valid for any future access.

Six new connected tests plus the payment/ticket/claim/classifier regression:
**80 PASS**, zero failures/errors/skips, 42.210s. A preliminary version also ran
80 PASS/29.269s; the final version adds the completed-dismissal guard before
delivery. These are overlapping runs, not 160 distinct cases.

The late-PAID case explicitly provisions an abnormal pre-existing UNKNOWN
attempt *without ever recording a CCP offer*, then uses real coordinator
reconciliation against the fake provider's settlement. It preserves one original
attempt/entitlement and OWED. Today's normal create guard already prevents this
state; no production escape or real provider settlement is claimed. The second
abnormal-state case injects an independent receipt ACK with no screen render.
Other tests retain actual original events, isolate missing-event corruption,
reject foreign finance facts and preserve independent merchant-failure review.
Partial mapping: PP-040/085/086/087/088/089. Full acceptance stays NOT_RUN.

```text
python tools/run_kiosk_unittests.py test_post_preview_refund_assessment test_post_preview_payments test_post_preview_ticket test_post_preview_claim
```

The versioned CSV is normalized to LF after the initial CSV writer used CRLF;
there is no change to original historical rows or acceptance criteria.

## Increment C — independent-process isolation fault barriers

Increment B pushed and remote-verified at `07b8664b91443f37fbc6f72db88247e2d94c11bd`.
Four new tests reuse the original process-death fixture and actually terminate
the worker with `os._exit(73)`, then inspect original SQLite in another process:

- Death after committed PREPARE retains PREPARED, OWED and blocked local B admission.
- Death after ACK commit/before reply retains one ACKED identity/event, increments
  the original generation once and permits a distinct local B draft.
- A printer lane becoming busy after PREPARE prevents ACK and B admission.
- Failure writing the archive event inside the ACK transaction rolls back its
  close/generation mutation; after hard exit, PREPARED/OWED and blocked B remain.

Affected process/isolation scope: **26 PASS**, zero failures/errors/skips,
23.818s. Four new methods are distinct from 26 overlapping executions.
Partial mapping: PP-064/071/077 and UAH-019/021/022. The UAH-022 sub-scope is
transaction rollback; this is **not** an injected real archive fsync failure.
No protected key is recreated, restored or persisted by the independent reader.
It checks local ledger admission only, not original-worker restoration, full
backend PREPARE/local-receipt/ACK/archive protocol or a new payable B checkout.
Those implementation and target-OS dependencies remain explicit.

```text
python tools/run_kiosk_unittests.py test_post_preview_process_crash test_post_preview_isolation
```

## Remaining execution and external gates

Next: independent-process crash/handoff barriers; virtual receipt/strip/Drive races; final native complete
journeys and actual-monotonic ticket replay; one complete appropriate regression
and exact-source Windows/Ubuntu/native CI. Continue software work before asking
the owner to test. Historical acbac15 results remain historical.

Full protected original-worker restoration is not implemented; Windows DPAPI
byte tests alone do not supply it, and the Ubuntu protector remains unsupported.
Actual merchant profile/credentials/account evidence, POS80 paper, webcam/touch/
speaker, cloud ACL/retention and security/finance/legal review remain separate.
PP-101/104–110/112 still lack their required implementation/external scope;
classifier candidates are not refunds. Refund and production stay disabled.

Owner PILOT remains 24 NOT_RUN / 2 BLOCKED. The supervised synthetic worksheet
remains conditional on its actual device preflight; this in-progress campaign
does not request owner testing or declare final readiness at the new source.
