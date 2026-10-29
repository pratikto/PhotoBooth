# Meong Photobooth — test evidence and acceptance

## 29 October — verified AR audit checkpoint at 4642841

**Functional `4642841f3e99d8c74b4b379e24922a7ba3f614c9`**, pushed/remote-verified. Full
**1,100 run / 1,097 PASS / 3 optional palm SKIP / zero failure/error**, 364.124s;
native video PASS, GUI/audio/video opt-ins, Python 3.12.14/Debian 13.6/offscreen/
dummy audio. Matching [CI 40790865010](https://github.com/pratikto/PhotoBooth/actions/runs/40790865010)
**all three jobs SUCCESS**, including Windows payment/reconstruction cases.
[Exact command/source/digests](qa/portrait-v2-sandbox/evidence/ar-audit-final-verification.json).
Payment micro-push 8ebcd12: 116 focused PASS; BUG-022 fix 4642841: 61 focused PASS;
source audit/docs 5d318f8 pinned. No new local native/physical evidence inferred.

BUG-022 fixed/verified; **BUG-023 OPEN**, no durable wrong-PIN denial audit (UX-13
FAIL), and native connectivity-restored producer absent (PAY-08 NOT_RUN).
Matrix **44 PASS / 1 FAIL / 9 BLOCKED / 15 NOT_RUN**. First source pass read;
overall audit **IN_PROGRESS**, no blanket conformity/unattended release verdict.
Next: AR-02 bounded native connectivity event/fixture, AR-03 exact allocation/
STARTED faults, remaining service/media cases, AR-09 redacted denial audit.
External gates/OPS NOT_STARTED unchanged. Current containing docs publication
pins the safe handover; only disposable work/ local, no unpublished runtime patch.


## 29 October — AR source audit first pass and corrected denial verdict

Functional `4642841f3e99d8c74b4b379e24922a7ba3f614c9` pushed and remote HEAD verified. Payment
8ebcd12: 116 focused PASS; BUG-022 correction: 61 focused PASS. Bounded source
pass now covers AR-00–13. **BUG-023 OPEN**: wrong-PIN requests are rejected/rate-
limited but lack durable denial audit; UX-13 corrected from PASS to **FAIL**.
Operator rate budget is process-local, customer ticket budget separately durable.
Native connectivity-restored producer is absent (AR-AUDIT-002/PAY-08 NOT_RUN).
Current matrix **44 PASS / 1 FAIL / 9 BLOCKED / 15 NOT_RUN**; no blanket conformity
verdict. [Findings/probe](qa/portrait-v2-sandbox/AR00-AR13-CODE-REVIEW.md#increment-4--nativeoperational-source-pass-and-remaining-findings).

Full regression at 4642841 running; CI 40790865010 pure/Windows SUCCESS, desktop
still running. Superseded 40790391324 CANCELLED by concurrency. Finish both and
pin actual results, then dependency-ordered PAY-08/CAP-01–05 fault evidence and
AR-09 denial audit. External/device/production gates unchanged, OPS NOT_STARTED.
This containing docs checkpoint preserves exact source/findings; only disposable
work/ diagnostics local, no unpublished runtime patch.


## 29 October — AR audit BUG-022: hold missing committed output before restore

Payment audit `8ebcd123098fe5a937c59f2b88d7fe60c9bedf7b` pushed/remote-verified,
116 focused PASS; PAY-06/PAY-21 closed as synthetic evidence gaps. Matrix now
45 PASS / 9 BLOCKED / 15 NOT_RUN. Subsequent source review confirmed **BUG-022**:
missing COMMITTED PNG was accepted by inspection; restore installed state before
FileNotFoundError. Corrected validation holds before installation, preserves
originals/manifest/OWED and performs no rerender/print or payment mutation.
New test first reproduced 2 FAIL/1 ERROR in a 14-case run; **61 focused PASS**
after correction, zero failures/errors/skips (39.146s). This containing commit
is the functional correction; final full regression and matching CI PENDING.
[Review and exact evidence](qa/portrait-v2-sandbox/AR00-AR13-CODE-REVIEW.md#increment-3--confirmed-missing-output-reconstruction-defect-bug-022).
Audit IN_PROGRESS; no production/OPS/deployment. Previous f72fdbc full/native
results remain historical. Next: full regression at pushed correction and remaining
native/privacy/operator/launcher review, then exact remaining matrix faults.
Only disposable `work/` local; no unpushed runtime patch after publication.


## 29 October — final AR-12 source evidence and AR-13 readiness

Final runtime/test `f72fdbc53041dd785fbcf7d8ef6b8eb0c17dcc88`: **1,097 run / 1,093 PASS / 4 SKIP / zero failures/errors**, 428.924s, Python 3.12.14 / Debian 13.6,
GUI/audio opt-ins with offscreen software GL/dummy audio, tracked tree clean.
[CI 40767441201](https://github.com/pratikto/PhotoBooth/actions/runs/40767441201):
all three jobs SUCCESS at matching source. Native 28 PNGs/both portrait sizes,
four QR checks PASS; payloads private. Previous-session 1094/1091/3 log unavailable;
this is a new independently captured result. Matrix 43 PASS / 0 FAIL / 0 SKIP /
9 BLOCKED / 17 NOT_RUN; exact missing fault windows are not credited as PASS.

[AR-13 assessment](qa/portrait-v2-sandbox/AR13-READINESS.md): **CONDITIONAL** for
controlled acceptance; **NOT READY for unattended commercial release**. Device,
merchant, phone/paper/Drive/deletion, privacy/remedy/operations and owner approval
remain open. First unfinished source-evidence task: PAY-06 abrupt exit between
provider evidence and DB commit, then remaining matrix gaps. AR stays top priority;
all future Settings/Emulate Ticket/QRIS Slip implementation stays NOT_STARTED.
[Exact command/skips/provenance](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-VALIDATION.md) ·
[checkpoint/next action](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md).

## 29 October — AR-12.d: retain Windows pass and expose Linux isolated-photo failure details

CI 40756011109 Windows autonomous/native and pure jobs PASS; desktop P3 group FAIL with unknown cause. Failure-only report annotation added, no assertions/application changes. Final local full rerun still running. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-VALIDATION.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-12.c: correct Windows PNG fsync and verify real output crash boundaries

First full local run 1093 run/1090 PASS/3 optional palm SKIP; Windows CI revealed read-only fsync Errno 9. Fixed non-truncating writable descriptor, added four output child-exit boundaries, retained all assertions; focused outcome recorded in validation. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-VALIDATION.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-12.b: expose Windows autonomous test failures without changing assertions

Pinned source 09788b1 native 28 PNG captures and four QR checks PASS; local full suite running. Initial Windows autonomous CI FAIL, underlying case unavailable because log-storage host is network-denied; diagnostic annotation added. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-VALIDATION.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-12.a: close final archive binding and WAL fault gaps before full regression

Focused 57 PASS, then final durability/core 25 PASS, zero failures/errors/skips. Actual child os._exit, WAL integrity and locked writer checked; Windows recovery CI and release/return renderer extended. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-VALIDATION.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-11: design public webhook boundary and verify unmounted durable inbox prototype

Focused 38 PASS, zero failures/errors/skips; no public listener, runtime mount, merchant callback, deployment or BI-SNAP migration. Infrastructure gates remain explicitly unapproved/NOT_RUN. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-WEBHOOK.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-10: bound opt-in exited-GUI recovery with durable budget and original leases

Focused 93 PASS, zero failures/errors/skips; no live-process kill or automatic business effect, three restarts/ten minutes only with isolated Sandbox and released leases. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-SUPERVISOR.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-09.c5: mount deliberate isolated booth release and original customer return

Focused 47 PASS plus four isolation PASS, zero failures/errors/skips. Native two-step PIN release waits for local receipt and server ACK; original one-photo session returns without another charge; uncertain printing stays held. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATOR.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-09.c4: persist worker isolation and exact archived customer recovery

Focused 37 PASS, zero failures/errors/skips; real HTTP and synthetic photo release/new visit/return preserves original bytes, grant and capture count; lost ACK repeats persisted IDs. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATOR.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-09.c3: authenticate two-phase release and require current service fencing tokens

Focused 58 PASS, zero failures/errors/skips; operator HTTP release and reacquired current-token service covered. No native release control yet. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATOR.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-09.c2: preserve paid rights through two-phase occupancy release and exact reacquisition

Focused 48 PASS, zero failures/errors/skips; prepare/ACK/restart/replay and original proof/new-token/free-booth invariants covered. Core internal seam only, no release endpoint/UI yet. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATOR.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-09.c1: fence stale service workers before implementing safe booth release

Focused 86 PASS, zero failures/errors/skips; five migration/CAS/restart/race cases. Dormant internal seam only; no UI/API rotates fences and no booth release is enabled. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATOR.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-09.b: mount PIN-protected native operator metadata inspection

Focused 64 PASS, zero failures/errors/skips; wrong/missing/correct PIN, private media denial, journal secrecy and retired callbacks covered. Twenty provisional native PNG fixtures rendered at both required sizes. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATOR.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-09.a: isolate a per-launch Sandbox operator PIN from the GUI

Focused 64 PASS, zero failures/errors/skips; backend-only PIN and mocked launcher argv/environment/local-notice isolation covered. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATOR.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-08.b2: record native postpaid faults with durable same-operation retries

Focused 58 PASS, zero failures/errors/skips; postpaid missing-camera, capture I/O failure and lost-ACK/restart fixtures preserve payment, OWED, manifest and one issue operation. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-READINESS.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-08.b1: persist paid-unfulfilled issues without altering customer financial rights

Focused 56 PASS, zero failures/errors/skips; five new durable/concurrent/migration/authenticated HTTP issue cases; CI registration included. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-READINESS.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-08.a: gate native new payment on camera storage and template readiness

Focused 57 PASS, zero failures/errors/skips; offline readiness and native no-camera/no-order gates covered; new module registered in CI. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-READINESS.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-07.b4: recover original pre-manifest allocation without creating another session

Focused 42 PASS, zero failures/errors/skips; original RESERVED empty allocation recovery and STARTED/orphan denial covered in photo and native HTTP fixtures. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-NATIVE.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-07.b3: mount native ticket claim and customer-led exact photo recovery

Focused 46 PASS, zero failures/errors/skips; native HTTP-to-photo restore, cached-camera ticket decode, minimize/idle privacy and input-preserving polling covered. Sixteen provisional fixture PNGs rendered at both target sizes. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-NATIVE.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-07.b2: hide private photo snapshots and fence reconstruction after lock

Focused 35 PASS, zero failures/errors/skips, including same-session reclaim and lock-during-reconstruction fixtures. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-NATIVE.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-07.b1: revoke stale permits and acknowledge exact resumed service

Focused 37 PASS, zero failures/errors/skips; three added session cases cover privacy revocation, original STARTED acknowledgment/current refund and completed-result-only restore. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-NATIVE.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-07.a: native save-ticket gate and neutral privacy-held screen

Two new native gates and focused 37 PASS, zero failures/errors/skips. Twelve native working-tree captures rendered at 800x1280/452x900; both recovery-ticket screenshot QR payloads decode correctly without logging secrets. Payment URL/copy actions remain hidden until ticket acknowledgment. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-NATIVE.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-06.b: memory-only customer ticket and trusted claim controller

Six new session cases; focused 92 PASS, zero failures/errors/skips, including native Sandbox compatibility. Raw ticket never enters journal/backend views; restart requires original proof. Current settlement is rechecked at resume action, pending proof never issues media permission, and privacy generation rejects late callbacks. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CUSTOMER-CLAIM.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-06.a: hashed customer capability and current-payment redemption

Eight new customer-proof cases and focused 137 PASS, zero failures/errors/skips. Additive capability binding is atomic with order; only SHA-256 persists. Expiry, durable attempt budget, one-use action replay and fresh settlement gate protect redemption without operator privilege bypass. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CUSTOMER-CLAIM.md).
Physical/provider gates remain separate; no production activation.

## 29 October — AR-05.b: exact private photo reconstruction behind one-use in-memory permit

Nine new reconstruction cases pass; focused 63 PASS plus nine final guard checks, zero failures/errors/skips. Restores partial shots, selected/used retake, staged captures/PNG and multi-design copies without new IDs, shutter, renderer or print. No old media is returned without a bound ephemeral permit; UI mounting remains disabled until AR-06/07. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-PHOTO-RESUME.md).
Physical/provider gates remain separate; no production activation.

## 28 October — AR-05.a: immutable strip publication with frozen input hashes

Three new output cases; focused 71 PASS, zero failures/errors/skips, including native handoff, capture, delivery and v1 retention/workflow. PNG intent and input identities persist before rendering; published-but-unacknowledged output cannot be overwritten on retry. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-PHOTO-RESUME.md).
Physical/provider gates remain separate; no production activation.

## 28 October — AR-04.a: write-ahead immutable JPEG capture and atomic retake quota

Seven new capture cases, five abrupt process boundaries, and focused 73 PASS, zero failures/errors/skips. V2 opts in; v1 writer defaults unchanged. Existing/orphan JPEGs cannot be overwritten; retake selection/quota commit with saved bytes. Native Sandbox and retention checks pass. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CAPTURE.md).
Physical/provider gates remain separate; no production activation.

## 28 October — AR-03.b: unique allocation before local photo creation

Focused 204 PASS, zero failures/errors/skips, including native HTTP-to-photo handoff, allocation replay/restart, initial binding, v1 workflow and retention. Server atomically assigns one PB001V2AR-style transaction before any folder creation; exact initial manifest binds original payment/permit. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-FULFILLMENT.md).
Physical/provider gates remain separate; no production activation.

## 28 October — AR-03.a: frozen order contract and independent fulfillment obligation

Six new fixtures and focused 133 PASS, zero failures/errors/skips. New orders freeze server pricing/template hashes before I/O; payment creates an owed fulfillment independently of UI claims. Legacy duplicate bindings quarantine both mappings without altering original evidence. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-FULFILLMENT.md).
Physical/provider gates remain separate; no production activation.

## 28 October — AR-02.c: private restart observation and recovery worker retry

Focused 152 PASS, zero failures/errors/skips, including native Sandbox lifecycle. Four new restart tests and persisted priority-trigger test pass; RECOVERY retains original phase, grant and transaction and never resumes capture. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-RECONCILIATION.md).
Physical/provider gates remain separate; no production activation.

## 28 October — AR-02.b: durable bounded reconciliation scheduling and fencing

Focused 126 PASS, zero failures/errors/skips. Fifteen new AR-02 cases cover cached evidence, concurrent workers, jittered backoff, stale responses, additive schema and clock rollback. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-RECONCILIATION.md).
Physical/provider gates remain separate; no production activation.

## 28 October — AR-02.a: fresh payment observation and admission guard

Nine new cases; focused 120 PASS, zero failures/errors/skips. Backend-only provider GET observation requires booth authentication; operator mutation remains PIN-gated. Cached PAID cannot authorize claim/STARTED without fresh settlement. [Scope, tests and remaining work](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-RECONCILIATION.md).
Physical/provider gates remain separate; no production activation.

## 28 October — final AR-01 automated validation

Exact functional SHA `017b417d02d63a79b1c5b21c4f0613b7d15186fc`: full **968 run / 965 PASS / 3 SKIP / zero failures/errors**;
132 focused PASS/zero skips. Three optional palm-assets SKIP are not passed cases.
Matching [CI 40688374416](https://github.com/pratikto/PhotoBooth/actions/runs/40688374416):
all three jobs SUCCESS, including Windows attempt/crash fixtures. Linux local uses
SDL offscreen/software rendering and dummy audio. [Raw reports/commands/hashes](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CREATION.md).
Merchant, physical Windows/Ubuntu, paper/Drive/retention and release NOT_RUN.

## 28 October — AR-01 test-first creation durability

Nine attempt/migration tests and six AR-00 baseline tests included in **132
focused PASS, zero FAIL/ERROR/SKIP** (Linux/Python 3.12.14). Earlier eight new
tests produced 2 FAIL/6 ERROR before implementation. Includes separate SQLite
connections, concurrent backends, abrupt PREPARED/SENT/provider-accepted exits,
old-schema preservation and rows from rollback-era writers. Full/CI/physical
checks pending; exact commands/results/source hashes in
[AR-01 evidence](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CREATION.md).

## 28 October — AR-00 offline baseline

Base `f6736b7c739e3317e3bcc4506edb250f9e47d92b`, runtime unchanged.
Six new baseline fixtures plus existing focused protocol group: **87 PASS,
0 FAIL/ERROR/SKIP**, Linux/Python 3.12.14. Actual abrupt child exits before
provider send/after accepted synthetic charge reopen the original SQLite order;
missing/404 evidence cannot replace it. Optional fraud semantics and capture
restart hold covered. Command and limits in the [checkpoint](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md).
These characterize existing safeguards; AR-01–13 and physical/provider/full
acceptance are not credited by this result.

## 28 October — Sandbox GUI copy link

Source `39e8c32`: exact current image-action URL, clipboard error/retry,
unavailable QR pixels, stale callbacks and phase/mode/busy/suspend guards tested
with unchanged order/one charge. Six native pending/success/error screenshots
at 800×1280 and 452×900 reviewed; both pending QR screenshots decode to the
offline fixture. [Raw results and device/provider limits](qa/portrait-v2-sandbox/COPY-LINK.md).

## 28 October — BUG-021 pending QR image

Before: seven regression cases, five failures/zero errors. After: **182 focused
PASS / zero failures/errors/skips**, 14.158s. Repeated automatic native polling,
durable restart, replacement/cache validation and terminal removal covered.
Source `4237d3f`: full **933 run / 930 PASS / 3 optional palm SKIP / zero
failures/errors**, 289.540s; CI 40614355442 all three jobs SUCCESS (Sandbox:
182 PASS/zero skips). Ten native captures and two actual screenshot QR decodes
verified; [raw evidence and device limits](qa/portrait-v2-sandbox/QR-POLLING.md).

## 28 October — Sandbox QR logo

175 focused Sandbox/QR checks PASS, zero failures/errors/skips, 11.383s.
Includes pixel-identical data, failure fallback, unchanged bounded downloads,
same-order cache/status, native resize and the existing strict screenshot
reader's negative tests. Initial one-scale 277px OpenCV failure is preserved
with its diagnosis; no runtime QR data is changed to satisfy the test.
Source `8ed6f11`: final full 926 run / 923 PASS / 3 optional native palm-assets
SKIP / zero failures/errors, 290.905s; matching CI 40610731638 all three jobs
SUCCESS. Fifteen exact-source native PNGs and all three WAITING QR pixel decodes
PASS. [Source, raw reports and manual limits](qa/portrait-v2-sandbox/QR-LOGO.md).

## 28 October — saved Sandbox credentials

New offline tests cover file defaults, pair precedence, prompt fallback, no code
execution, sanitized errors and shared/v2 backend-only forwarding. Existing
Sandbox CI and Windows stdlib-only CI include the new module. Local execution
became unavailable before edits: do not transfer prior 901-case evidence to this
source. Matching source `b496d9f` / CI 40576392500: all three jobs SUCCESS,
15 new cases PASS on each OS; Linux Sandbox 157 PASS, Windows portable 55 PASS,
zero skips in those groups. [Exact CI/source results](qa/portrait-v2-sandbox/LOCAL-SETTINGS.md).

## 28 October — BUG-020 Sandbox key syntax

Baseline reproduction: two new-format checks error at the unchanged prefix
guard. Corrected source: 136 focused launcher/provider/backend/session checks
PASS, zero failures/errors/skips, 0.420s. Both key formats retain Sandbox-only
requests and server-only credentials; HTTP 401 never falls back to Production.
Source `6a271de`: final full 901 run / 898 PASS / 3 optional native palm-assets
SKIP / zero failures/errors, 277.362s. Matching CI 40572395949 all three jobs
SUCCESS (Sandbox group 142 PASS). Raw results and merchant NOT_RUN limits are in the
[correction evidence](qa/portrait-v2-sandbox/KEY-FORMAT.md).

Matching-source CI **40481718367**: all three jobs SUCCESS.
Gallery fix **eb0297d**: final local **898 run / 895 PASS / 3 optional
palm-assets SKIP / zero failures/errors**, 291.903s; 20 targeted checks and
18 exact-source native captures (nine held-pointer frames). Actual device retest
remains pending. [Exact evidence/update](qa/portrait-v2-carousel-hold/README.md).


## 27 October — BUG-019 held gallery drag

Owner reports an empty incoming side while holding a carousel drag. Five pooled
Images existed, but two outer textures were cleared at rest. The existing widget
now retains a five-picture cached window through drag, reversal and release.
Native checks cover all 12 designs, both directions and five sizes, including
wraparound; selection/quantity and lifecycle guards remain. Device acceptance
is separate. [Scope, tests and update](qa/portrait-v2-carousel-hold/README.md).


Final customer-delivery source **311f3d8**: **896 local run / 893 PASS /
3 optional palm-assets SKIP / zero failures/errors**; 73 focused PASS,
14 exact-source native captures and eight exact right-panel QR decodes.
Matching-source CI **40472339778**, all three jobs SUCCESS.
[Exact evidence/update](qa/drive-delivery-performance/CUSTOMER-PRIORITY.md#final-source-and-evidence).


## 27 October — customer upload priority and early folder QR

Latest owner instruction supersedes the earlier completion-only screen QR and
interleaved old-recovery policy. Customer uploads now run FIFO to completion;
old retries/reserves/content wait at request boundaries. Two short retry delays
(5s, 15s) precede release to bounded background retry after a third consecutive
failure. Verified assigned-folder QR can appear while bytes are pending, with
truthful upload/retry messaging and a 30-minute check-back suggestion, not an SLA.
Folder claims/manifest mapping survive restart; duplicate/replaced customer
folders are rejected. Code.gs and physical printing policy are unchanged.
[Current contract, evidence, update and limits](qa/drive-delivery-performance/CUSTOMER-PRIORITY.md).

Logging correction source **4c31406**: full local **888 run / 885 PASS /
3 optional palm-model SKIP / zero failures/errors**, 262.543s; real-Kivy
console-active integration, broken-sink worker survival and 11 delivery widget
checks PASS. Matching-source CI 40460799605: all three jobs SUCCESS.
[Update and exact evidence](qa/drive-delivery-performance/LOGGING.md).
The supplied RecursionError incident is distinct from the protected old-folder
conflict; exact on-device handler/exit traceback and post-update timing remain unverified.

## 27 October — delivery logging recursion recurrence

Owner reports >10 minutes and supplies RecursionError timing; new queued work
has no worker_start in the extract. Old-folder BIND_FOLDER_CONFLICT is confirmed
for one transaction. Real-Kivy console-active reproduction exposes root/stderr
logging recursion missed by earlier console-disabled QA. Timing now uses the
session file directly, contains sink failures/re-entry, and v2 defaults to MIXED
logging with native diagnostics retained. 54 targeted tests PASS; final checks
are recorded in the [correction runbook](qa/drive-delivery-performance/LOGGING.md).
Code.gs unchanged; no redeploy, reset or known-folder replacement is required.

Retry source **8578825**: complete local **884 run / 881 PASS / 3 optional
palm-assets SKIP / 0 failures/errors**, 268.095s. 67 focused service and
11 native delivery PASS. Matching-source CI 40455236898: all three jobs SUCCESS.
[Exact proof/update guide](qa/drive-delivery-performance/RETRY.md).
Functional source is unchanged in the final evidence publication; actual
Windows/Ubuntu/Google timing after this update still needs device evidence.

## 27 October — failed-delivery retry isolation

Owner timing identifies repeated old bind failures as 70.782s of a 122.719s
queued-to-QR session; exact ValueError cause/installed SHA remain unknown.
Healthy-first scheduling, one recovery/30s, persisted 30–300s backoff and safe
bind codes are implemented; known folder/transaction conflicts remain protected.
Focused service/native checks PASS; final regression/CI evidence is in the linked runbook.
Code.gs unchanged; no redeploy required. [Scope, evidence, updates and limits](qa/drive-delivery-performance/RETRY.md).

Final delivery source **2e140c1**: full local **877 run / 874 PASS / 3 optional
palm-assets SKIP / zero failures/errors**, 262.743s; 29 Code.gs VM PASS,
11 focused native delivery PASS. Matching-source CI **40448427344**, all three
jobs SUCCESS; 14 native FBO screenshots verified at both required sizes.
[Final evidence, update/manual deployment, timing export and limits](qa/drive-delivery-performance/README.md).
Runtime unchanged in the final evidence publication. No production Drive-speed,
Windows/Ubuntu hardware, cloud deployment or deletion acceptance is inferred.

## 27 October — Drive delivery priority and timing

The owner prioritizes customer upload/GUI responsiveness. Source now uses one
file per transaction per pass, chunk-yielding content sync, incremental five-slot
reserve batches with startup/periodic reconciliation, and verified cross-version
asset reuse. Structured monotonic timing distinguishes queue/request stages.
Known-delay production root cause remains unmeasured; native/fixture evidence
and exact update/rollback steps are in the [delivery runbook](qa/drive-delivery-performance/README.md).
No deployed Google version, actual throughput or cloud deletion is certified.

**Final FEAT-009 verification — 27 October:** source `f023029` / matching-source
CI [40423003641](https://github.com/pratikto/PhotoBooth/actions/runs/40423003641),
all three jobs SUCCESS. Windows fixture cleanup preserves assertions and runtime;
final local rerun 869 cases / 866 PASS / 3 optional palm-assets SKIP / zero
failures/errors, 272.035s. Raw final reports, source hashes, initial failed runs
and target-device NOT_RUN gates: [stage-2 package](qa/portrait-v2-recovery/README.md).

## FEAT-009 stage 2 — 27 October 2026

Initial stage-2 local **869 run / 866 PASS / 3 SKIP / 0 failures/errors**, 261.246s;
the three skips require optional native palm assets (camera recovery, v2 palm
countdown and standalone palm inference). 47 focused stdlib-only checks PASS;
16 real-API/Sandbox fixture checks PASS. Native launcher rejects duplicate
ownership while UI runs, resumes after suspension and releases its lock after
teardown. Generated Ubuntu user unit passes systemd-analyze verification.
Source hashes, raw reports, review scope and manual Windows/Ubuntu gates are in
the [stage-2 evidence](qa/portrait-v2-recovery/README.md). No physical acceptance.
Prior API hangs were reproduced with command-network restriction; granting
network permission resolves the fixture without changing payment/API source.
Keep older failed reports below as dated evidence, not current unresolved tests.

## FEAT-009 stage 1 — 27 October 2026 local continuation

New-source validation and pending Windows/startup checks are tracked in the
[watchdog runbook](qa/portrait-v2-watchdog/README.md). Baseline `5639400`, working
tree changes; existing dated CI below does not cover this increment. User defers
manual device testing. Hardware/provider/cloud/startup sign-in checks NOT_RUN.
New-source checks: 22 focused PASS, 15 package-free PASS, native launcher
pause/resume/exit PASS; twelve synthetic render hashes/dimensions verified.
Full regression NOT VERIFIED: two terminated attempts, latest blocked in existing
API TestClient after 715 case starts. Separate unchanged Sandbox widget fixtures:
6 tests / 6 FAIL (`Worker did not settle`). Raw reports/stacks are in the runbook.

## Drive layout repair acceptance (26 October 2026)

Verify PB001/Photo/eight-digit-number/{raw,bw,color}, actual bytes and signed-out QR access after updating both Python and the existing Web App deployment. Automatic fixture passes do not close live delivery or BUG-009. See qa/drive-photo-layout/README.md.

Updated **26 October 2026** for `feature/portrait-kiosk-v2-next`.
Recorded execution evidence remains tied to its tested source. BUG-018 final
source has new automatic checks below; actual Windows/provider acceptance is
not inferred. Earlier audit-only evidence remains tied to its original source.

## Automated evidence ledger

| Evidence | Source and result | Limits |
| --- | --- | --- |
| Latest storage/content source | 53e7b4c: **824 full Python PASS / zero failures/errors/skips**, 24 Code.gs VM PASS; matching-source CI 40273343183 all three jobs SUCCESS | 28 final native captures + two form views; 133 CI PNGs verified. No real Google/paper/phone/provider acceptance. [Evidence](qa/feat-004-storage/README.md) |
| Foldering source audit, 26 October | Source `19e3f4d`: **38 existing-service tests PASS / zero failures/errors/skips**, 5.660s; temporary visit/pool/native-raster experiments PASS | Proves current behavior/gaps, **not** target implementation or live Drive readiness. `old` contents excluded/untouched. [Audit](qa/storage-layout-audit-2026-10-26/README.md) |
| Mirrored v2 output | `fc26e3d`: **808 full PASS / zero failures/errors/skips**, 230.670s; 42 focused PASS; 19 shared renderer/template checks PASS | Asymmetric all-twelve tests preserve QR/art/masks/original hashes and actual print path/copies; first 808-PASS source 977d26b kept separately. [Proof](qa/portrait-v2-mirrored-output/README.md) |
| Mirror visual/form checks | Sixteen clean-source native captures hash/dimension verified, eight selected native + two form views reviewed at 800×1280/452×900; browser 360px overflow check | Five fresh unchecked items, safe import/Submit/persistence/download; old P03 passes do not transfer. Actual paper/Windows NOT_RUN |
| Mirror final-source CI | [40263151709](https://github.com/pratikto/PhotoBooth/actions/runs/40263151709): all three jobs SUCCESS; delivery/retention/renderer 63 PASS, health 80 PASS, Sandbox 139 PASS, native 103 PASS/one optional model-assets skip | Skipped model case covered locally; Windows audio dummy output. [Raw proof](qa/portrait-v2-mirrored-output/README.md) |
| BUG-009 source repair/diagnosis | `887ba39`: **807 full Python PASS / zero failures/errors/skips**, 238.684s; 44 focused Python PASS; 19 actual-Code.gs VM PASS | Reproduced stale enabled flag/missing clock and setup accepting wrong trigger type. Original cleanup reused; no live Google setup/deploy/delete. [Raw evidence](qa/bug-009-retention/README.md) |
| BUG-009 Submit form | Eight fresh unchecked items; metadata/READY/forged pass fields do not pass cloud checks; partial Submit/persistence/download; 360/452/800px no overflow, zero browser errors | Form screenshots are synthetic fixtures, reviewed 800×1280/452×900. Windows/Google evidence NOT_RUN; no new twenty-cycle gate |
| BUG-009 matching-source CI | [40255716011](https://github.com/pratikto/PhotoBooth/actions/runs/40255716011): all three jobs SUCCESS; delivery/retention 44 PASS, health 80 PASS, Sandbox 139 PASS, native 103 PASS/one optional model-assets skip | Skipped model case covered locally; four clean-source native views reviewed at both required sizes. [Raw reports/visual manifest](qa/bug-009-retention/README.md) |
| Simpler photo entry | `20453fe`: **800 PASS / zero failures/errors/skips**, 217.888s; preliminary focused 55 PASS/two opt-in skips covered by final full run | Twelve clean-source PNGs verified; six idle/invitation/tutorial views reviewed at 800×1280/452×900. Windows spot checks NOT_RUN. [Raw proof/checklist/rollback](qa/portrait-v2-photo-entry/README.md) |
| Photo-entry matching-source CI | [40248962384](https://github.com/pratikto/PhotoBooth/actions/runs/40248962384): all three jobs SUCCESS; delivery 17 PASS, health 80 PASS, Sandbox 139 PASS, native 103 PASS/one optional palm-assets skip | Skipped model case covered locally; Windows audio uses dummy PCM. [Raw reports](qa/portrait-v2-photo-entry/ci-reports/) |
| Print/Drive final source | `266b2c8`: **800 PASS / zero failures/errors/skips**, 213.823s; 15 new-feature focused PASS | Linux/software GL/dummy PCM/offline assets; nine reused v1 files unchanged. Physical paper/phone/cloud acceptance NOT_RUN. [Raw proof](qa/portrait-v2-print-drive/README.md) |
| Print/Drive CI/screens | [40208966127](https://github.com/pratikto/PhotoBooth/actions/runs/40208966127): all three jobs SUCCESS; 133 PNGs source/hash/dimension verified | Delivery 17 PASS, health 80 PASS, Sandbox 139 PASS, native 103 PASS/1 optional model-assets skip covered locally; large right-panel QR screenshot pixels decode at both sizes |
| BUG-018 final source / full regression | `ebb53fd`: **785 PASS / 0 failure/error/skip**, 321.181s; focused 37 PASS | Two earlier MOCK fixture timeouts preserved; final helper drains an already-completed result, unchanged deadline/runtime. [Raw evidence](qa/portrait-v2-health-clicks/README.md) |
| BUG-018 matching-source CI/screens | [40189694738](https://github.com/pratikto/PhotoBooth/actions/runs/40189694738): all three jobs SUCCESS; 119 PNGs verified | Health 80 PASS, Sandbox 139 PASS, native 97 PASS/one optional model-assets skip covered locally. Required operator views reviewed; subsequent owner retest 4/4 at unknown HEAD, monitoring |
| Earlier operator full regression | `ea394e8`: **780 PASS / 0 failure/error/skip**, 270.671s | Linux/Python 3.12/Kivy 2.3.1, software GL/dummy PCM, synthetic I/O and supplied offline face/palm assets |
| Operator matching-source CI | [40157638369](https://github.com/pratikto/PhotoBooth/actions/runs/40157638369), three jobs SUCCESS | Health 80 PASS; Sandbox 139 PASS; native 92 PASS/1 optional palm-model-assets skip, covered locally |
| Operator screenshot package | 119 PNGs verified against source/hash/dimensions; required views reviewed | Fifteen local operator PNGs also reviewed; all observations are fixtures |
| Earlier P5 full regression | `9433010`: **688 PASS / 0 failure/error/skip**, 211.646s | Earlier baseline, before health/report integration |
| P5 matching-source CI | [40109206417](https://github.com/pratikto/PhotoBooth/actions/runs/40109206417), three jobs SUCCESS; 109 PNGs verified | Native optional model-assets skip retained; no merchant/hardware PASS |

[Operator raw outputs/manifests](qa/portrait-v2-operator-health/README.md) ·
[P5 raw outputs/manifests](qa/portrait-v2-p5/README.md).
CI job success does not imply all optional cases ran. Dummy playback and native
window rendering do not prove audible speakers or touchscreen accuracy.

## Owner reports

| Report | Recorded result and limits |
| --- | --- |
| BUG-018 targeted Windows retest, later 25 October | **4/4 checked, zero unchecked, no issue notes**. Repeated/mixed input, busy close, lifecycle and next input/restart owner-reported PASS; BUG-018 MONITORING. HEAD/OS/display/device fields remain unknown; specific tested resolutions not inferred. [Raw report and assessment](qa/portrait-v2-health-clicks/owner-retest-2026-10-25.json) |
| Initial Operator Device Health, 25 October | Raw 8/8 checked; issue note reports app hang with rapid clicks, clarified as all buttons pressed in combination. **Not clean PASS at that stage**; H03/H04 prompted the later targeted retest above. HEAD/OS/display/device fields unknown. [Record and four-item form](qa/portrait-v2-health-clicks/README.md) |
| Photo/preview/first-use buttons | 16/16 and twenty cycles, no issue notes; tested HEAD/device fields incomplete; [record](qa/portrait-v2-preview-redraw/README.md) |
| Game/header/resize | 14/14 and twenty cycles, unknown HEAD; video→video lag also reported at that stage; [record](qa/portrait-v2-native-controls/README.md) |
| Later typography/audio | 8/8 and “udah clear semua”, unknown HEAD; BUG-017 becomes OWNER-REPORTED PASS / MONITORING; [record](qa/portrait-v2-sandbox/owner-acceptance.json) |
| Windows preflight, 25 October | HEAD `0dc6555` → READY_FOR_MANUAL_TEST; stdout supplied, metadata JSON/P5 form not supplied; [record](qa/portrait-v2-p5/owner-preflight-2026-10-25.json) |
| Merchant/current integration/Drive cloud deletion | Complete new evidence not supplied; BUG-009 remains OPEN |

Keep accepted observations at their original metadata limits. Do not attach
unknown-HEAD reports to a newer source or formally close bugs from preflight.

## Consolidated outstanding acceptance — 26 October

[49-item combined checklist + Submit](qa/portrait-v2-pending-acceptance/windows-checklist.html)
covers current Windows integration, physical print/mirror, actual Drive/offline,
per-booth global/local cache, BUG-009 activation/expiry, official merchant
Sandbox/recovery, its twenty NEW integration cycles, privacy and operator review.
[Coverage/scope/run instructions](qa/portrait-v2-pending-acceptance/README.md) ·
[plain checkboxes](qa/portrait-v2-pending-acceptance/checklist.md).

Earlier owner PASS/monitoring and twenty local photo/game cycles stay recorded;
no new old-cycle gate or production action is inferred. All new checkboxes start
empty. Imported metadata/READY/CI does not pass physical/provider tests. Missing
Sandbox access leaves F/G NOT_RUN while other groups can proceed. G01/G02 require
twenty new Sandbox integration cycles, as the existing P5 form already did.
Public webhook, trusted provider game promotion, v1-specific audio/Settings and
unapproved production/repository operations remain separately scoped.

## Current manual forms

| Form | Purpose | Cycle rule |
| --- | --- | --- |
| [Mirror five-item form](qa/portrait-v2-mirrored-output/windows-checklist.html) | Live/review/strip/paper orientation, unchanged raw JPEGs, frame/QR and no replay | No new twenty-cycle gate; paper requires actual sheets |
| [BUG-009 eight-item form](qa/bug-009-retention/windows-checklist.html) | Existing project/setup/new-version deployment, safe status, authorized synthetic deletion and actual clock execution | No new photo/game cycle gate; READY/import does not pass cloud tests |
| [Print/Drive eleven-item form](qa/portrait-v2-print-drive/windows-checklist.html) | New automatic print, actual paper/phone download, offline queue/restart, layout/lifecycle | No new twenty-cycle gate; paper/phone items require actual evidence and start unchecked |
| [BUG-018 four-item form](qa/portrait-v2-health-clicks/windows-checklist.html) | Repeated/mixed operator clicks, close while busy, reopen/minimize and normal next input | No additional twenty-cycle run; fresh unchecked results |
| [P5 26-item form](qa/portrait-v2-p5/windows-checklist.html) | New Windows/Sandbox integration, metadata, source/device/provider/privacy gates | G01/G02 concern twenty cycles of the new integration; old photo/game reports do not pass these |
| [Operator eight-item form](qa/portrait-v2-operator-health/windows-checklist.html) | F12/hold, observations/refresh, resize, lifecycle and safe local report | No additional twenty-cycle photo/game requirement |

Run `python tools/check_portrait_v2.py`; import
`data/diagnostics/windows-readiness.json` into the form. Import fills metadata,
not pass checkboxes. Verify the actual kiosk display and supply missing camera/
speaker fields. Check only completed successful tests; blank means failed/not run.
Submit prepares text for chat; it does not transmit it automatically.

Use [root launch instructions](../README.md) for local/MOCK modes and
[Sandbox runbook](qa/portrait-v2-sandbox/README.md) for the isolated merchant trial.
Leave unavailable provider/device checks NOT_RUN; preserve journals and reconcile
uncertain orders rather than replaying charge/capture/print.

## Remaining external evidence

Actual merchant simulator create/status/settlement/cancel/restart/outage behavior;
current Windows touch/scaling/camera/speakers/video and prolonged use; ordinary
opt-in physical printing and uncertain-send recovery; Drive/download/offline
synchronization, privacy and 30-day cloud deletion; explicit release signoff.

A public HTTPS webhook is a separate deployment/operational scope, not a
prerequisite for the current loopback launcher and simulator/polling trial. It
has not been deployed or acceptance-tested. Trusted QRIS game promotion is also
separate: the current Sandbox uses full-price consent.

## Recording new evidence

Record date, exact source/dirty state, OS/dependencies/display/device, command or
manual steps, PASS/FAIL/SKIP/NOT_RUN, observation and limits. Exclude secrets and
customer photos. Distinguish automated source results, owner reports, preflight,
merchant acceptance and physical acceptance. Keep dated failures when recording
later successful retests. [Current bugs](bug_tracker.md).

## Historical record

The [pre-audit version](https://github.com/pratikto/PhotoBooth/blob/5f09eff9998c942ed54feef0cf0563fc3944611b/docs/test_checklist.md) preserves the complete dated history. Its former “current”, approval, branch and next-step statements apply only to their recorded stage. Use the current documents linked above for continuation.

