# Portrait GUI v2 — P2.6–P2.8 quality gate

> **Historical P2 scope and evidence — 21–23 October 2026.** The non-hardware
> P2 gates were closed at their recorded SHAs. “No game/camera/QRIS integration”
> and old twenty-cycle/device stop instructions below describe that original
> stage, not today's source or approval. P3/P4/P4b/P5 were subsequently approved
> and implemented; later owner reports are recorded at their metadata limits.
> Current acceptance uses the [P5 form](qa/portrait-v2-p5/windows-checklist.html)
> plus the separate [operator form](qa/portrait-v2-operator-health/windows-checklist.html).
> Do not repeat an old gate solely because it remains unchecked in this snapshot.
> [Current evidence](test_checklist.md) · [roadmap](portrait-kiosk-v2.md).

**Scope:** GUI v2 branch `feature/portrait-kiosk-v2-next` only. Meong Fly remains read-only; no integration, real scanner, QRIS, discounts, capture, or printing changes.

## Checkpoint and evidence policy

- Current owner update (2026-10-23): following diagnostic/correction instructions, the owner replies “sudah oke”. BUG-012 becomes OWNER-REPORTED PASS / MONITORING. Preserve the earlier five-cycle failure as history; post-update tested HEAD/cycles remain unknown and twenty-cycle F05/F06 acceptance stays unverified. [Confirmation and evidence](qa/portrait-v2-return-ad-crash/README.md).
- Diagnostic/correction source `bef4014` has matching-SHA CI 39869369246 SUCCESS (three jobs, 38 Windows native audio/diagnostic tests) and verified/reviewed original screenshot artifact. This remains separate from the subsequent owner-reported PASS; formal exact-source and twenty-cycle acceptance are still pending.
- Current owner-directed follow-up: [gallery focus / response / moving images / pixel typography](qa/portrait-v2-gallery-focus/README.md). Visual source `5a568bf` passes exact-SHA CI 39803887478, all three jobs; original artifact ZIP digest, clean manifests and images are verified and reviewed. Owner reports ten successful Windows cycles at an unknown earlier HEAD; twenty-cycle duration and owner acceptance of the new visual source are still open.
- Original P2 closure application/renderer checkpoint: `0fbf15829d1537a7f18990b492b1e5934f21c0f8`, [CI 39618540570](https://github.com/pratikto/PhotoBooth/actions/runs/39618540570), both jobs successful. Its artifact has been downloaded, digest verified and visually reviewed. Newer commits must not inherit this CI PASS; the current workflow also has a third Windows audio job.
- A pushed commit and verified remote HEAD mean **published**, not **tested**.
- Gate requires a GitHub Actions run with `head_sha` **exactly equal** to the milestone checkpoint SHA and both jobs successful. If no matching run is available, mark **BLOCKED / NOT VERIFIED**, never PASS.
- The desktop job must upload twelve screenshots (six pages × two viewports). Download and inspect those screenshots; existence alone does not prove legibility or alignment.
- Never claim hardware audio, camera, printer, QR/payment, or touch accuracy from Xvfb synthetic tests.

## P2.6 — Visual unification

- [x] Extract game palette and pixel geometry as pure design tokens.
- [x] Replace native v2 card/button backgrounds with stepped arcade styling.
- [x] Add design-token and clipped-corner regression tests; include them in CI.
- [x] Review all six rendered pages at **800×1280** and **452×900**, with no clipping, obscured CTA, unreadable text, or accidental rounded v1 elements.
- [x] Record a matching-SHA CI PASS and preserve artifact reference: P2.6 SHA `5fced9d`, run `39616959017`, artifact `12352643337`; downloaded ZIP digest verified and all twelve CI images reviewed.

## P2.7 — Responsive, interactive and audio lifecycle

- [x] Add fake-provider tests for page ownership, game-preview handoff, suspension, resume, cleanup, and idempotent teardown.
- [x] Verify navigation and touch targets across both viewport sizes with widget smoke and visual evidence.
- [x] Check transitions, timeout-to-idle behavior, one-tutorial-per-visit, and no restart of soundtrack during tutorial-to-template navigation.
- [x] Verify game preview does not overlap GUI music; actual Meong Fly is not integrated.
- [ ] Verify real Windows speaker playback and camera only during later operator acceptance, not in CI.

## P2.8 — Visual QA and rollback

- [x] Review screenshot artifact pixel-by-pixel for each page, each viewport.
- [x] Record screenshot artifact URL, exact SHA, test run ID, test summary and known limitations.
- [x] Close all P2.6–P2.8 blockers; mark non-hardware gates PASS only with evidence.
- [x] Record final stable commit as rollback reference; do not merge to `master`.
- [x] Present Windows acceptance checklist for user approval **after** P2.8 evidence is ready.

## Operator Windows acceptance (approval required later)

1. Run the GUI v2 on the actual 10.1-inch portrait touchscreen at its native resolution.
2. Confirm idle/invitation/tutorial/templates/cart/game-preview screen alignment and all CTA touch areas.
3. Confirm music on image advertisements and tutorial/templates, source audio only on video advertisements, no GUI music on game preview, and one click per enabled action on every page; suspend/resume and exit cleanly.
4. Confirm the camera and thermal printer are **not** represented as validated by this prototype; verify those only in separately authorized end-to-end integration.
5. Compare approved 12 vertical thermal designs and three-photo/QR layout against their existing source of truth; GUI prototype must not silently modify print output.

**Release rule:** no automatic promotion to master, no game integration, no assertion of production readiness from synthetic checks.

## Historical 2026-10-21 local checkpoint (superseded by the 2026-10-22 update)

P2.6 review found and corrected unreadable disabled payment/scanner labels.
40 local tests passed; twelve screenshots preserved in [local evidence](qa/portrait-v2-p26/README.md).
Matching-SHA CI/artifact gate remains pending. P2.7 and P2.8 are not closed.
Pre-change rollback: `e888d9945bc8c0a4c74bd1a8de57e946acb26204`.

P2.7 local follow-up: [45 tests, native dummy audio and twelve renders](qa/portrait-v2-p27/README.md).
Page callbacks now reject retired/suspended input; all CTA heights are at least
48dp, fourth tutorial step scroll access is tested at both sizes, and effects
stop during suspend or handoff to advert/game preview. Exact-SHA CI and remote
artifact inspection are still required; do not mark P2.8 complete.

## Historical 2026-10-21 stop point — external evidence gate

[Checkpoint report, exact SHAs, CI/artifact references, blocker and Windows checklist](qa/portrait-v2-p28/README.md).
P2.6 exact-SHA CI passed both jobs; artifact download is still blocked by proxy
CONNECT 403. P2.7 exact-SHA run was queued at last observation. Local P2.8
renderer checks, 45 tests and twelve pixel-identical rerenders passed, but
**P2.6–P2.8 completion is not certified** until required CI/artifact review.

## Historical first 2026-10-22 post-publish verification (superseded below)

[Exact-SHA CI metadata, downloaded P2.6 images and review](qa/portrait-v2-ci/README.md).
P2.6 non-hardware gate is PASS. P2.7 and P2.8 both pass exact-SHA CI, but
their artifact visual review is still BLOCKED by two additional GitHub storage
hosts (13 and 9). Those exact domains were saved in a new environment draft.
Post-publish local validation: 45 tests PASS, clean `0fbf158` manifests and twelve
new screenshots. No new application code changes. P2.8 remains incomplete.

## Final 2026-10-22 closure — non-hardware PASS

[Final CI evidence](qa/portrait-v2-ci/README.md) and [report/Windows checklist](qa/portrait-v2-p28/README.md).
All three milestone checkpoints have exact-SHA successful CI, both jobs successful,
and downloaded original screenshot artifacts reviewed at both target dimensions.
P2.7/P2.8 ZIP digests match GitHub; P2.8 manifests match clean source and PNG hashes.
45 local tests PASS, zero skips. Stable code/renderer rollback:
`0fbf15829d1537a7f18990b492b1e5934f21c0f8`.
Windows speaker/touch acceptance is deliberately still unchecked above.
No master merge, game integration, production payment or hardware certification.
