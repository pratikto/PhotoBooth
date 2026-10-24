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
  motion. Do not scale far and near positions differently (BUG-015).
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
