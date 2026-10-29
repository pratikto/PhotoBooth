# Meong Photobooth — current feature status

## 29 October — AR-02.d PAY-08 focused verification

Passive OS restoration is connected to the native checkout worker: same-order
GET only, existing durable retry/lease and privacy guards preserved. **103
focused PASS**, zero failure/error/skip; final full/CI pending at this functional
publication. Matrix **45 PASS / 1 FAIL / 9 BLOCKED / 14 NOT_RUN**; BUG-023 OPEN.
[Contract/evidence/limits](qa/portrait-v2-sandbox/PAY08-CONNECTIVITY.md).
Next: final verification, then AR-03 CAP-01–05 exact allocation/STARTED crashes.
Actual devices/provider and queued OPS remain unverified/NOT_STARTED.


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

## 28 October — AR-01 final source evidence

`017b417d02d63a79b1c5b21c4f0613b7d15186fc`: immutable attempt durability verified with
132 focused PASS and full **968 run / 965 PASS / 3 SKIP / zero failures/errors**. Matching CI
40688374416 all three jobs SUCCESS. This is AR-00/AR-01 source verification;
AR-02–13, autonomous private photo resume, actual devices/provider and production
remain pending. [Current checkpoint](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md).

## 28 October — AR-01 creation durability (source, not unattended acceptance)

Backend persists immutable creation request scope/fingerprint and send ambiguity
in an additive table. Old rows remain held; timeout/404/restart cannot create a
replacement charge. Merchant/mode/request mismatches reject before provider I/O.
132 focused PASS; full/CI/device/merchant gates pending at publication.
No customer resume GUI is implemented. [AR-01 evidence](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CREATION.md).

## 28 October — Autonomous Recovery baseline

AR-00 contract/fixtures verified offline: six new cases, 87 focused PASS, no
runtime/schema change. AR-01–13 remain pending; autonomous photo resume/customer
claim is not delivered. [Exact source contract and gaps](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-BASELINE.md)
and [continuation checkpoint](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md).

## 28 October — Sandbox GUI copy link

IN SOURCE at `39e8c32`: **SALIN LINK QRIS** copies the verified active image
URL for the official web simulator, with success/failure feedback. Existing
payment and lifecycle guards remain. [Usage/checks/limits](qa/portrait-v2-sandbox/COPY-LINK.md).

## 28 October — BUG-021 pending QR polling

IN SOURCE: verified image URLs survive omitted status actions and backend
restart; explicit replacement validation and payment/expiry guards remain.
Source `4237d3f`: 182 focused PASS; full 933 run / 930 PASS / 3 optional palm
SKIP / zero failures/errors; CI 40614355442 all three jobs SUCCESS. Ten native
PNGs and both WAITING screenshot QR decodes verified. Exact device cause/retest
remains separate; [current evidence](qa/portrait-v2-sandbox/QR-POLLING.md).

## 28 October — centered Meong Sandbox QR

IN SOURCE: direct Drive-renderer/artwork reuse, exact provider-payload check,
original-image fallback, nearest filtering and per-order cache. 175 focused
checks PASS. Source `8ed6f11`: full 926 run / 923 PASS / 3 optional palm-assets
SKIP / zero failures/errors; matching CI 40610731638 all three jobs SUCCESS.
Fifteen native PNGs and three screenshot decodes are verified; actual merchant/
phone acceptance remains pending. [Evidence](qa/portrait-v2-sandbox/QR-LOGO.md).

## 28 October — saved Sandbox credentials

IN SOURCE: optional ignored local defaults remove repeated terminal entry;
static literal read, source-pair precedence, safe errors and backend-only
credential forwarding. Source `b496d9f` has 15 new-case PASS on Linux and Windows,
matching CI 40576392500 all three jobs SUCCESS. Results and local-executor limits
are tracked in the [current package](qa/portrait-v2-sandbox/LOCAL-SETTINGS.md).
Actual merchant authentication remains a separate acceptance check.

## 28 October — BUG-020 Sandbox key syntax

IN SOURCE: launcher accepts both dashboard Server Key formats; fixed Sandbox
host, redirect refusal and server-only secrets remain. 136 focused tests PASS;
full local source `6a271de` has 901 run / 898 PASS / 3 optional palm-assets SKIP /
zero failures/errors. CI 40572395949 all three jobs SUCCESS; actual merchant
acceptance remains pending. Exact evidence is tracked in the
[source-specific record](qa/portrait-v2-sandbox/KEY-FORMAT.md).

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

## Delivery responsiveness

Owner-approved Drive/GUI improvement continues from fcabfbb. Background delivery
snapshots no longer lock result buttons/footer during rebuild. The strict
UPLOAD_COMPLETE QR contract and operator-disabled printing remain. Controlled
native regression PASS; actual five-minute delay is unmeasured.
[Scope, v1 comparison, evidence and rollback](qa/drive-delivery-performance/README.md).

**Final FEAT-009 source `f023029`:** matching-source CI 40423003641 succeeds in
all three jobs (Linux pure, Linux desktop, Windows). Post-fixture-correction local
rerun: 869 run, 866 PASS, 3 optional palm-assets SKIP, zero failures/errors,
272.035s. [Final evidence](qa/portrait-v2-recovery/README.md#final-verification--f023029).
This supersedes the older stage-1/initial Windows CI limits below. Actual
Windows/Ubuntu mini-PC hardware and service installation remain unverified.

**27 October current increment:** FEAT-009 stages 1–2 IN SOURCE: observer,
read-only local recovery review, guarded watchdog startup, per-checkout launcher
lease, Windows cmd and Ubuntu graphical-session service generation. Owner develops
on Windows and deploys to an Ubuntu mini PC; actual deployment/hardware pending.
Documentation-before-code / documentation-after-code is the primary rule.
Final local **869 run: 866 PASS, 3 optional model SKIP, 0 failures/errors**;
47 focused PASS, 16 API/Sandbox PASS, native launcher and systemd unit verification
PASS. No automatic restart, replay, service installation or commercial release.
[Stage-2 scope, reviewed sources and evidence](qa/portrait-v2-recovery/README.md).

**Historical stage-1 checkpoint (superseded by stage 2 above):**
optional external heartbeat observer and Windows startup generator. Automatic
restart/recovery and startup installation remain unimplemented. Device acceptance
is deferred by owner; no remote-source CI claim. [Current scope/evidence](qa/portrait-v2-watchdog/README.md).
Focused checks and native launcher lifecycle pass; complete regression remains
NOT VERIFIED because API/Sandbox fixtures stall (isolated Sandbox: six failures).

## Drive layout and QR source correction (26 October 2026)

Numbered Photo folders, flat raw/bw/color uploads and verified link-sharing acknowledgements are implemented in the repair source. Actual installed deployment, cloud upload and signed-out phone scan remain pending.

Updated **26 October 2026** after documentation baseline `f36ebad` on
`feature/portrait-kiosk-v2-next`. Latest functional source **53e7b4c** is the coordinated [storage integration](qa/feat-004-storage/README.md), after mirrored v2 **fc26e3d**, following BUG-009 diagnosis `887ba39`, tutorial entry `20453fe` and print/Drive `266b2c8`.
The earlier **`9433010` / `0dc6555`** pair is the P5 source/evidence baseline,
not the latest operator checkpoint. GitHub's default remains `master`.

IN SOURCE means implemented; VERIFIED AUTOMATED means a recorded source-specific
check passed; OWNER-REPORTED means a physical observation with the recorded
metadata limits; PENDING/NOT_RUN means acceptance has not been demonstrated.
None of these alone means production-certified or formally released.

**Owner flow refinement, 26 October:** idle no longer has a separate CARA PAKAI
button. Direct/invitation photo entry still requires the four-step tutorial for
a fresh visit, using the existing navigation/actions. [Current change and
validation](qa/portrait-v2-photo-entry/README.md).

**Latest owner retest, 25 October:** targeted R01–R04 **4/4 checked**, zero
unchecked and no issue notes. BUG-018 moves to **OWNER-REPORTED PASS / MONITORING**:
rapid/mixed clicks, close while busy, reopen/minimize and next input/restart are
reported working. Preserve the earlier contradictory raw 8/8/hang report.
Tested HEAD/device fields remain unknown; no exact-source verification, formal
closure or external P5 acceptance is inferred. No new runtime patch is needed.
[Reports and correction](qa/portrait-v2-health-clicks/README.md).

| Feature | Current GUI v2 source | Evidence and boundary |
| --- | --- | --- |
| Advertising/tutorial/twelve templates | Responsive media, inline invitation, tutorial once per visit via photo entry (no separate help button), swipe gallery, native captions and animated header | Source screenshots; final owner visual/audio 8/8 at unknown HEAD; later entry refinement has its own source checks |
| Camera/face/optional palm | Async camera and preview, display-only mirror, existing face/palm services; manual SIAP retained | Owner-reported preview/button/palm PASS and prior twenty cycles; missing source/device fields stay unknown |
| Capture/review/retake | Three original photos/design, one retake/design; v2 review and photo areas in the shared result/print/digital PNG mirror | Raw JPEGs retain original orientation/resolution; template/text/QR and v1 defaults stay normal. Old outputs unchanged; quantity means copies, not more sessions. [Mirror proof/form](qa/portrait-v2-mirrored-output/README.md) |
| Audio | Single v2 owner; GUI loop for still ads/photo journey, video's own audio, distinct game loop; one cue per action | Owner-reported normal. BUG-017 is monitoring after the later report, not a proven decoder fix; v1 BUG-001/007 stay separate |
| Thermal photo printing | Existing v1 backend/config; --print auto-sends one durable batch per approved design, --manual-print optional; uncertainty/no-replay guards | New-source fixtures pass; actual current paper/copy/QR acceptance pending. Prior owner paper reports stay at unknown HEAD. Merchant trial forces printer off |
| Drive/download | --drive resumes existing isolated queue on startup/after visits; offline-safe admission, background binding/retry and large verified on-screen QR, original retention guard | New-source fixtures/pixel decode available; actual phone access/offline/restart and cloud deletion unverified. Default local; merchant trial off. BUG-009 OPEN |
| BUG-009 retention activation | Reused v1 setup/cleanup; real CLOCK required for active registration ACK, incorrect trigger setup repaired; read-only redacted CLI/status and eight-item Submit form | 807 full Python PASS/zero skips; 19 actual-Code.gs VM PASS. Owner setup/deployment unconfirmed. Google timer/deletion NOT_RUN; bug stays OPEN. [Guide/evidence](qa/bug-009-retention/README.md) |
| Meong Fly — FEAT-021 (game) | Original Stage/Flow/renderer/assets/emitter reused; persistent one-use v2 DEMO ledger | 26 reference files pinned to `672e3f7`. V2 uses manual DEMO entry; standalone camera scanner is not mounted |
| Local MOCK checkout | Local SQLite quote/promotion/admission; nonpayable QR and simulated confirmation | Win discount Rp2,500 once per order, capped at subtotal; no bank settlement |
| FEAT-020 QRIS Sandbox | Reused service/client/journal plus native v2 adapter/isolated launcher | Server quote, provider verification, one-use grant/ACK/recovery in source. Actual merchant simulator evidence pending; no trusted game-promo API |
| P5 readiness | Read-only CLI, safe metadata JSON, 26-item Submit/import form, rollback package | Owner preflight `0dc6555` = READY_FOR_MANUAL_TEST, not hardware/provider PASS |
| FEAT-008 operator Device Health | Original v1 backend/panel/worker reused with small v2 adapters and safe report export | Later R01–R04 owner retest 4/4, no issues: BUG-018 monitoring at unknown HEAD/device metadata. Selection/switching disabled |
| Other reference features | Device staging/switching, AI Background Studio, WhatsApp, newer dithering lab | Separate branches; not automatically in v2. [Reference map](gui-v2-branch-audit.md) |
| FEAT-004 ads + BUG-009 booth storage/content | Ordinary v2 launcher uses PB00X roots, 25 empty reserves, Photo/NN/raw,color,bw, saved 1-bit print and verified global/local caches; Code.gs supplies scoped reservations/binding/content/cleanup | 824 full local PASS/zero skips, 24 Code.gs PASS, matching three-job CI SUCCESS; [stage package](qa/feat-004-storage/README.md). Actual Google setup/deploy, phone/paper and deletion NOT_RUN. BUG-009 stays OPEN until real expiry evidence |
| Production payments, merchant POS/scanner, trusted QRIS promo | Disabled/not delivered in v2 | Require their own approved scope, trust contract and acceptance |

## Latest recorded automated evidence

| Checkpoint | Local full regression | Matching-source CI | Screenshot evidence |
| --- | --- | --- | --- |
| Mirror source `fc26e3d` | **808 PASS / zero failures/errors/skips**, 230.670s; earlier focused 42 PASS, renderer/template 19 PASS | [40263151709](https://github.com/pratikto/PhotoBooth/actions/runs/40263151709), all three jobs SUCCESS; native 103 PASS/one optional model-assets skip covered locally | Sixteen clean-source native captures verified, eight selected views and two form views reviewed at required sizes. Actual paper orientation NOT_RUN. [Proof](qa/portrait-v2-mirrored-output/README.md) |
| Storage/content source `53e7b4c` | **824 PASS / zero failures/errors/skips**, 241.156s; 24 Code.gs VM PASS; cold ordinary launcher offline PASS | [40273343183](https://github.com/pratikto/PhotoBooth/actions/runs/40273343183), all three jobs SUCCESS; optional CI model skip covered by the full local run | 133 CI PNGs / source reports checked; 28 final native captures + two form views published. [Proof/setup/checklist](qa/feat-004-storage/README.md). No cloud/paper/phone acceptance inferred |
| BUG-009 source `887ba39` | **807 PASS / zero failures/errors/skips**, 238.684s; 44 focused Python and 19 Node VM PASS | [40255716011](https://github.com/pratikto/PhotoBooth/actions/runs/40255716011), all three jobs SUCCESS; native 103 PASS/one optional model-assets skip covered locally | No main GUI layout change; four native CI and two form views reviewed at 800×1280/452×900, 360px form overflow check; [proof](qa/bug-009-retention/README.md). Fixtures are not Google acceptance |
| Photo-entry source `20453fe` | **800 PASS / zero failures/errors/skips**, 217.888s | [40248962384](https://github.com/pratikto/PhotoBooth/actions/runs/40248962384), all three jobs SUCCESS; native 103 PASS/one optional palm-assets skip covered locally | Twelve clean-source PNGs hash/dimension verified; six affected idle/invitation/tutorial views reviewed at both required sizes; [proof](qa/portrait-v2-photo-entry/README.md) |
| Print/Drive source `266b2c8` | **800 PASS / 0 failures / 0 errors / 0 skips**, 213.823s | [40208966127](https://github.com/pratikto/PhotoBooth/actions/runs/40208966127), all three jobs SUCCESS; delivery 17 PASS, health 80 PASS, Sandbox 139 PASS, native 103 PASS/1 optional model-assets skip | 133 PNGs verified; delivery views reviewed at both sizes, large QR screenshot pixels decoded; [proof/form](qa/portrait-v2-print-drive/README.md) |
| BUG-018 source `ebb53fd` | **785 PASS / 0 failures / 0 errors / 0 skips**, 321.181s | [40189694738](https://github.com/pratikto/PhotoBooth/actions/runs/40189694738), three jobs SUCCESS; health 80 PASS, Sandbox 139 PASS, native 97 PASS/1 optional model-assets skip | 119 PNGs source/hash/dimension verified; operator views reviewed at 800×1280/452×900; [proof](qa/portrait-v2-health-clicks/README.md) |
| Operator source `ea394e8` | **780 PASS / 0 failures / 0 errors / 0 skips**, 270.671s | [40157638369](https://github.com/pratikto/PhotoBooth/actions/runs/40157638369), three jobs SUCCESS; health 80 PASS, Sandbox 139 PASS, native 92 PASS/1 optional palm-model-assets skip | 119 PNGs source/hash/dimension verified; required views reviewed; 15 local operator PNGs reviewed |
| Earlier P5 source `9433010` | **688 PASS / 0 failures / 0 errors / 0 skips**, 211.646s | [40109206417](https://github.com/pratikto/PhotoBooth/actions/runs/40109206417), three jobs SUCCESS; native includes one optional palm-model-assets skip | 109 PNGs source/hash/dimension verified; required views reviewed |

The optional CI model case is covered by each recorded local full run with
supplied assets. Three successful CI jobs do not mean zero skipped cases.
These are Linux/software-GL/dummy-audio/offline-fixture results, with the Windows
CI audio job also using dummy output. They are not physical acceptance.
[Operator proof](qa/portrait-v2-operator-health/README.md) · [P5 proof](qa/portrait-v2-p5/README.md).

## Outstanding acceptance

Use the [49-item consolidated outstanding checklist](qa/portrait-v2-pending-acceptance/windows-checklist.html)
for current-build Windows/paper/Drive/cache/retention, real Sandbox/recovery
and privacy review. It retains earlier owner passes; only the existing NEW
Sandbox integration gate requires twenty cycles. Import never checks tests.
[Scope and instructions](qa/portrait-v2-pending-acceptance/README.md).

P5 is ready for acceptance, with current Windows integration, actual merchant
Sandbox, physical paper/uncertain-job handling, Drive/download/offline/cloud
retention, privacy and release signoff still awaiting complete evidence. Keep
prior owner reports at their known or unknown tested HEAD; never attribute them
to a newer commit. Safe approved source work continues independently of laptop
availability. [Test ledger](test_checklist.md) · [bug register](bug_tracker.md).

## Historical record

The [pre-audit version](https://github.com/pratikto/PhotoBooth/blob/5f09eff9998c942ed54feef0cf0563fc3944611b/docs/FEATURE_STATUS.md) preserves the complete dated history. Its former “current”, approval, branch and next-step statements apply only to their recorded stage. Use the current documents linked above for continuation.

