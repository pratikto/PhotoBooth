# Meong Photobooth — GUI v2 development handover

## 29 October — published safe checkpoint through AR-09.c1

Exact tested/pushed functional source `b38e030d2a8586f2de61dd96e8b4a590e85dde54`; remote HEAD verified.
AR-07 native customer recovery and AR-08 readiness/paid remedy source increments
are locally verified. AR-09 PIN launcher/inspection and dormant service fencing
are locally verified; safe release/reacquisition remains unfinished. Latest 86
focused PASS, zero FAIL/ERROR/SKIP. Final full suite deferred; CI pending, external
Windows/Ubuntu/merchant/paper/Drive NOT_RUN. No production or release enabled.
[Ten commits, exact tests, blockers and continuation](qa/portrait-v2-sandbox/CONTINUATION-2026-10-29.md).
Next: AR-09.c2 two-phase audited release, token-aware service API, worker-stop ACK
and exact returning-customer lookup. Then AR-10–13. Tracked source clean before
this docs checkpoint; only disposable work/ local, no unpushed runtime patch.
Do not redo published work. Documentation checkpoint's own SHA is git HEAD.

## 29 October — AR-09.c1: fence stale service workers before implementing safe booth release

Base / last remote-verified commit `ed1612bd8f35d785d8c617db1343f9a0fc396f33`. Focused 86 PASS, zero failures/errors/skips; five migration/CAS/restart/race cases. Dormant internal seam only; no UI/API rotates fences and no booth release is enabled.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-09.c2 implement two-phase audited suspend/release and token-aware service API, then archived exact returning-customer reacquisition and native worker-stop/ACK; AR-10–13 remain pending.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATOR.md).

## 29 October — AR-09.b: mount PIN-protected native operator metadata inspection

Base / last remote-verified commit `cc6032c6556dbe4fcd2f26f8a32d9b611b948ed6`. Focused 64 PASS, zero failures/errors/skips; wrong/missing/correct PIN, private media denial, journal secrecy and retired callbacks covered. Twenty provisional native PNG fixtures rendered at both required sizes.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-09.c define and implement audited fenced suspend/release plus returning-customer lookup without losing OWED or allowing stale worker effects; then AR-10–13.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATOR.md).

## 29 October — AR-09.a: isolate a per-launch Sandbox operator PIN from the GUI

Base / last remote-verified commit `4e4f95b8396f585966c9e98e9fb7ebd3f06bb28e`. Focused 64 PASS, zero failures/errors/skips; backend-only PIN and mocked launcher argv/environment/local-notice isolation covered.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-09.b native operator PIN entry/metadata inspection, then audited fenced suspension/release without losing OWED or exposing previous photos; AR-10–13 pending.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATOR.md).

## 29 October — AR-08.b2: record native postpaid faults with durable same-operation retries

Base / last remote-verified commit `e84af128d296e4acae37132569e09f3f2da14049`. Focused 58 PASS, zero failures/errors/skips; postpaid missing-camera, capture I/O failure and lost-ACK/restart fixtures preserve payment, OWED, manifest and one issue operation.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-09 integrate separate operator PIN launcher/UI and safe fenced suspension/release; AR-10 bounded restart, AR-11 design/opt-in fixtures, AR-12 validation and AR-13 release gates remain.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-READINESS.md).

## 29 October — AR-08.b1: persist paid-unfulfilled issues without altering customer financial rights

Base / last remote-verified commit `4863aa3009d1c23e0b710ea9340db6a931a19623`. Focused 56 PASS, zero failures/errors/skips; five new durable/concurrent/migration/authenticated HTTP issue cases; CI registration included.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-08.b2 persist local reporting intent before API I/O, retry after restart and route native camera/photo faults into the ledger; then AR-09–13.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-READINESS.md).

## 29 October — AR-08.a: gate native new payment on camera storage and template readiness

Base / last remote-verified commit `d65fb97c7244d7aff8b0242d060a7de7c072bde1`. Focused 57 PASS, zero failures/errors/skips; offline readiness and native no-camera/no-order gates covered; new module registered in CI.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-08.b durable idempotent paid-unfulfilled issue ledger/API and native postpaid fault reporting; then AR-09–13.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-READINESS.md).

## 29 October — AR-07.b4: recover original pre-manifest allocation without creating another session

Base / last remote-verified commit `0745f754288d4ef58e07b93685209d619c796005`. Focused 42 PASS, zero failures/errors/skips; original RESERVED empty allocation recovery and STARTED/orphan denial covered in photo and native HTTP fixtures.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-08 prepayment camera/storage/template readiness and durable paid-unfulfilled remedy; then AR-09–13 in dependency order.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-NATIVE.md).

## 29 October — AR-07.b3: mount native ticket claim and customer-led exact photo recovery

Base / last remote-verified commit `7cedee5b0145720c9f1eaee04ab57ca8b183ec9c`. Focused 46 PASS, zero failures/errors/skips; native HTTP-to-photo restore, cached-camera ticket decode, minimize/idle privacy and input-preserving polling covered. Sixteen provisional fixture PNGs rendered at both target sizes.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: Finish AR-07 interrupted pre-manifest allocation handling and extra stale-callback/reboot fixtures, then AR-08 prepayment readiness and durable paid-unfulfilled remedy; AR-09–13 still pending.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-NATIVE.md).

## 29 October — AR-07.b2: hide private photo snapshots and fence reconstruction after lock

Base / last remote-verified commit `61571841786f5109f866157fe68e4c479d5c710f`. Focused 35 PASS, zero failures/errors/skips, including same-session reclaim and lock-during-reconstruction fixtures.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-07.b3 mount ticket claim/scan, exact restore and original ACK in native UI; wire minimize/60-second idle lock with stale callback guards.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-NATIVE.md).

## 29 October — AR-07.b1: revoke stale permits and acknowledge exact resumed service

Base / last remote-verified commit `6d53d91fcfcad6083aee9f17ac8f80cf635fdf2f`. Focused 37 PASS, zero failures/errors/skips; three added session cases cover privacy revocation, original STARTED acknowledgment/current refund and completed-result-only restore.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-07.b2 mount customer ticket input/scan and exact photo restore; add minimize/inactivity privacy lock and late native callback guards.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-NATIVE.md).

## 29 October — AR-07.a: native save-ticket gate and neutral privacy-held screen

Base / last remote-verified commit `064bf384f46a10eb9cf3d25cf94462feb463b626`. Two new native gates and focused 37 PASS, zero failures/errors/skips. Twelve native working-tree captures rendered at 800x1280/452x900; both recovery-ticket screenshot QR payloads decode correctly without logging secrets. Payment URL/copy actions remain hidden until ticket acknowledgment.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-07.b customer ticket input/scan, exact restore/STARTED handoff, inactivity/minimize lock and late-callback guards.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-NATIVE.md).

## 29 October — AR-06.b: memory-only customer ticket and trusted claim controller

Base / last remote-verified commit `c10998cace1c869139f17b55796ff3367e992054`. Six new session cases; focused 92 PASS, zero failures/errors/skips, including native Sandbox compatibility. Raw ticket never enters journal/backend views; restart requires original proof. Current settlement is rechecked at resume action, pending proof never issues media permission, and privacy generation rejects late callbacks.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-07.a native save-ticket gate before payment QR, then claim/scan/resume and privacy-lock integration.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CUSTOMER-CLAIM.md).

## 29 October — AR-06.a: hashed customer capability and current-payment redemption

Base / last remote-verified commit `adf87496479d4647b8248e8880acf691e87f8e38`. Eight new customer-proof cases and focused 137 PASS, zero failures/errors/skips. Additive capability binding is atomic with order; only SHA-256 persists. Expiry, durable attempt budget, one-use action replay and fresh settlement gate protect redemption without operator privilege bypass.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-06.b original-process ticket generation and private controller authorization; then native customer recovery AR-07.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CUSTOMER-CLAIM.md).

## 29 October — AR-05.b: exact private photo reconstruction behind one-use in-memory permit

Base / last remote-verified commit `3c04e31f56e5ed7e4fc30c971fc7ead28e1cc446`. Nine new reconstruction cases pass; focused 63 PASS plus nine final guard checks, zero failures/errors/skips. Restores partial shots, selected/used retake, staged captures/PNG and multi-design copies without new IDs, shutter, renderer or print. No old media is returned without a bound ephemeral permit; UI mounting remains disabled until AR-06/07.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-06.a hashed customer capability, expiry/action CAS/rate limiting and fresh-payment redeem API.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-PHOTO-RESUME.md).

## 28 October — AR-05.a: immutable strip publication with frozen input hashes

Base / last remote-verified commit `879d69bf4553e84befb21705033d9eb84759b571`. Three new output cases; focused 71 PASS, zero failures/errors/skips, including native handoff, capture, delivery and v1 retention/workflow. PNG intent and input identities persist before rendering; published-but-unacknowledged output cannot be overwritten on retry.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-05.b exact metadata/intent reconstruction behind an ephemeral resume permit; then AR-06 customer capability.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-PHOTO-RESUME.md).

## 28 October — AR-04.a: write-ahead immutable JPEG capture and atomic retake quota

Base / last remote-verified commit `075e97319762cfd73a089b444340fcf0eb2deb36`. Seven new capture cases, five abrupt process boundaries, and focused 73 PASS, zero failures/errors/skips. V2 opts in; v1 writer defaults unchanged. Existing/orphan JPEGs cannot be overwritten; retake selection/quota commit with saved bytes. Native Sandbox and retention checks pass.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-05.a output publication and deterministic manifest/intent reconstruction; customer disclosure stays gated until AR-06.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CAPTURE.md).

## 28 October — AR-03.b: unique allocation before local photo creation

Base / last remote-verified commit `4e0dadee16c3596d7575ee2ce2ed32a43bc0b7cf`. Focused 204 PASS, zero failures/errors/skips, including native HTTP-to-photo handoff, allocation replay/restart, initial binding, v1 workflow and retention. Server atomically assigns one PB001V2AR-style transaction before any folder creation; exact initial manifest binds original payment/permit.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-04.a write-ahead immutable capture intents and crash-boundary tests; then photo reconstruction AR-05.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-FULFILLMENT.md).

## 28 October — AR-03.a: frozen order contract and independent fulfillment obligation

Base / last remote-verified commit `30ebd0bad394046f99286b0f0f90785cb9e12161`. Six new fixtures and focused 133 PASS, zero failures/errors/skips. New orders freeze server pricing/template hashes before I/O; payment creates an owed fulfillment independently of UI claims. Legacy duplicate bindings quarantine both mappings without altering original evidence.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-03.b unique allocation operation and preallocated local transaction, then native handoff.
Only work/ scratch files local; scope and rollback in
[stage contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-FULFILLMENT.md).

## 28 October — AR-02.c: private restart observation and recovery worker retry

Base / last remote-verified commit `949d8e35c44f92d9a22c852df81dd3527ee041c6`. Focused 152 PASS, zero failures/errors/skips, including native Sandbox lifecycle. Four new restart tests and persisted priority-trigger test pass; RECOVERY retains original phase, grant and transaction and never resumes capture.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-03.a frozen quote/template contract and additive fulfillment/allocation migration tests.
Only work/ scratch files local; scope and rollback in
[AR-02 contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-RECONCILIATION.md).

## 28 October — AR-02.b: durable bounded reconciliation scheduling and fencing

Base / last remote-verified commit `877268f46d7360e4a6e3ef021862d93103d07f00`. Focused 126 PASS, zero failures/errors/skips. Fifteen new AR-02 cases cover cached evidence, concurrent workers, jittered backoff, stale responses, additive schema and clock rollback.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-02.c restart and existing RECOVERY observations without photo reentry, then AR-03 immutable fulfillment/allocation ledger.
Only work/ scratch files local; scope and rollback in
[AR-02 contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-RECONCILIATION.md).

## 28 October — AR-02.a: fresh payment observation and admission guard

Base / last remote-verified commit `6339d13817a74fcaf8c0ae3d76d9b73e73e2ed5c`. Nine new cases; focused 120 PASS, zero failures/errors/skips. Backend-only provider GET observation requires booth authentication; operator mutation remains PIN-gated. Cached PAID cannot authorize claim/STARTED without fresh settlement.
Full regression follows final functional change; physical Windows/Ubuntu,
merchant/print/Drive acceptance NOT_RUN. No repeat charge, production, private
photo display or customer state reset. Next: AR-02.b durable per-order reservation, bounded backoff and stale-reply fencing tests/implementation.
Only work/ scratch files local; scope and rollback in
[AR-02 contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-RECONCILIATION.md).

## 28 October — final verified AR-00/AR-01 handover

Latest functional source pushed and remote verified: `017b417d02d63a79b1c5b21c4f0613b7d15186fc`.
AR-00.a/b contract/baseline and AR-01.a/b attempt durability are implemented and
verified automatically. Focused **132 PASS / zero skips**; final complete local
**968 run / 965 PASS / 3 SKIP / zero failures/errors**, at that exact source. Optional skips require
external palm assets. Matching [CI 40688374416](https://github.com/pratikto/PhotoBooth/actions/runs/40688374416)
completed **all three jobs SUCCESS**, including Windows creation fixtures.
No actual merchant/Windows/Ubuntu hardware, paper/Drive/retention acceptance.

First unfinished step **AR-02.a**: deterministic tests for narrow booth-authenticated
fresh reconciliation of cached PAID/refund/offline, separate from operator resolve;
then rate-limited/backoff implementation. Read current checkpoint/source before
continuing. Do not repeat AR-00/AR-01 or enable repeat POST: Legacy provider
resend contract is still BLOCKED. AR-02–13 remain unfinished; new recovery GUI,
photo reconstruction, customer capability and unattended pilot are not delivered.
All source/tests and required evidence are on GitHub. Only disposable work/
scratch files remain local. [Checkpoint](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md)
contains rollback/data preservation and [evidence](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CREATION.md).
This final safe companion checkpoint is documentation-only; no extra GUI rerun.

## 28 October — AR-01 creation-attempt durability

AR-00 pushed/remote verified at `4261236694358c2f3cd2a475a4cd9cd82f436e00`.
AR-01.a/b adds a backend-only additive attempt ledger with frozen request and
merchant/mode binding before provider I/O; uncertain creation never retries POST.
Nine new attempt/migration tests plus baseline/protocol/HTTP group: **132 PASS,
zero failures/errors/skips** on Linux/Python 3.12.14. Initial failing tests are
recorded. Full regression/CI pending at this code checkpoint; source SHA will be
pinned after push. [AR-01 contract/evidence](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CREATION.md)
and [latest checkpoint](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md).
Next: full validation, then AR-02.a fresh reconciliation tests. Legacy repeat-charge
contract remains BLOCKED; independent stages may proceed without enabling resend.
Only work/ scratch files local; no customer data/credentials or unsafe WIP pushed.

## 28 October — AR-00 contract and crash-fixture checkpoint

Current owner continuation authorizes dependency-ordered AR work with immediate
safe pushes. Refreshed existing branch from clean remote
`f6736b7c739e3317e3bcc4506edb250f9e47d92b`; no new remote branch or master change.
AR-00.a/b freezes the actual schema/state/legacy fallback contract and adds six
offline characterization cases, including abrupt subprocess exit/reopen of WAL.
Focused suite **87 PASS / zero failures/errors/skips** on Linux/Python 3.12.14.
Runtime source unchanged; full/device/merchant checks NOT_RUN. Exact command,
changed scope, rollback and first unfinished AR-01.a are in the
[checkpoint](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md) and
[baseline contract](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-BASELINE.md).
Companion publication will pin the exact pushed AR-00 commit. Only scratch files
under work/ are local; no unpushed runtime work. Provider repeat-charge contract
remains open; no speculative resend/header or production activation.

## 28 October — owner preference: push in small increments for five-hour continuity

The owner explicitly asks Codex to **commit and push safe, tested
micro-increments continuously** rather than accumulating changes until a long
ChatGPT/Codex session finishes. Continue from remote-verified Git history
without redoing completed work after the five-hour limit. Follow
[checkpoint and resume instructions](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md),
[AR roadmap](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-ROADMAP.md)
and [development prompt](DEVELOPMENT_PROMPT.md). Each checkpoint must record
the last verified remote SHA, completed vs pending substeps, test evidence,
blockers and any explicitly **unpushed** local changes. Never push unsafe
source or sensitive values solely to manufacture a checkpoint. **No runtime
recovery implementation or new test verification is claimed by this change.**

## 28 October — autonomous recovery master design and Codex handover (no runtime changes)

Authoritative planning entrypoint: [Master](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-MASTER-PLAN.md), [Codex stages AR-00–AR-13](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-ROADMAP.md), [official Midtrans contract and open verification](qa/portrait-v2-sandbox/MIDTRANS-PROVIDER-CONTRACT.md), [fault-injection test matrix](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-TEST-MATRIX.md), [operator/customer runbook](qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-OPERATIONS.md). This documentation-only increment preserves the existing operator-first backend source; target policy is unattended-first when provider/payment, photo identity and customer ownership are independently proven. Five-minute invoice idempotency does **not** establish the same TTL/header for Legacy `/v2/charge`. No implementation, fixtures, live merchant or physical tests were run for the new plan. Codex must refresh remote HEAD and start at AR-00 on `feature/portrait-kiosk-v2-next`. No new branch or master merge.


## 28 October — Sandbox GUI link for the web simulator

Owner requests a GUI action to copy the current QRIS link for pasting into
Midtrans's simulator, keeping the existing branch. Source `39e8c32` adds
**SALIN LINK QRIS** and feedback using native widgets/Clipboard and the shared
URL validator. Backend/payment authority is unchanged. Exact checks and device
limits: [copy-link runbook](qa/portrait-v2-sandbox/COPY-LINK.md).

## 28 October — BUG-021 pending QR polling

Owner confirms image-only disappearance on the Sandbox page, with no duration
or status text. Reproduced pending action-URL overwrite and native image loss.
The shared backend now retains/revalidates saved URLs when actions are omitted;
no new order, endpoint guessing or relaxed payment guards. Source `4237d3f`:
182 focused PASS; full 933 run / 930 PASS / 3 optional palm SKIP / zero
failures/errors; CI 40614355442 all three jobs SUCCESS. Ten exact-source native
PNGs and two screenshot QR decodes verified; device limits/update in the
[runbook](qa/portrait-v2-sandbox/QR-POLLING.md).

## 28 October — centered Meong logo on Sandbox QR

Owner requests reuse of the Drive QR logo. The v2 adapter now calls that exact
renderer with locally decoded provider data, checks equivalence and retains
original pixels on failure. Renderer algorithm/artwork, download URL and payment
authority are unchanged. Source `8ed6f11`: 175 focused PASS; final full 926 run /
923 PASS / 3 optional palm-assets SKIP / zero failures/errors, 290.905s.
Matching CI 40610731638 all three jobs SUCCESS; 15 exact-source native PNGs and
three screenshot QR decodes. [Evidence/update](qa/portrait-v2-sandbox/QR-LOGO.md).

## 28 October — saved Sandbox credentials

Owner requests ignored local Merchant ID/Server Key defaults. The shared launcher
reads only the two Sandbox literal fields without executing local settings,
keeps environment-pair precedence and missing-value prompts, and forwards the
key only to the backend child environment. Existing Drive values/profile/payment
journals are preserved. Source `b496d9f`: all three CI jobs SUCCESS; 15 new cases
PASS on both Linux and Windows. Exact results and local-executor limits are recorded
in the [setup/evidence package](qa/portrait-v2-sandbox/LOCAL-SETTINGS.md).

## 28 October — BUG-020 Sandbox Server Key format

Owner's Sandbox dashboard shows `Mid-server-`; the launcher previously rejected
it locally. Both Server Key spellings are accepted without changing the fixed
Sandbox endpoint, credential isolation or payment authority. 136 focused protocol/
launcher checks PASS. Source `6a271de`: full local 901 run / 898 PASS / 3 optional
palm-assets SKIP / zero failures/errors; CI 40572395949 all three jobs SUCCESS.
Exact source, raw reports and update instructions are recorded in the
[correction runbook](qa/portrait-v2-sandbox/KEY-FORMAT.md). Actual merchant
authentication and simulator acceptance still need the owner's local test.

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

## Current delivery continuation

Owner-approved Drive/GUI improvement continues from fcabfbb. Background delivery
snapshots no longer lock result buttons/footer during rebuild. The strict
UPLOAD_COMPLETE QR contract and operator-disabled printing remain. Controlled
native regression PASS; actual five-minute delay is unmeasured.
[Scope, v1 comparison, evidence and rollback](qa/drive-delivery-performance/README.md).

**Final published checkpoint, 27 October:** FEAT-009 source `f023029` is on the
required branch; matching [CI 40423003641](https://github.com/pratikto/PhotoBooth/actions/runs/40423003641)
has all three jobs SUCCESS. Windows fixture connections are explicitly closed
before database replacement; production runtime is unchanged from `b99c613`.
Final local rerun: 869 cases, 866 PASS, three optional palm-assets SKIP, zero
failures/errors, 272.035s. [Final proof](qa/portrait-v2-recovery/final-verification.json).
Docs-first primary rule and Windows-development/Ubuntu-deployment direction
are persisted in AGENTS/protocol/prompt. Next: actual target-device acceptance;
automatic restart remains off and no service was installed.

## Current — 27 October FEAT-009 stage 2 and primary working rule

Owner requires comprehensive/careful documentation review before code, then
documentation updates after code. Persisted in AGENTS, protocol and continuation
prompt. Windows is development; Ubuntu mini PC is deployment. Continue on this
branch; read [stage-2 review/runbook](qa/portrait-v2-recovery/README.md) first.
Current source adds read-only recovery review, pre-GUI watchdog holds,
per-checkout launcher ownership and Ubuntu graphical-session unit generation.
No automatic restart, replay, service installation or production/deployment.

Remote refresh works with network permission; synchronized remote `a7815d9`
(includes Drive/QR repair `0bd69a9`) before rebasing the unpublished watchdog
checkpoint to `ae5c62a`. Do not undo the current cloud numbered-Photo correction.
The older source/ordering paragraphs below are dated historical checkpoints.
Initial stage-2 local regression: **869 run / 866 PASS / 3 optional palm-assets SKIP /
0 failures/errors**, 261.246s. Focused 47 PASS with site packages disabled;
API/Sandbox 16 PASS and actual native launch/pause/resume/lease/exit PASS.
Earlier HTTP stalls reproduce under restricted command-network access and clear
with network permission; no payment/fixture code patch was needed. Raw old
failures stay preserved. [Current evidence/limits](qa/portrait-v2-recovery/README.md).

Ubuntu mini-PC/Windows hardware, graphical sign-in/service start, paper, actual
merchant and Google deployment/retention acceptance remain NOT_RUN. No source
success grants release or closes BUG-009. Future FEAT-009 automatic recovery
requires a durable safe-idle contract; the current unit deliberately uses Restart=no.

**Historical stage-1 checkpoint (before stage 2):** user requests next roadmap
development while manual tests wait. FEAT-009 stage 1 adds an opt-in external
liveness observer and Windows startup-script generator. It never kills/restarts
the kiosk or replays fulfillment. Ordinary launch behavior is retained; merchant
Sandbox keeps its dedicated launcher. Base `5639400`; remote refresh currently
fails because the configured proxy is unreachable. No push/CI claim.
[Scope, commands, limitations, acceptance and rollback](qa/portrait-v2-watchdog/README.md).
Focused 22 PASS, package-free 15 PASS and actual native launcher lifecycle PASS;
full suite NOT VERIFIED (blocked in existing API TestClient), isolated Sandbox
widget checks 6 FAIL (`Worker did not settle`). Trace/raw reports preserved in
the runbook; no full-source certification or payment fix is claimed.
Earlier latest-source references below describe the prior committed baseline.

## Latest Drive/QR repair (26 October 2026)

Continue from the correction in docs/qa/drive-photo-layout/README.md. The earlier per-transaction-root cloud tree is superseded by owner instruction. The existing Web App needs a new deployment version; this session performed read-only Drive inspection only.

Updated **26 October 2026**. Repository `pratikto/PhotoBooth`; required branch
**`feature/portrait-kiosk-v2-next`**. Documentation baseline **`f36ebad`**, latest functional
source **`53e7b4c`** (coordinated per-booth storage/content; mirror `fc26e3d`, BUG-009 `887ba39`, print/Drive `266b2c8`). Refresh remote HEAD before continuing. GitHub's default is
still `master`; `main.py` launches v1. Do not restart the project or P3/P4 work.

## Latest requested acceptance checklist

Owner asks for every still-untested gate. The [49-item combined form](qa/portrait-v2-pending-acceptance/windows-checklist.html)
and [coverage/runbook](qa/portrait-v2-pending-acceptance/README.md) reuse the existing
offline Submit/metadata/persistence implementation. Prior passes remain recorded;
twenty cycles apply only to the existing NEW Sandbox gate. This is documentation,
not runtime/provider/production work or a newly reported device failure.

## Latest completed increment

**Latest owner instruction — FEAT-004 + BUG-009 implementation:** application
and Code.gs integration is implemented in the ordinary launcher: per-booth
25 empty local/remote reserves, Photo/NN/raw,color,bw, immutable offline claims,
verified global/local caches and original deadline retention. Foundation 76bb9a0
and backend 6e2f777 are pushed/verified. Final integration source/evidence and
setup/Submit checklist live in the [implementation package](qa/feat-004-storage/README.md).
Final source 53e7b4c has 824 full local PASS/zero skips, 24 Code.gs PASS and
matching three-job CI SUCCESS (40273343183); 28 final native PNGs verified.
Actual Google deployment/deletion, phone/paper and release remain NOT_RUN. Keep
all archive contents excluded and v1/Sandbox state isolated.

**26 October foldering audit:** owner asks to check current organization against
per-booth/25-reserve/Photo/NN/raw-color-bw/global-cache requirements and excludes
all contents of `old` from inspection/change. Owner selects continued local
photo/print when Drive/reserves are unavailable, with upload/QR later. The
[audited target contract](photobooth-storage-layout.md) is documentation, not a
runtime/cloud cutover. Existing source fixtures: 38 tests PASS plus controlled
two-session/three-copy/retake, native raster and pool checks. At that audit checkpoint the runtime
still had target 2 and its prior active paths; real Drive was not accessible. Do not
infer new-layout implementation or scan/migrate the archive from this audit.

Owner then clarifies that this target belongs to **FEAT-004 ads + BUG-009**.
Keep storage roots/reserves/session paths, shared content caches and retention
in one coordinated implementation sequence; content-sync success and actual
photo-deletion acceptance remain distinct. The earlier retention-only source
scope describes what was delivered then, not an exclusion of this new linkage.

**26 October mirrored outputs:** owner explicitly chooses mirrored review,
result/printed/digital strips. Source 977d26b extends the v1 compositor via a
default-off photo-only option; v2 opts in. Full-resolution original JPEGs and
detector inputs remain original; frame/text/logo/QR and v1 defaults stay normal.
One saved PNG serves result/print/Drive, no old output migration/replay. Source
fc26e3d corrects obsolete preview/consent wording found by screenshot review.
Final 808 full PASS/zero skips (230.670s); 42 focused PASS, all-twelve-renderer
checks pass. Sixteen clean-source native captures verified; eight selected
native and two form views reviewed at 800×1280/452×900. Matching-source CI
40263151709 has all three jobs SUCCESS; optional native model-assets skip covered
locally. Paper orientation NOT_RUN.
Use the fresh five-item Submit form; no extra twenty-cycle gate. Updated older
delivery P03 has a new storage key, preserving old answers without passing the
new orientation automatically. [Evidence/rollback](qa/portrait-v2-mirrored-output/README.md).

**26 October BUG-009:** owner explicitly resumes this previously deferred bug;
setup/redeployment not confirmed. Source 130aae1 repairs stale-flag ACK and
incorrect same-handler trigger setup, reusing v1 cleanup unchanged. Source
887ba39 adds one authenticated read-only status request/CLI with original private
configuration, redacted report and eight-item Submit form. Full 807 Python
PASS/zero skips, 44 focused PASS, 19 actual-Code.gs VM PASS; matching-source CI
40255716011 all three jobs SUCCESS, optional native model-assets skip covered
locally, four native and two form views reviewed at both required sizes. Original 15/30-day
clocks, v2 upload hold and deletion selection preserved. No Google deployment,
trigger write or actual deletion performed; BUG-009 remains OPEN until owning
account and authorized synthetic evidence. No ad sync/watchdog scope.
[Current guide, checkpoints and proof](qa/bug-009-retention/README.md).

**26 October owner flow refinement:** remove only idle CARA PAKAI; reuse the
existing Start/invitation/postgame tutorial gate and acknowledgement/reset rules.
Full-width UNDANGAN (DEMO) replaces the redundant split row. Source `20453fe`
has 800 full PASS/zero skips and twelve clean-source PNGs verified, six affected
views reviewed. Matching-source CI 40248962384 has all three jobs SUCCESS
(one optional native palm-assets skip covered locally). [Scope, exact
evidence and rollback](qa/portrait-v2-photo-entry/README.md). This does not start
retention/watchdog or any other backlog candidate.

**Owner-selected print/Drive continuation:** user postponed proposed watchdog
work and selected automatic print as v1 with background Drive. Stage 1 **7b691c7**
exposes launch options/contracts (29 focused PASS, matching CI SUCCESS); native
stage 2 **266b2c8** connects the existing durable print worker, startup queue resume,
verified-folder consent and large verified result QR. Nine original v1 backend
files are unchanged. Default local and dedicated merchant-trial boundaries stay.
Fifteen new-feature checks and 92 earlier native regressions pass. Final source
has **800 full PASS/zero skips**, matching-source CI 40208966127 all three jobs
SUCCESS and 133 verified PNGs; large screenshot QR decodes at both required sizes.
Actual paper/phone/cloud acceptance remains pending.
[Current print/Drive runbook and eleven-item form](qa/portrait-v2-print-drive/README.md).

**Latest owner retest / BUG-018:** targeted R01–R04 **4/4 checked**, zero
unchecked and no issue notes. Rapid/mixed buttons, busy close, reopen/minimize
and next input/restart are owner-reported PASS; move BUG-018 to **MONITORING**,
not formally CLOSED. Tested HEAD/device fields and specific display sizes remain
unknown. Preserve the earlier raw 8/8 plus hang note as the initial failure.
Delivered input guard `ebb53fd` has 785 full PASS/zero skips, 37 focused PASS,
matching-source CI 40189694738 all three jobs SUCCESS and 119 verified PNGs.
No new runtime patch or old twenty-cycle repetition follows this passing report.
Watchdog remains a proposed feature scope, not implemented by recording this retest.
[Raw reports, evidence and rollback](qa/portrait-v2-health-clicks/README.md).

Read-only operator Device Health now reuses the original v1 panel/backend and
extracted worker from **`dbbe055`**. Small adapters connect v2 scheduling,
cached-camera observations, audio/input lifecycle and redacted local reports.
F12 or a 1.5-second header hold opens it at idle; protected Sandbox RECOVERY also
allows observations. Selection remains disabled; no second camera, print payload,
automatic restart, order mutation or upload is introduced.

Recorded checks: **780 full local PASS / zero skips**; matching-source
[CI 40157638369](https://github.com/pratikto/PhotoBooth/actions/runs/40157638369)
three jobs SUCCESS, with one optional native model-assets skip covered locally;
119 PNGs verified. [Proof and eight-item operator form](qa/portrait-v2-operator-health/README.md).
These results predate this documentation-only reconciliation.

## Checkpoints

| Commit | Purpose |
| --- | --- |
| `d6fb5d4` | Visual/local baseline before Sandbox service imports |
| `37da798` | Reused QRIS service/client/journal; 124 original focused PASS |
| `ce603c2` | Native Sandbox → P3 handoff; 195 focused PASS; later full CI exposed a standalone hook regression |
| `9433010` | Corrected final P5 source/readiness/ACK guards; 688 full PASS |
| `0dc6555` | P5 evidence: matching CI, 109 verified PNGs; owner preflight later reported ready |
| `ae90269` / `fdafbe2` | Dated 19-branch audit / consolidated documentation baseline |
| `4c89e4f` | Reused v1 health foundation; 73 focused PASS |
| `ea394e8` | Mounted original health panel/worker and safe reports; 780 full PASS |
| `5f09eff` | Operator matching-source evidence/documentation |
| `f36ebad` | Completed English documentation consistency baseline |
| `ebb53fd` | BUG-018 fresh-press/repeat guard; final 785 full PASS, three-job CI SUCCESS |
| `edeec47` | Later BUG-018 owner 4/4/no issues at unknown HEAD; monitoring |
| `7b691c7` | Explicit print/Drive options and worker setup/QR contracts; 29 focused PASS |
| `266b2c8` | Native automatic print, background queue startup/resume and verified result QR; 800 full PASS, matching three-job CI SUCCESS |
| `20453fe` | Remove redundant idle help action; mandatory Start/invitation/postgame tutorial unchanged; 800 full PASS/zero skips |
| `130aae1` | BUG-009 real-CLOCK activation/setup correction and authenticated read-only backend status; 19 VM + 25 Python PASS |
| `887ba39` | Safe existing-config diagnosis/report and Submit form; 807 full Python PASS/zero skips, 19 VM PASS |
| `977d26b` | Mirror photo areas consistently via existing compositor; 808 full PASS, first matching three-job CI SUCCESS |
| `fc26e3d` | Preview/consent copy correction after visual review; final 808 full PASS/zero skips |

Use scoped inverse commits for code rollback after inspection; preserve all
payment journals, consumed attempts, reports, photo/print manifests and customer
data. Do not reset data to make an uncertain order disappear.

## Authorized continuation and acceptance

The owner's 25 October instruction permits safe approved source work while
laptop acceptance waits; it supersedes older “wait for P5 before any source work”
sequencing. The bounded health/report increment is completed. Additional feature
scope follows the owner's next instruction; do not treat the backlog as approval.
The English documentation audit completed at f36ebad. The next owner report
authorizes this BUG-018 correction; proposed watchdog work is not started.

- Preserve the [later operator 4/4 retest](qa/portrait-v2-health-clicks/owner-retest-2026-10-25.json)
  at unknown HEAD/device metadata; BUG-018 monitoring, no new patch while working.
  Do not impose another old photo/game twenty-cycle run.
- Collect the [P5 form](qa/portrait-v2-p5/windows-checklist.html) and actual merchant
  simulator evidence when available; the new Sandbox integration cycle checks
  are distinct from earlier photo/game reports.
- Owner preflight **`0dc6555` → READY_FOR_MANUAL_TEST** is recorded, but its JSON
  metadata/form were not supplied. Do not borrow missing device fields from older reports.
- Preserve owner-reported P3/visual/audio/game passes and BUG-012–017 monitoring.
  Investigate recurrence with evidence rather than patching reported-working paths.
- BUG-009 cloud retention is OPEN; owner resumed source remediation at 130aae1/887ba39.
  Use the new read-only diagnostic/activation guide; installed-account evidence is pending.
  V2 retention acknowledgement is an upload guard,
  not proof of deployed 30-day deletion. V1 BUG-001/007 are not closed by v2 audio.

## Implementation invariants

Reuse the actual original game Stage/Flow/render/assets/emitter (`672e3f7`, 26
reference files), QRIS service/client/journal (`3cc8a8e`) and health panel/worker
(`dbbe055`). Refresh relevant remote references before new reuse.

Preserve uniform game motion/spacing and centered world (BUG-015/016), native
readable main-button captions without mandatory icons, large animated Meong,
three original unmirrored captures and one retake per design. Quantity means copies.

Sandbox uses server quotes, independently verified status, a one-use grant,
durable STARTING before allocation and STARTED ACK before countdown. Pending,
unknown or paid states cannot be discarded by browsing timeout. No trusted QRIS
game-promo contract exists; require full-price/no-promo consent. Dedicated merchant
trial keeps printer/Drive off. Local MOCK remains a simulation.

[Roadmap](portrait-kiosk-v2.md) · [source status](FEATURE_STATUS.md) ·
[technical contracts](portrait-kiosk-v2-technical-design.md) ·
[reference audit](gui-v2-branch-audit.md) · [promotion plan](gui-v2-promotion-plan.md) ·
[continuation prompt](DEVELOPMENT_PROMPT.md).

## Historical record

The [pre-audit version](https://github.com/pratikto/PhotoBooth/blob/5f09eff9998c942ed54feef0cf0563fc3944611b/docs/DEVELOPMENT_HANDOVER.md) preserves the complete dated history. Its former “current”, approval, branch and next-step statements apply only to their recorded stage. Use the current documents linked above for continuation.

