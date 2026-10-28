# Repository working instructions

## Primary rule — documentation before and after code

Owner instruction, 27 October 2026: **Before changing any code, read the
documentation thoroughly, comprehensively and carefully. After changing code,
update the documentation. This is the primary working rule.**

Read the documentation index and all current authoritative documents relevant
to the work, including handover, architecture, decisions, feature/bug status,
roadmap, protocol, specifications and acceptance evidence. Follow linked
contracts that affect the change; reconcile later owner corrections with dated
historical guidance before editing. A keyword search or a quick skim alone is
not sufficient. Record the sources reviewed and keep code, behavior, tests,
limitations and continuation instructions synchronized in the same delivery.
If the scope changes, review the additional documentation before further code.

Platform clarification, 27 October 2026: development runs on **Windows**;
the intended mini-PC deployment runs on **Ubuntu**. Support both where relevant.
Do not treat Windows-only startup files or Windows test results as Ubuntu
deployment acceptance. Startup generation must use explicit target paths when
the developer and deployment machines differ.

Latest owner correction, 26 October: Google Drive photos must be at
`Photobooth/PB001/Photo/00000001/{raw,bw,color}` and subsequent numbers.
This supersedes the older transaction-root/Photo/NN cloud contract below.
Keep internal IDs/local journals intact; see docs/photobooth-storage-layout.md
and docs/qa/drive-photo-layout/README.md. No live Apps Script deployment follows
from source publication; installed cloud activation is separate.


## Excluded archive and requested storage target

Owner direction, 26 October: ignore **all contents of `old`**. Never inspect,
modify, delete, migrate, import or include it in discovery/sync/retention. Prune
it before descending directories; do not use it as a reuse source. Current
foldering audit/target is documented in docs/photobooth-storage-layout.md: per-booth
roots, 25 READY transactions, Photo/NN/raw/color/bw and global/local asset caches.
That document distinguishes the requested target from the current runtime;
the audit did not implement or perform a path/cloud cutover.

Owner clarification: that requested layout/global-local offline cache belongs
to **FEAT-004 ads + BUG-009** as one coordinated workstream. Align booth roots,
25-slot reserves, Photo/NN/raw-color-bw, content sync and retention before a
cutover; keep asset-sync and actual photo-deletion evidence distinct. Earlier
retention-only increments did not implement sync. This scope linkage is
documentation, not a completed source implementation or cloud deployment.

The owner then explicitly requests implementation in the application and
Code.gs, not only documentation. Proceed through the coordinated contract on
the same branch, with tested staged pushes. Track delivered source in
docs/qa/feat-004-storage/README.md. Keep archive exclusion, v1/Sandbox isolation,
no print/charge replay and no automatic live Google deployment/deletion.

## Reuse existing working features first

Owner instruction, 2026-10-24: **Do not reinvent the wheel or waste GitHub
Actions credits on work that already exists and works.**

- Before implementing a feature, inspect the current code, roadmap, recent
  commits and relevant feature branches. Verify the latest remote reference
  HEAD; read other branches without switching, merging or changing them.
- Reuse the existing implementation, assets, renderer, animations and tested
  behavior when a similar working feature exists. Reusing just an engine while
  independently recreating its GUI does not meet this requirement.
- Prefer direct imports and small integration adapters. Record the source SHA
  and any necessary differences. Write a new implementation only when concrete
  compatibility evidence shows reuse cannot satisfy the approved requirements.
- Responsive gameplay must preserve displayed speed and wave spacing across the
  whole flight path. Unchanged physics alone is insufficient; test rendered
  motion. Do not scale far and near positions differently (BUG-015). Check player
  position at portrait and landscape sizes too; center the complete world
  instead of right-aligning it to the physical spawn edge (BUG-016).
- Keep existing safety and lifecycle guards when integrating; reuse does not
  authorize production payments, discounts, scanners, deployments or merges.

## Mandatory incremental Git checkpoint policy — owner preference, 28 October 2026

The owner prefers **small, frequent Git commits AND pushes** because ChatGPT/Codex
work sessions can end at a five-hour usage limit. A locally committed change that
was never pushed is **not** a reliable cross-session handoff.

- Split each approved implementation stage into independently reviewable
  **micro-increments** (for example: one contract/test, one backend invariant,
  one GUI seam), with explicit expected tests and rollback boundary.
- After **every meaningful, safe, locally checked increment**, commit and push
  immediately to the already authorized `feature/portrait-kiosk-v2-next` branch.
  Verify the remote branch HEAD equals the local pushed commit before proceeding.
  Do **not** accumulate all work until the end of an AR stage or a long chat.
  Aim for a checkpoint every ~30–45 minutes of active work where a meaningful
  change is ready, rather than making empty/time-based commits.
- Before the conversation/context window or five-hour usage limit interrupts
  work, **stop starting new large tasks**. Push all safely isolated, reviewed
  increments, then publish an accurate continuation checkpoint in the project's
  handover and the [autonomous recovery checkpoint](docs/qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md).
  Record stage/substep, commit SHA, changed files, focused tests and
  PASS/FAIL/SKIP/NOT_RUN, remaining tasks/blockers, exact next action and any
  local-only unpushed files. Commit/push this docs checkpoint and verify remote.
- Never push secrets, local merchant credentials, photos, databases, logs or
  unrelated dirty files. Do not force-push, create a branch, merge master, or
  publish knowingly unsafe/broken code simply to create a checkpoint.
  If source is incomplete, checkpoint **safe docs/tests or a disabled isolated
  increment** and explicitly label implementation WIP/NOT VERIFIED; preserve
  risky uncommitted code locally and clearly state that it is **not recoverable
  from GitHub**. Never claim a successful backup of unpushed work.
- In a **new Codex/chat session**, inspect `git status`, branch, remote HEAD
  and the latest commits, read the last remote checkpoint and related specs,
  reconcile any local-only modifications, then continue the **first unfinished
  micro-increment**. Do not redo previously verified, pushed work or reset data.
- This policy complements (not replaces) the documentation-first rule, small
  logical tests, one final functional regression, feature flags/safety gates,
  exact evidence requirements, and separate production/release authorization.

## Staged delivery and CI budget

- Make small logical changes, run relevant local checks, fix failures, commit,
  push to the authorized branch and verify remote HEAD before the next stage.
  Tell the owner which stage was pushed; do not accumulate a large silent change.
- Run one complete regression on the final functional change. Repeat broad
  checks only for new changes, failures or unresolved concerns. Do not send
  empty/documentation-only pushes merely to rerun successful GUI workflows.
- Documentation-only pushes skip the portrait workflow; manual dispatch remains
  available. Preserve code-change and PR validation. Superseded runs should be
  cancelled through the workflow concurrency policy.
- Report exact tested source, actual results and device/provider limits. Never
  claim visual parity solely because the physics engine matches.

Current authorized work stays on `feature/portrait-kiosk-v2-next`; no new branch,
master change or merge unless the owner later explicitly changes that scope.

Read `docs/DEVELOPMENT_HANDOVER.md` for current checkpoints and
`docs/DEVELOPMENT_PROTOCOL.md` for the broader project rules. Current explicit
owner instructions take precedence over older historical documentation.

## GUI v2 documentation and future primary branch

Owner direction, 2026-10-25: GUI v2 is the development focus and intended future
primary branch. Continue on existing `feature/portrait-kiosk-v2-next`; GitHub's
default remains `master` until an explicit repository operation. Read the current
root README and `docs/gui-v2-branch-audit.md` before borrowing branch features.
The audit pins all 19 branch tips; refresh the relevant remote before reuse.
Do not treat the branch direction as permission to rename, merge, change default,
switch `main.py`, enable production or automatically port candidate features.

Owner continuation, 2026-10-25: do safe approved source work and automatic checks
while laptop acceptance waits; do not stop solely for missing physical tests.
Refer to/reuse v1 whenever related, including actual UI and controller methods,
to avoid duplicate work. Latest completed bounded increment is read-only operator Device
Health + local safe reports (functional source ea394e8); hardware/provider gates
stay explicit. A later documentation request cross-checked obsolete/conflicting
guidance in English, completed at f36ebad. Preserve dated raw evidence and
distinguish current guidance from historical snapshots. That documentation task
did not authorize application changes, production, device switching, deployment
or default/merge operations; the following owner bug report has its own scope.

Owner retest continuation, 2026-10-25: the eight operator boxes were checked but
the notes report an application hang after pressing all Device Health buttons
rapidly. Preserve that initial contradiction and unknown tested HEAD. The scoped
v2 input correction reused the original v1 panel/backend/worker at ebb53fd.
A later targeted retest reports R01–R04 4/4 with no issue notes: BUG-018 is now
OWNER-REPORTED PASS / MONITORING. Do not patch the reported-working path or require
another old twenty-cycle run. Exact tested source/device metadata remains unknown;
recording the pass does not authorize proposed watchdog work or external gates.

Owner priority correction, 2026-10-25: develop **printing and Google Drive only**
before watchdog. The owner selected automatic print after approving photos (v1
behavior), with Drive in the background. Reuse existing v1 printer/config/Drive/
pool/QR services and v2 durable jobs/retention guard. Use explicit operator launch
opt-ins; preserve dedicated merchant-trial printer/Drive-off isolation. Cloud QA
uses fixtures; no real paper/upload, retention deployment/deletion, production,
branch/default change or watchdog is inferred. Physical acceptance can wait while
safe source work proceeds. See docs/qa/portrait-v2-print-drive/README.md.

Print/Drive delivery checkpoints: 7b691c7 options/contracts, 266b2c8 native
automatic print/background queue/verified QR. Final 800 full local PASS/zero
skips; matching-source CI three-job SUCCESS, 133 PNGs verified. Nine original
v1 service/config files remain unchanged. Record actual Windows paper/phone/
cloud results separately via the new eleven-item form; BUG-009 remains OPEN.
No additional feature (including watchdog) starts from this completed scope.

Owner continuation, 26 October: resume BUG-009 photo-retention remediation;
setup/redeployment is not confirmed. Reuse v1 setup/cleanup/configuration. Sources
130aae1/887ba39 repair CLOCK activation and add read-only redacted diagnosis;
807 full Python PASS/zero skips and 19 Code.gs VM PASS. Installed Google-account
activation/actual deletion is not verified; BUG-009 stays OPEN. No FEAT-004 ad
sync or watchdog is included. See docs/qa/bug-009-retention/README.md.

Owner orientation refinement, 26 October: GUI v2 review and photo areas of the
result, printed and digital strip must all mirror consistently. Keep raw camera
JPEGs/resolution and detector inputs original; artwork/text/logo/QR stay normal.
Reuse the existing compositor through a default-off option (v1 stays normal);
v2 opts in. New output only: never rewrite old strips or replay a print/upload.
See docs/qa/portrait-v2-mirrored-output/README.md and the five-item Submit form.

Storage integration continuation, 26 October: ordinary v2 launcher mounts layout 2
(data/Photobooth or explicit PHOTOBOOTH_V2_STORAGE_ROOT); physical PB001 maps to
transaction namespace PB001V2S2 to avoid legacy lease reuse. Reuse original
render/print/queue/ad services and preserve immutable cache generations, explicit
offline Drive intent, private claim state and no print replay. Code.gs requires
manual setupBoothStorage/setupPhotoRetention and redeployment at the existing
URL; source fixtures cannot close BUG-009. See implementation QA/SETUP/Submit
form. Legacy profile may finish its own existing queues, never migrate old.

