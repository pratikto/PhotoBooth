# PP-07 execution campaign R1 — 5 November 2026

> **Latest remote R2–R4 supersedes this historical R1 checkpoint.**
> At source 824b6ae, [R4](PP07-SIMULATION-CLOSURE-R4-2026-11-05.md) records
> 1,801 all-opt-in local PASS, zero failure/error/skip, and CI 41960994370
> 3/3 SUCCESS (597 Windows/597 Ubuntu/68 native). R2 separately completed
> exact-source all-model/audio verification; the R1 FAIL/SKIP history below
> is retained without reopening it as a current blocker. Latest mapping is
> 110 partial PP scopes, all full outcomes unchanged. Supervised fresh-root
> [physical trial](PP07-PHYSICAL-QUICK-START.md) can begin after device preflight.
> Two-hour synthetic qualification has only an interim remote record; do not
> infer completion. [Latest verification](evidence/pp07-r4-final-verification-2026-11-05.json).

> **Historical R1 software checkpoint — superseded:** source `3825473`, runtime
> `fec4f7f`. Latest broad run: **1,760 run / 1,756 PASS / 1 FAIL / zero errors /
> three model SKIP**, 1,199.371s. Delivery helper now PASS; native SDL PCM probe
> failed with an empty callback sample. Isolated audio module 2 PASS and three
> further repetitions PASS; broad occurrence remains unexplained and FAIL.
> CI [41930961409](https://github.com/pratikto/PhotoBooth/actions/runs/41930961409)
> **3/3 SUCCESS**, 557 Windows + 557 Ubuntu + 67 native; these registered jobs
> do not include the failing legacy native PCM module. No full local PASS.
> [Current continuation](PP07-R1-CONTINUATION-2026-11-05.md) supersedes older
> RUNNING/pending notes below. No active test job or owner-testing request.

**IN PROGRESS.** Authorized branch: `feature/post-preview-qris-checkout`.
Remote baseline independently verified as `291d5227f1bc7bc050cd0ad1028c3af1b2d1c8ca`.
The unrelated clean `/workspace/PhotoBooth` checkout remains on `work` at
`27f3801b235d81dc0a49ab201f3e143b62314413`. A separate existing-branch clone
excludes `old` before checkout. No reset, merge, branch creation or deployment.

[Execution evidence](evidence/pp07-execution-r1-2026-11-05.json) and
[versioned 188-case register](evidence/pp07-execution-register-r1-2026-11-05.csv)
preserve the original blank/historical register. All full acceptance outcomes
remain NOT_RUN/BLOCKED. Current evidence maps 103 PP IDs and three UAH IDs to **partial** software scope;
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

## Increment D — actual-time replay and environment verification

Increment C pushed and remote-verified at `36ec0cc83f65940bd78e8865c0ded6329a2522e3`.
The inspected, existing timed harness completed **PASS in 96.553s**, using
actual Kivy `App.run()` and monotonic time: eight real five-second countdowns,
six initial captures + two retakes, one Rp25,000 synthetic charge, one receipt,
2+1 virtual strip copies, eight private JPEGs. The original ticket remained
visible **30.002 seconds** before automatic private-card wipe. OWED remained
and `physical_paper_verified=False`. No countdown deadline was advanced or NEXT
forced. The replay started at 07b8664; runtime/CheckoutFixture files are byte
identical in 36ec0cc (C adds only process tests/documentation).

Static pilot preflight reports READY_FOR_SUPERVISED_SYNTHETIC_PILOT at 36ec0cc.
`pip check` has no broken requirements. Original Apps Script syntax and offline
Node VM pass (1 Node test, zero failure/skip); no account/deployment/deletion.
Dependencies are freshly installed, with OpenCV constrained below 5 to match
the existing CI workflow; exact versions are in the execution JSON.

The pinned public MediaPipe model host `storage.googleapis.com` is unavailable:
an ordinary HEAD request through the session proxy receives CONNECT **403**.
No route/proxy/TLS workaround is attempted. The three optional real inference
methods require those model/sample assets and remain explicitly blocked here;
fake inference is not a substitute. GUI/audio/video opt-ins are enabled for
the current full regression. Its result and final source-matched CI are pending,
not inferred from this timed PASS or historical acbac15.

## Increment E — final functional-source CI and second timed layout

**[CI 41920786730](https://github.com/pratikto/PhotoBooth/actions/runs/41920786730)
at 36ec0cc completed 3/3 SUCCESS.** All completed logs independently inspected:
556 Windows PASS (422.000s), 556 Ubuntu PASS (174.551s), 65 native Kivy PASS
(109.763s), each zero failures/errors/skips. These are 1,177 platform executions,
not unique acceptance cases. The nine new connected assessment/native methods
and four process methods are individually present in their applicable logs.
[CI/artifact evidence](evidence/pp07-ci-r1-2026-11-05.json) pins the actual source
and synthetic preview artifact digest; the archive was not downloaded.

The timed harness now accepts `--size 800x1280` (default remains 452x900).
The 800x1280 actual-event-loop replay **PASS in 79.353s**, with **30.008s**
genuine ticket visibility, eight real countdowns, one charge/receipt, 2+1 copies
and unchanged OWED/no physical paper claim. Both requested portrait sizes now
have independent actual-monotonic complete replays. Eight private-preview PNGs
rendered successfully in two fresh processes; the two all-design previews were
visually inspected. No private CCP/paid-ticket screenshot was saved.

[Bounded resource observations](evidence/pp07-resource-r1-2026-11-05.json): five
repetitions of existing J21, **60 synthetic paid visits in 237.048s**, fresh
temporary fixtures with cleanup. Every J21 invariant passes. After GC, threads
stay 1 and open descriptors stay 4; first/last RSS is 201,134,080/202,772,480
bytes, traced Python memory 8,382,805/8,611,310 bytes. No leak-free claim or
invented resource ceiling. This is not the proposed two-hour/four-hour soak.
Disk is a post-run shared-workspace sample; numeric queue depths are not sampled
after cleanup. Full qualification remains blocked on budgets and real lifecycle
observations. To reproduce, run the J21 method five times in one process with
`tracemalloc`, GC, `/proc/self/status`, `/proc/self/fd` and thread counts.

The broader local GUI/audio/video regression is still running. No final local
full result is inferred from matching CI. Documentation-only pushes do not
retrigger or cancel the successful functional workflow.

## Increment F — actual-time receipt barrier

The timed harness adds `--slow-receipt`: a virtual printer worker holds its
original receipt call for **45 real seconds**, without blocking the Kivy loop.
The complete 452x900 replay **PASS in 95.080s**. The original ticket actually
remained visible **33.207s** under concurrent broad-regression load, and was
wiped while the original receipt was **still in flight**. This is not described
as exactly 30s or a performance-budget PASS. The single receipt then completed
before the original 2+1 strip batches; charge/receipt counts remain one and
OWED/`physical_paper_verified=False` remain honest. Eight real capture countdowns
and two independent retakes are retained. This run uses natural expiry; it does
not claim the early-NEXT sub-scope of PP-051 or physical printer acceptance.

The 45-second fixture delay is a fault stimulus, not a product timeout policy.
No actual device/provider/Drive transport is enabled. Runtime source remains
36ec0cc; only the versioned diagnostic harness/documentation changes.

```text
python docs/qa/portrait-v2-sandbox/evidence/run_timed_synthetic_journey.py --slow-receipt
```

## Increment H — broad-run setup error preserved and fixture retest

The first complete local GUI/audio/video run at 36ec0cc finished in 1,204.513s:
**1,757 run, 1,753 PASS, zero FAIL, one ERROR, three SKIP**. The model SKIPs are
the three explicitly blocked real MediaPipe methods, not PASS. There are 1,667
normalized distinct method IDs. The error was in positive PAID setup for
`PrivateTicketCheckoutTests.test_retired_private_owner_cannot_offer_receipt_or_restore_pixels`:
`payment` was None and the helper indexed it before reaching privacy assertions.
This full run is **not PASS**, even though 36ec0cc CI is independently green.

Five isolated repeats of that exact case PASS. A sixth diagnostic holds
readiness beyond the existing two-second bound: the backend correctly raises
DraftHeld, sends **zero charges**, and reproduces the same helper TypeError.
The first occurrence lacked detailed readiness telemetry; its exact cause
remains **unproven**, not silently attributed to that controlled reproduction.

The positive privacy-test helper now permits one fresh original setup retry
**only** after proving zero provider calls and no attempt beyond PREPARED.
It asserts original attempt identity, PENDING and exactly one charge before
proceeding. It never retries SENT/UNKNOWN or alters a production guard. No
assertion, durability check, timeout or safety requirement is removed. A new
connected regression ages the original readiness after PREPARE, checks zero
POST before the second observation, and proves the same original attempt pays
once after fresh readiness. Before repair: one ERROR; after: affected ticket/
checkout/readiness scope **41 PASS**, zero failures/errors/skips, 16.887s.

This is a **test-fixture assumption repair**, not a new product defect ID or a
relaxation of the two-second readiness fence. Runtime remains unchanged from
36ec0cc. The complete local regression must now be repeated without concurrent
resource probes/replays, and the new test-source CI must be inspected before
final status. The original failure and all diagnostics stay in the run ledger.

## Increment I — BUG-044: native original checkout recovery action

Follow-up UI inspection found an independently reproduced product dead end:
after initial begin is held before sending, PERIKSA STATUS only reconciles an
existing attempt. With no attempt, restoring readiness cannot get the visitor
to QRIS; the screen had no original begin retry. The same action was unavailable
after a lost initial HTTP reply. Two actual Kivy/API regressions initially FAIL
(2 run, zero errors/skips, 38.727s).

The original page now offers **COBA LAGI CHECKOUT ASLI** for an initial missing
observation/NOT_CREATED or UNKNOWN+PREPARED attempt. It reuses the existing
serialized `begin_payment` command and authenticated backend begin, preserving
the original frozen group and lease. Backend PREPARED is freshly checked before
POST; SENT/UNKNOWN never POST again. Status polling still cannot create a
payment. Verified expiry/cancel/review do not get this action; QR3 still offers
no QR4. No new provider semantics, ticket, discount or public output.

The entire native checkout widget module now **17 PASS**, zero failures/errors/
skips, 161.703s. Assertions witness zero charges during readiness HOLD/status
poll, explicit user retry after readiness returns, one original attempt/charge,
unchanged six captured files, and same attempt/order after an accepted create
whose HTTP reply was lost. The existing QR1–3 regression also rejects the new
retry action after QR3 expiry. Partial mapping: PP-019/021/083.

This product defect is distinct from the positive-helper assumption in H; the
first broad run's precise original cause remains unproven. The running 2ac2380
broad retest was deliberately **SUPERSEDED/CANCELLED** (exit 137, no summary),
because a runtime repair now requires final-source verification. It is neither
PASS nor product FAIL. Final runtime/test CI and broad replay must use the new
BUG-044 source; earlier source-specific successful evidence remains historical.

## Increment J — final-source replays and verification in progress

BUG-044 was immediately pushed and remote-verified at
`fec4f7f9d3169d1421a704813d83355bee12f4d1`. Final-source actual-monotonic replays:
452x900 with held receipt **PASS / 94.168s**, ticket visible **30.031s** and
wiped before the 45s virtual receipt returns; 800x1280 **PASS / 79.731s**, ticket
visible **30.024s**. Each preserves eight real countdowns, one charge/receipt,
2+1 strips, OWED and no physical-paper claim.

[CI 41927170321](https://github.com/pratikto/PhotoBooth/actions/runs/41927170321)
at fec4f7f has completed Ubuntu **557 PASS** and native **67 PASS**; logs inspected,
zero failures/errors/skips. Windows pending. The broad local GUI/audio/video
run at the same source started 05:43:59 Asia/Jakarta and is still RUNNING.
No full result or 3/3 CI is claimed yet. Follow the
[exact active verification checkpoint](PP07-R1-CONTINUATION-2026-11-05.md).

## Final functional-source CI gate — complete; local broad run still pending

**[CI 41927170321](https://github.com/pratikto/PhotoBooth/actions/runs/41927170321)
at fec4f7f completed 3/3 SUCCESS:** Windows **557 PASS** / 493.965s, Ubuntu
**557 PASS** / 172.505s, native **67 PASS** / 112.044s. All zero failures/errors/
skips; every completed log independently inspected. This is **1,181 platform
executions**, not unique acceptance cases. New BUG-044 native cases and the
original privacy case/new guarded setup case are individually present in logs.
[Exact-source CI/artifact record](evidence/pp07-ci-final-r1-2026-11-05.json).

The local broad run at fec4f7f remains RUNNING without a summary at this
checkpoint. No local full PASS is inferred from CI, no owner row is promoted,
and the first ERROR/cancelled run remain in the ledger. Documentation-only
checkpoints preserve the successful functional CI without rerunning it.

## Remaining execution and external gates

Next: investigate the native SDL PCM callback failure, then complete protected
original-worker restoration and remaining implementation scopes. Independent
local hard-exit barriers, virtual delivery races and actual-monotonic replays
have executed within their recorded scope; none supplies full device acceptance.
Historical acbac15 results remain historical.

Full protected original-worker restoration is not implemented; Windows DPAPI
byte tests alone do not supply it, and the Ubuntu protector remains unsupported.
Actual merchant profile/credentials/account evidence, POS80 paper, webcam/touch/
speaker, cloud ACL/retention and security/finance/legal review remain separate.
PP-101/104–110/112 still lack their required implementation/external scope;
classifier candidates are not refunds. Refund and production stay disabled.

Owner PILOT remains 24 NOT_RUN / 2 BLOCKED. The supervised synthetic worksheet
remains conditional on its actual device preflight; this in-progress campaign
does not request owner testing or declare final readiness at the new source.

## Increment K — broad regression failure and idle-helper diagnosis

The fec4f7f broad run completed **1,760 executions: 1,756 PASS, 1 FAIL,
zero errors, three model SKIP**, 1,141.769s; 1,670 normalized method IDs.
The failing original delivery-widget preparation case observed `busy=True`
after its settle helper. Preserve this FAIL, independently of successful CI.
An isolated original repetition PASS (1.651s). A controlled ordinary refresh
deadline at the helper's trailing idle poll reproduces the same assertion
(1 FAIL, 1.507s): polling while idle can submit a new Drive snapshot.
The original full occurrence lacks action telemetry, so its precise cause is
**unproven**; this controlled reproduction is not silently substituted for it.

The test-only helper now stops as soon as it observes idle, without a second
unconditional idle poll. Five-second bound, busy assertion and all readiness,
thread identity, one-service and no-transaction checks remain intact. There is
no production timeout/worker/readiness change and no new product bug ID.
The entire native delivery-widget module **11 PASS**, zero failure/error/skip,
24.256s; a controlled idle-refresh boundary replay also **1 PASS**, 1.358s.
A new source-matched broad run is still required; this is not a full local PASS.

## Increment L — exact-source CI, broad PCM failure and reconciled register

At `38254738cf0724655aea61dfd3bb1beb5812b5cb`, the broad GUI/audio/video run
completed **1,760 executions / 1,756 PASS / 1 FAIL / zero errors / three model
SKIP**, 1,199.371s, **1,670 normalized method IDs** (including non-PASS IDs).
It started 06:06:28 Asia/Jakarta. The delivery helper case now PASS.
The failing method is
`test_kiosk_v2_native_audio.NativeChannelReuseTests.test_repeated_muted_video_channel_reuse_has_real_pcm_and_keeps_active_ad_gain`: the game soundtrack
probe returned **no callback samples (`[]`)** in its 0.12s observation window.
That is not an observed zero-amplitude buffer and does not prove silent physical
audio. It remains an unexplained broad-run FAIL. Do not change playback, enlarge
a product timeout, skip the assertion or label a product defect without evidence.

Fresh isolated complete audio module **2 PASS / 14.017s**, followed by the
original native case repeated three times **3 PASS / 38.572s**, all zero failure/
error/skip. Actual dummy SDL PCM was measured; physical speakers remain pending.
These scoped retests do **not** turn the earlier full run green. No further
runtime/test change was made after `3825473`. No active local/CI test remains.

Exact-source [CI 41930961409](https://github.com/pratikto/PhotoBooth/actions/runs/41930961409)
completed **3/3 SUCCESS**: Windows 557 PASS / 446.437s, Ubuntu 557 PASS /
179.632s, native 67 PASS / 82.835s; zero failure/error/skip, all logs individually
inspected. [CI record](evidence/pp07-ci-k-r1-2026-11-05.json). This is 1,181
platform executions, not acceptance cases. The registered workflow excludes
the legacy native SDL PCM/delivery-widget modules; it cannot resolve that FAIL.

All canonical PP mappings were checked against actual per-method outcomes at
this source, with current AST locations. **103 PP IDs / 154 distinct mapped
method IDs** have individually observed PASS within partial software scope,
even though the overall suite failed. Nine PP required scopes remain missing:
**PP-101, PP-104–110, PP-112**. Three UAH IDs (019/021/022) have local-only
SQLite process-barrier evidence. The timed final-runtime replays add actual
30.031s/30.024s ticket observations, with one charge/receipt, 2+1 virtual copies
and OWED; they do not discharge paper obligations.
[Per-case evidence](evidence/pp07-case-evidence-r1-2026-11-05.json) and the
[versioned register](evidence/pp07-execution-register-r1-2026-11-05.csv) preserve
all **188 identities and full statuses: 186 NOT_RUN / 2 BLOCKED**, zero full
acceptance PASS. PILOT remains 24 NOT_RUN/2 BLOCKED; the 14 original AR stage
definitions/approvals are unchanged. Sixteen new R1 methods are not sixteen
acceptance cases. No owner observation is inferred or requested.

**Owner readiness:** do not begin full device UAT on a claim of all-green
software. The existing supervised synthetic worksheet remains a conditional
route after device preflight, but this continuation first investigates the
remaining independently testable PCM failure. Real paper/cloud/provider/refund,
protected restore and production/AR-13 remain separately unapproved or blocked.
Raw logs, venv and synthetic render PNGs are task-local only; sanitized counts,
checksums, source/tests and exact continuation are committed.
