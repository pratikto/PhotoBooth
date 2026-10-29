# AR-13 — release-readiness assessment

29 October 2026 (Asia/Jakarta). Repository `pratikto/PhotoBooth`, existing branch
`feature/portrait-kiosk-v2-next`. This is an evidence assessment and acceptance
handoff; it grants no release, deployment, production payment or merge permission.

## Final AR-02.d verification — 29 October 2026

PAY-08 / AR-AUDIT-002 **SOURCE VERIFIED**. Functional source `e0dc59435772148be86449c55140d4b9be2f6364`:
**1117 run / 1114 PASS / 3 optional palm SKIP / zero failure/error**, 335.317s,
GUI/audio/video opt-ins, Python 3.12.14/Debian 13.6, SDL offscreen/software GL/
dummy audio. Native video PASS. Reader: 9 focused PASS; integration: 103 focused
PASS. Test/workflow-only portability source `c94696d243c6a345182857d28d249d2d01d7d05b`: **49 focused PASS**,
zero failure/error/skip, 1.389s Linux and 11.955s Windows CI.

[CI 40809459547](https://github.com/pratikto/PhotoBooth/actions/runs/40809459547)
at c94696d: **all three jobs SUCCESS**. Its application/tools Git trees exactly
match the full-run e0dc594 source. Tests differ only by explicit fixture lease
cleanup; no assertion changed. The full run is not relabeled as a c94696d test
run. Initial Windows missing-qrcode failure at 40808591124 is retained;
reader CI 40807439692 also succeeded. [CI steps/counts](evidence/pay08-final-ci.json).

**28 clean native PNGs / four QR checks PASS**, both 800×1280 and 452×900 at
c94696d. Dimensions/hashes/phase transitions checked; selected claim/resume/
capture/isolation layouts inspected. Raw ticket QR pixels/payloads/logs remain
untracked private work/; only safe verdicts/manifests/digests are published.
[Exact commands/trees/skips/digests/native hashes](evidence/pay08-final-verification.json).

Current matrix **45 PASS / 1 FAIL / 0 SKIP / 9 BLOCKED / 14 NOT_RUN**.
Overall AR conformity audit remains IN_PROGRESS; BUG-023/UX-13 denial audit OPEN.
Actual Windows/Ubuntu OS reconnection, merchant/provider, phone/paper/Drive/
retention/privacy/operations and release gates remain NOT_RUN/BLOCKED.
Unknown/unavailable OS hints fall back to existing polling; this is no universal
Internet/provider reachability guarantee. No production or future OPS activation.

Next dependency: **AR-03 CAP-01–05 exact allocation/STARTED process-exit fixtures**
plus PAY-18 lost service replies, then remaining retake/COMPLETE/disk evidence and
AR-09 denial audit. Never repeat completed charge/reconciliation work or clear
customer state. No unsafe unpublished runtime patch; only disposable work/ local.

## Historical verified source supplement — audit 4642841

Functional `4642841f3e99d8c74b4b379e24922a7ba3f614c9`: **1,100 run / 1,097 PASS /
3 optional palm SKIP / zero failure/error**, 364.124s; native video PASS.
Matching [CI 40790865010](https://github.com/pratikto/PhotoBooth/actions/runs/40790865010)
all three jobs SUCCESS. [Command/trees/digests](evidence/ar-audit-final-verification.json).
BUG-022 is fixed and regression-verified. Audit remains IN_PROGRESS: native
connectivity producer absent, BUG-023 denial audit OPEN. Current matrix
**44 PASS / 1 FAIL / 9 BLOCKED / 15 NOT_RUN**, no unattended commercial release.
Earlier f72fdbc full/native/CI evidence below remains historical. No device,
merchant, phone, printing, upload/deletion or release approval is inferred.

## Operator denial evidence — original audit qualification

At that original audit the matrix became **44 PASS / 1 FAIL / 9 BLOCKED / 15 NOT_RUN** after a direct
UX-13 denial probe. Wrong-PIN rate limiting works, but denied attempts are not
recorded in a durable operator audit. PIN limits are process-local; the persisted
customer-ticket attempt budget is a separate mechanism. Earlier wording claiming
persisted PIN attempts was incorrect and is corrected below. **BUG-023 OPEN**,
without an observed authentication bypass. [Evidence](evidence/ar-audit-pin-denials.json).
The original missing PAY-08 producer is now resolved by AR-02.d above. BUG-023
remains open and is not waived by a passing regression or controlled testing.

## Historical intermediate functional checkpoint — BUG-022

Increment 3 corrects a confirmed missing-COMMITTED-PNG hold defect; **61 focused
PASS**, final full/matching CI PENDING at publication. [Finding/source evidence](AR00-AR13-CODE-REVIEW.md#increment-3--confirmed-missing-output-reconstruction-defect-bug-022).
The f72fdbc full/native/CI evidence below is historical and is not reassigned to
this correction. Audit remains IN_PROGRESS and commercial release NOT READY.

## Historical payment audit supplement — before UX-13 reclassification

The payment conformity audit added PAY-06/PAY-21 exact synthetic evidence against
unchanged f72fdbc runtime: **116 focused PASS**, matrix now **45 PASS / 9 BLOCKED /
15 NOT_RUN**. [Review](AR00-AR13-CODE-REVIEW.md#increment-2--payment-crash-and-provider-response-evidence)
and [safe evidence](evidence/ar-audit-payment.json). The dated full regression,
CI, screenshots and baseline counts below remain their original evidence.
Audit is IN_PROGRESS; the CONDITIONAL decision and external gates are unchanged.

## Decision

**CONDITIONAL — proceed with controlled owner acceptance under the gates below.**
**NOT READY for unattended commercial release.** Software evidence supports
isolated offline/Sandbox acceptance with existing printer/Drive-off guards.
Unproven provider creation outcomes, missing exact fault windows, real device
behavior, merchant eligibility, privacy deletion, fulfillment/remedy policy and
operational ownership prevent a production-ready claim. A full-suite pass cannot
turn an unexecuted matrix scenario or real device into PASS.

AR-13's source-readiness assessment is complete when this report and its linked
evidence are published. AR-12 remaining acceptance/fault gaps and release approval
remain open. Do not restart completed AR stages or start OPS implementation.

## Historical f72fdbc assessment and verification summary

The remaining assessment below preserves the original f72fdbc baseline. Its
source/counts and then-open PAY-06/PAY-21 entries are historical; the latest
4642841 verification and audit qualifications above supersede those facts.

**1,097 run / 1,093 PASS / 4 SKIP / zero failures/errors**, 428.924s; `.venv/bin/python tools/run_kiosk_unittests.py` with GUI/audio opt-ins,
CPython 3.12.14 / Debian 13.6 / SDL offscreen / dummy audio, clean tracked tree.
[Matching CI 40767441201](https://github.com/pratikto/PhotoBooth/actions/runs/40767441201):
all three jobs SUCCESS at `f72fdbc53041dd785fbcf7d8ef6b8eb0c17dcc88`. Native 28 PNGs / four QR decodes PASS;
matrix **43 PASS / 0 FAIL / 0 SKIP / 9 BLOCKED / 17 NOT_RUN** (69 IDs).
The four full-run SKIPs comprise three optional palm-model assets and the subsequently verified native-video case; the matrix's zero SKIP
count refers to its scenario classifications and is a different denominator.

## Exact source and evidence authority

- Final application/test source: `f72fdbc53041dd785fbcf7d8ef6b8eb0c17dcc88`.
  This adds a bounded alternate OpenCV recovery decode. Previously final runtime
  was `635de92c0f8fba9189981ebf2f168bff8b7a52af`; `b5931c8ef2e3d7b800e024c38a653fef5b4b4a1e`
  only added CI diagnostics. Twelve subsequent owner commits through `e303cdf`
  were documentation-only. Test clock correction is `959264962bb4e64a8a4531a085676b55ad26e660`.
- [AR-12 validation](AUTONOMOUS-RECOVERY-VALIDATION.md) records historical failures,
  exact final command/counts, Python/OS and source/dirty metadata. At this assessment's initial publication, the prior 1094 / 1091 PASS / 3 SKIP report was unavailable in that review environment. A later [historical provenance supplement](evidence/historical-635de92-provenance.json) verifies the recovered original 635de92 report/digest and pinned source hashes. It remains separate older evidence; this f72fdbc final-source run retains independently captured provenance.
- [Final evidence summary](evidence/ar12-final-verification.json) contains safe
  counts, source trees, report digests, skipped-test names, native hashes/QR
  verdicts and CI job references. Raw local logs and synthetic ticket QR pixels
  remain private disposable scratch; no merchant/customer secrets are published.
- [The matrix](AUTONOMOUS-RECOVERY-TEST-MATRIX.md#executed-evidence-ledger--29-october-2026)
  assigns exactly one PASS/FAIL/SKIP/BLOCKED/NOT_RUN to every PAY/CAP/UX/WEB ID.
  PASS is limited to stated synthetic assertions. NOT_RUN retains supporting
  tests without falsely crediting an exact missing process-exit boundary.
- [Checkpoint](AUTONOMOUS-RECOVERY-CHECKPOINT.md) gives the exact unfinished step.
  Later docs commits do not revalidate runtime or require another complete suite.

## A. Financial safety

| Area | Evidence and observed source boundary | Remaining gate |
| --- | --- | --- |
| QRIS charge identity | Creation-attempt fixtures persist one order/key/cart/merchant fingerprint before POST; PREPARED/SENT child exits and accepted/lost-reply tests retain original identity | Real merchant behavior for never-received/lagging 404/uncertain creation NOT_RUN |
| Provider idempotency | Repeat create/concurrent backend fixtures send once; reconciliation uses original-order GET | PAY-22 BLOCKED: exact Legacy same-order POST/header/TTL/body mismatch contract unverified. No repeat POST activation; Invoice five-minute header is not this contract |
| Duplicate payment after restart | Durable original key, one create attempt, no replacement while ambiguous; multi-connection grants remain one | Real power loss, merchant cancel/settlement race and financial reconciliation on actual booth NOT_RUN |
| Payment authority | Backend verifies immutable amount/currency/order/merchant/type/reference and fraud semantics; customer GUI/QR never establishes settlement | Merchant credential/account eligibility and BI-SNAP requirement need provider/owner confirmation |
| UNKNOWN/PENDING | Unknown, missing, 404 and network errors hold original liability, bounded retry; pending QR/order preserved | PAY-08 actual connectivity-restoration event remains NOT_RUN; long outage operations not device-certified |
| PAID/refund/review | Fresh provider check before sensitive recovery; stale PAID/refund/outage denies new admission; late evidence fenced | PAY-06 exact evidence/pre-commit process exit and PAY-18 combined lost service replies remain NOT_RUN |
| EXPIRED/CANCELLED | Only verified provider terminal evidence closes payment path; cancellation race retains settlement | Actual merchant expiry lag and cancellation guarantees NOT_RUN |
| Credential separation | Fixed Sandbox transport, backend-only server key, distinct booth bearer/customer ticket/operator PIN; redirect rejection tested | Production provisioning/rotation/OS access controls/backups/security review NOT_RUN; no production credentials changed |
| Refund/compensation | No automatic refund, no fake paid cancellation or liability satisfaction; OWED survives archival/release | Business must approve merchant-supported remedy, eligibility, approver, SLA and dispute/legal policy before promising compensation |

Financial conclusion: source safeguards are suitable for controlled testing;
no source result certifies merchant behavior or resolves a real ambiguous charge.

## B. Customer fulfillment

| Area | Verified source evidence | Remaining gate |
| --- | --- | --- |
| Paid entitlement | Additive payment/fulfillment/issue ledgers retain OWED across close, restart, faults and operator release | No production records inspected; actual outstanding paid-but-unfulfilled count is UNKNOWN, not zero. Operator must reconcile before pilot |
| One identity | Unique order/grant/fulfillment/allocation mapping; concurrent/lost claim replay; exact archived-key lookup | CAP-01–05 exact allocation/STARTED child-exit windows not fully exercised |
| Original photos | JPEG intent/temp/staged/published/committed child exits; hashes/decoding, orphan/no-overwrite and bound reconstruction | Real filesystem power loss and Windows junction/filesystem behavior NOT_RUN |
| Retake/multi-design/copies | Restore 1/2/3 originals, selected/used retake quota, completed output and unfinished design/copies; no rerender/reprint | CAP-11–13 exact retake child exits and CAP-16 compose/COMPLETE boundary NOT_RUN; multi-design/retake native screenshot scenes NOT_RUN |
| PNG output | Four real output publication child-exit boundaries, hash/ACK visibility; Windows non-truncating writable fsync | Windows lacks Python directory-fsync equivalent; real disk/controller power loss still separate |
| Printing | Durable uncertain-send holds; no automatic replay; same output/copy obligations preserved | Dedicated merchant trial printing remains OFF. Actual copies/thermal output/uncertain-paper inspection NOT_RUN; printer-specific pre-charge gate unverified here |
| Drive | Existing immutable folder mapping, FIFO/retry/offline/retention fixture checks, no folder reassignment | Actual upload, signed-out phone access, retry after outage and 30-day deletion NOT_RUN; BUG-009 OPEN |
| Customer ticket | 256-bit capability hash, booth/order binding, bounded trial expiry/replay/rate limit, original customer proof; alternate decode preserves backend auth | Trial 24h ticket and 60s in-memory proof are not approved commercial support terms. Real phone/camera scanning NOT_RUN; older OpenCV without alternate remains fail closed with manual entry |
| Archive return | Two-phase operator isolation/ACK, preserved original photos/OWED, free-booth reacquisition and COMPLETED result-only guard | Physical restart/return-to-busy-booth/device acceptance and owner remediation policy NOT_RUN |

COMPOSED/COMPLETED GUI/service ACK does not prove all paper/cloud obligations
were delivered. Source intentionally does not erase OWED merely because a strip
was composed. Define actual fulfillment closeout and support responsibility.

## C. Privacy and security

| Area | Evidence | Remaining gate |
| --- | --- | --- |
| Next visitor privacy | Neutral restart/claim views; no old images without one-use in-memory permit; minimize/idle hides views and retires callbacks | Actual Windows/Ubuntu kiosk transitions, screen persistence, clipboard and OS access review NOT_RUN |
| Customer verification | Wrong/short/expired/replayed/cross-booth proof denied; fresh settlement and exact media binding required | Lost/stolen ticket support, consent, validity and privacy notice require owner policy |
| Credential roles | Customer proof cannot resolve operator action; booth bearer alone cannot unlock private media/operator actions | Production role-based admin identity/auth and secure provisioning NOT_RUN; future static Operator QR is not implemented |
| AR-09 PIN | Separate per-launch backend PIN, transient GUI entry, process-local PIN attempt limit, metadata-only inspection, exact audited successful action IDs | Local operator terminal is a deliberate trusted Sandbox channel; not a production remote-admin identity or hardware-security certification |
| Safe release/archive | PREPARE fences, serialized photo worker receipt, backend ACK before new visitor; archive exact key and original bytes | Actual operating procedures, authorized staff and ambiguous nonpaid-order abandonment path not universally certified |
| Logs/QR | Source assertions exclude raw ticket from journal/snapshots, PIN from argv/GUI env/reports; published evidence contains hashes/verdicts only | No exhaustive forensic audit of real device logs/backups or production secret rotation. Synthetic probes do not establish that all future logs are safe |
| Retention | Local 15-day/Drive 30-day original-clock/no-resurrection source tests; protected archive excluded | Actual owning-account deployed cleanup and approved synthetic deletion evidence absent. BUG-009 remains a release privacy blocker |

No real customer photos, merchant settings or databases were inspected or
changed. No real cloud deletion was performed. Access control and financial
audit retention require deployment-specific approval independently of photo expiry.

## D. Operational resilience

| Area | Source evidence | Limitation/gate |
| --- | --- | --- |
| Restart | Opt-in dedicated Sandbox supervisor; three abnormal exits/ten minutes, persisted 5/10/20s cooldown and original kernel leases | Observation-only defaults retained, no automatic live-process kill. Actual device restart/long soak/boot session NOT_RUN |
| No duplicate effects | Same-order reconciliation, unique grant/allocation, immutable captures/outputs and no uncertain print replay | Missing exact matrix fault windows stay NOT_RUN; no claim of universal exactly-once physical effects |
| Ownership/worker isolation | Durable service fencing/CAS, stale provider reply denial, one serialized photo worker, local isolation receipt and ACK | Cross-device distributed deployment and Android supervisor not certified |
| Offline | Local media/claims and deferred original Drive jobs preserved; safe bounded provider holds | A prolonged real outage, storage exhaustion and recovery under actual traffic remain NOT_RUN |
| SQLite | WAL/FULL, real PREPARE/ACK abrupt exits plus integrity_check, locked BEGIN rollback and preserved OWED | Not every write/fsync/ENOSPC/power-loss boundary covered; CAP-20 exact matrix requirement remains NOT_RUN |
| Portability | Linux/cloud and Windows hosted CI source checks, explicit Ubuntu startup paths | Hosted Windows Server/dummy audio is not actual Windows booth. SDL offscreen/Xvfb is not Ubuntu mini-PC installation |
| Diagnostics | Failure-first annotations now expose test/traceback/count; no assertions/tolerances removed | Historical Linux runner monotonic value and random failing QR were not logged; their exact historical triggers cannot be proved |
| Upgrade/rollback | Additive migration byte-preservation, legacy ambiguity held, current fence/token protocols | No production installed-data upgrade/rollback drill. Do not run old writers on protocol-1 media or remove fences to regain access |

The content-priority fixture is now independent of host uptime. Runtime's initial
content-check clock policy is unchanged; a newly booted host can defer that first
check until monotonic time 60. Recovery QR decode now tries one installed alternate
only after an empty primary result. No measured camera/phone latency guarantee
or universal QR recognition rate follows from the private 100-ticket probe.

## E. External acceptance and owner-executable checklist

Record exact Git SHA/dirty state, date, OS/Python/Kivy/OpenCV, screen size, device
models, launch command, actual observation and sanitized evidence per row. Use
existing [combined acceptance form](../portrait-v2-pending-acceptance/windows-checklist.html)
and the established Sandbox cycle gates; do not repeat unrelated old accepted cycles.

| Gate | Classification | Prerequisites and concise owner steps |
| --- | --- | --- |
| A01 Windows booth | NOT_RUN | Existing Windows environment/camera/display/storage; update feature branch with ff-only, run current preflight and isolated Sandbox, close/reopen/interrupt at pending/paid/partial capture/retake/release/return; verify no old media or repeated effects |
| A02 Ubuntu mini-PC | NOT_RUN | Intended hardware, graphical login, permissions and camera/printer; generate startup unit with real target paths, review/install separately, exercise boot/logout/restart/locks and verify original claims/media |
| A03 Android/tablet | NOT_RUN | Owner confirms target/build/lifecycle/permissions and printer transport; separately test rotation/background/relaunch/storage/camera. Desktop evidence is not a tablet acceptance result |
| A04 Physical camera | NOT_RUN | Actual camera; reject payment when unavailable/stale, disconnect after settlement, verify durable paid-unfulfilled issue, reconnect and resume with original proof/manual countdown |
| A05 Physical thermal printer | NOT_RUN | Configured ordinary local test profile, explicit print opt-in, synthetic output; check copy count/QR/orientation, disconnect during send, inspect paper, confirm no automatic resend. Never enable dedicated merchant-trial printing as a shortcut |
| A06 Real phone QR | NOT_RUN | Real phone display/camera and local trial ticket; scan both portrait targets under normal glare/distance, restart/claim/expiry/replay/wrong-booth cases; keep payloads private |
| A07 Drive delivery/access | NOT_RUN | Owner's configured existing Google project/account; verify two distinct synthetic sessions, actual hashes, signed-out phone access, offline/restart same-folder retry and unchanged original deadline |
| A08 Real retention/deletion | BLOCKED | Separate explicit cloud-deletion approval and designated synthetic expiring data; confirm deployed trigger/clock/parent scope, actual 30-day cleanup and access revocation. No deletion of customer or protected archive data |
| A09 Merchant Sandbox | NOT_RUN | Owner's existing Sandbox credentials and official simulator; create/status/settlement/cancel/late-settlement/outage/restart on same order, record redacted provider evidence and no duplicate charge/grant. Do not use bank/e-wallet or change merchant configuration without approval |
| A10 Public HTTPS webhook | BLOCKED | Separate infrastructure/merchant configuration approval, host/TLS/DNS, secure ingress/worker mount, monitoring/admin identity; then execute WEB-01–08. Offline inbox is unmounted and not a public endpoint |
| A11 Production merchant/API | BLOCKED | Merchant/provider eligibility, Legacy vs BI-SNAP decision, expiry/idempotency/refund/support terms and credential separation explicitly approved; production remains disabled |
| A12 Operational privacy/fulfillment/pilot | BLOCKED | Assign support/on-call/alerts/SLOs, approve ticket/compensation/retention/security terms, reconcile all outstanding paid liabilities privately, exercise backup/upgrade/rollback, then separately authorize bounded pilot and release |

No credentials/hardware/account/deployment are invented to close a row.
Unavailable external acceptance does not prevent safe independent AR source
work. It also does not authorize an OPS feature or public listener.

## Residual software evidence gaps and next action

The executed matrix deliberately retains NOT_RUN where a logical restart/exception
test is weaker than its specified exact child-process exit. First source-evidence
follow-up: PAY-06 provider-evidence/pre-DB-commit abrupt exit with WAL reopen,
fresh GET and no duplicate grant, then CAP-01–05 allocation/STARTED boundaries,
CAP-11–13 retake boundaries, CAP-16 COMPLETE ACK, CAP-20 write failures, PAY-21 oversized provider response and the
explicit connectivity/frozen-worker paths. These are evidence gaps, not observed
data-loss findings; no requirement is deleted to obtain a green readiness label.
Do not claim the entire fault matrix is verified until those cases run.

Before any commercial pilot, close all applicable payment/media/privacy P0
gates, execute A01/A02/A04/A06/A09 and privacy/fulfillment prerequisites, and
obtain an explicit owner go/no-go. A03 depends on whether tablets are actually
targeted; A05/A07/A08 require their separately opted-in operational profiles;
A10 is not required for current loopback simulator/polling acceptance but is
mandatory before claiming a production public callback. A11/A12 always precede
production. No automatic refund or release follows this report.

## Delivery, rollback and preserved future scope

Micro-commits `9592649` (test clock) and `f72fdbc` (bounded scanner) were pushed
and independently remote-verified. This report's containing docs commit is the
handover publication; inspect `git log`/remote for its SHA. No new branch,
master/default/release/deployment change or force-push occurred.

Rollback is a scoped inverse of the scanner change after review; `9592649` is
its preceding source reference, `e303cdf` the owner-doc baseline. Keep the test
clock correction where appropriate. Never reset/revert customer databases,
claim archives, counters, fences, JPEG/PNG bytes, payment/order/fulfillment/issue
ledgers, supervisor budget, print uncertainty or Drive mappings. Preserve
additive tables and quarantine ambiguous old writers; no effect replay.

All five [approved future Settings documents](../portrait-v2-operator-settings/README.md)
remain byte-identical to the owner baseline. OPS-00–10 and QRIS Payment Slip
implementation remain NOT_STARTED; exact future tabs remain Device Health /
Audio Settings / Emulate Ticket, static per-booth QR at Advertising AND SAFE_IDLE,
separate AR-09 PIN and private customer ticket. No future feature was implemented.
