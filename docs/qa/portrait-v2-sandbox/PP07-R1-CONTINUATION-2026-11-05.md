# R1 durable continuation — 5 November 2026 (Asia/Jakarta)

> **Final R2 verification:** [source-matched campaign](PP07-EXECUTION-CAMPAIGN-R2-2026-11-05.md) at 17f7863: 1,766 all-opt-in local PASS; CI 41944005227 all 3 SUCCESS (563 Windows/563 Ubuntu/67 native), zero failures/errors/skips. Windows protected mock service restart is verified after original local ACK; full pre-ACK worker/device/Ubuntu/merchant/refund acceptance remains separate. Next boundary and exact evidence are in the campaign; historical pending notes below are superseded.

> **R2 supersedes pending broad-regression notes:** [exact-source 3825473 execution](PP07-EXECUTION-CAMPAIGN-R2-2026-11-05.md): 1,760 local PASS, zero failures/errors/skips including all three real-model methods; CI 41930961409 inspected 557 Windows / 557 Ubuntu / 67 native PASS. Protected original-worker restoration remains next; full owner/provider/refund acceptance is unchanged.

> **Latest checkpoint K supersedes all RUNNING notes below:** fec4f7f broad
> regression completed 1,760 run / 1,756 PASS / 1 FAIL / zero errors / three
> model SKIP in 1,141.769s. The failing delivery idle-helper case is preserved.
> Test-only repair removes its trailing idle poll (which can start a normal
> periodic snapshot); all 11 delivery-widget tests PASS, unchanged five-second
> bound. Controlled deadline reproduces before / PASS after; precise original
> full occurrence cause remains unproven. Runtime remains fec4f7f, successful
> CI 41927170321 remains exact runtime evidence. Next: immediately push checked
> increment K and run the broad opt-in suite alone at its new test source.
> No active local test process at this checkpoint; no full acceptance promoted.

> **Latest verification:** fec4f7f CI 41927170321 is now COMPLETED 3/3 SUCCESS:
> 557 Windows, 557 Ubuntu, 67 native PASS; zero failure/error/skip; all logs
> inspected. The local broad run/session 72311 remains RUNNING, not PASS yet.
> Next: read full-final-r1.log/full-final-report.txt and publish its actual result.
> This supersedes Windows-pending notes below; previous failures/cancellations
> remain historical. [CI evidence](evidence/pp07-ci-final-r1-2026-11-05.json).

## Latest checkpoint — BUG-044 source fec4f7f supersedes the active-job notes below

Last remote independently verified:
`fec4f7f9d3169d1421a704813d83355bee12f4d1`.
BUG-044 native recovery action is repaired: two initial FAIL, complete checkout
widget module 17 PASS. An explicit original retry recovers an unsent checkout;
the existing backend never repeats SENT/UNKNOWN POST and QR3 cannot offer QR4.
Runtime/test source is now **fec4f7f**, not 36ec0cc/2ac2380.

Final source-matched actual-time replays both PASS: 452x900 **30.031s** visibility
while a 45s virtual receipt remains in flight (94.168s total); 800x1280
**30.024s** visibility (79.731s total). Both retain one charge/receipt, 2+1 copies
and OWED/no physical paper claim. No competing probes/replays run during the
final broad regression.

**First unfinished action:** finish full source **fec4f7f** verification.
[CI 41927170321](https://github.com/pratikto/PhotoBooth/actions/runs/41927170321):
completed log inspection confirms Ubuntu **557 PASS** / native **67 PASS**,
zero failures/errors/skips; Windows still pending. No 3/3 claim yet.
The local final broad run began **2026-11-05 05:43:59 Asia/Jakarta**, current
shell session **72311**, process **18784**, same selected task venv/checkout.
Read `full-final-r1.log` and `full-final-report.txt` under current task scratch.
No summary means no result. Exact next command in this environment:

```bash
tail -30 /workspace/work/pp07-evidence/full-final-r1.log
```

The earlier local 2ac2380 retest was **SUPERSEDED/CANCELLED** without a summary;
its CI 41924955940 was cancelled by this necessary runtime push. Neither is
PASS nor product failure. Keep the first 1,757-run ERROR and all controlled
diagnostics in history. The 16 new methods across R1 do not represent 16 full
acceptance cases. All owner/device/provider/refund/legal gates remain separate.
Do not start another large feature until this verification is recorded/pushed.

The dated checkpoint below remains historical. Current environment session IDs
and scratch paths are not portable; if absent, use the committed source and
source-specific CI before reconstructing an unfinished run. Local-only raw logs,
venv and PNGs remain uncommitted; source/tests and sanitized evidence are remote.

---

**IN PROGRESS; do not infer a complete local PASS.**
Authorized existing branch: `feature/post-preview-qris-checkout`.
Last independently verified remote before this documentation checkpoint:
`2ac2380e53e7738de59220f756bd46770565535a`.
Runtime implementation remains that of `36ec0cc83f65940bd78e8865c0ded6329a2522e3`;
2ac2380 adds only the guarded positive-fixture setup repair/new regression.

Read [the execution report](PP07-EXECUTION-CAMPAIGN-R1-2026-11-05.md),
[versioned 188-case register](evidence/pp07-execution-register-r1-2026-11-05.csv),
[run ledger](evidence/pp07-execution-r1-2026-11-05.json) and
[complete execution specification](PP07-CODEX-TEST-EXECUTION-PROMPT-2026-11-05.md).
Original historical register, all full acceptance criteria and 14 AR gates remain
preserved. No actual provider/refund/paper/cloud/production activation.

## Completed and remotely recoverable

- BUG-043: stencil-clipped private QR/code cannot record a genuine CCP/ticket
  offer. Initial two FAIL, corrected affected scope 68 PASS.
- Original settlement/presentation-journal remedy assessment, nonbinding and
  read-only, no customer endpoint or money/media authority: six new methods;
  affected 80 PASS. Never-offered PAID is remedy, not customer negligence.
- Four independent hard-exit/reopen isolation barriers: affected 26 PASS.
  Local PREPARE/ACK/worker/rollback evidence, not full protected worker restore.
- Two default actual-event-loop replays: 452x900 30.002s visible / 96.553s total;
  800x1280 30.008s visible / 79.353s total. Slow virtual receipt replay:
  33.207s visible / 95.080s total, card wiped while 45s receipt still in flight.
  All retain one charge/receipt, exact 2+1 copies and OWED/no physical claim.
- Five repeated J21 methods: 60 synthetic visits in 237.048s; resource data is
  sampled, not multi-hour qualification or performance acceptance.
- Source 36ec0cc [CI 41920786730](https://github.com/pratikto/PhotoBooth/actions/runs/41920786730)
  completed 3/3 SUCCESS: 556 Windows, 556 Ubuntu, 65 native; all logs inspected,
  zero failures/errors/skips. Original Apps Script syntax/Node VM and static
  synthetic pilot preflight PASS. Eight public synthetic preview PNGs rendered;
  no private proof screenshots.

## First unfinished action — finish exact-source retest verification

The first broad local run at 36ec0cc was **1,757 run / 1,753 PASS / 1 ERROR /
3 model SKIP**, 1,204.513s. Keep it in history. The error occurred before privacy
assertions when the positive fixture indexed an absent payment observation.
Five isolated repeats PASS; a controlled readiness expiry reproduces identical
TypeError with DraftHeld/zero charges. Original occurrence's exact cause remains
unproven. 2ac2380 allows one fresh retry only after proving the original attempt
was never SENT, and adds a same-attempt/one-charge regression. No production
freshness fence or assertion is relaxed. Focused corrected scope: 41 PASS.

Active work at checkpoint:

1. [New CI 41924955940](https://github.com/pratikto/PhotoBooth/actions/runs/41924955940),
   head **2ac2380**, is IN_PROGRESS, not PASS. Inspect all completed job logs and
   exact source/counts. Older successful CI is not this new test-source result.
2. Full GUI/audio/video local retest at **2ac2380** is RUNNING, without concurrent
   probes/replays. Current task shell session 52177, process 15241, checkout
   `/workspace/work/photobooth-pp07`, interpreter
   `/workspace/work/pp07-venv/bin/python`. Read
   `/workspace/work/pp07-evidence/full-retest-report.txt` and `full-retest-r1.log`
   once complete. No summary means no result. These paths/session IDs are only
   for the current environment and must not be assumed in a new account.

Exact next read in this environment:

```bash
tail -30 /workspace/work/pp07-evidence/full-retest-r1.log
```

If the environment/logs are gone, preserve the remote checkpoint and reconstruct
a clean checkout of the same authorized existing branch, without `old` or user
roots. Reuse/create a task-only Python 3.12 venv and install current requirements
plus QRIS/post-preview extras, constraining OpenCV below 5 like current CI.
Only if the unfinished result cannot be recovered, run the repository runner
with GUI/audio/video opt-ins, SDL offscreen/software GL and dummy audio, camera/
face/palm/live delivery OFF. Record all skips explicitly; do not fabricate the
missing summary or reset any occupied owner root. Stop starting large new tasks
until this verification and truthful register/checkpoint are pushed.

## Concrete remaining dependencies

- **Three native model methods:** session proxy denies `storage.googleapis.com`
  with CONNECT 403. Need approved network access to the pinned public model and
  samples, then MediaPipe 0.10.32 and independent SHA-256 verification using the
  existing full-simulation asset manifest. No proxy/TLS bypass or fake inference.
- **Protected original-worker restore:** full pilot composition remains absent;
  Ubuntu platform protector unsupported here. Need a supported provisioned OS
  vault and original worker/receipt/backend ACK/archive reconstruction. Windows
  DPAPI byte process tests are separate from device/reboot/reinstall restore.
- **Actual post-preview merchant profile:** requires guarded original-restoration
  composition, provisioned merchant credentials and authoritative provider/
  account/webhook evidence. The current synthetic launcher stays restricted.
- **PP-101/104–110/112:** eligibility/window/balance/account contracts, durable
  original refund intent/reconciliation, real worker fencing/status protocol and
  commercial/legal review remain missing. Candidate classification is not payout.
- **Physical acceptance:** camera/touch/speaker/POS80 paper/cuts, actual signed-out
  Drive ACL/download/retention and Windows/Ubuntu devices require independent
  observations. Proposed two-hour/four-hour soaks and budgets are not completed.

After retest verification, the first unfinished implementation boundary is the
supported protected original-worker restoration composition. Inspect the current
launcher, `credential_vault.py`, original claim/isolation and checkout services;
write a failing independent-process original-context restoration test before
mounting any real merchant transport. Preserve synthetic-only launch, occupied-
root refusal, original PAID/OWED, no uncertain print replay and scope/generations.
Never persist a plaintext key or invent provider/refund/TTL semantics.

## Local-only data and publication discipline

All source/test changes through 2ac2380 were immediately pushed and remote SHA
verified. Raw logs, venv/caches and preview PNGs under `/workspace/work` are
local-only, not recoverable from GitHub; committed numeric evidence/checksums,
scripts and CI links provide the portable record. No unfinished runtime patch
is being left local. Every later safe increment must likewise be checked,
committed, immediately pushed and independently remote-verified. No owner device
test is requested while independent verification is still running.
