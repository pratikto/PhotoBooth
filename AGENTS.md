# Repository working instructions

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
