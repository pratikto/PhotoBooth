# P2.8 evidence checkpoint — BLOCKED, not complete

Date: 2026-10-21. Branch: `feature/portrait-kiosk-v2-next` only.

## Published checkpoints

| Stage | Exact SHA | Outcome |
| --- | --- | --- |
| Before this task | e888d9945bc8c0a4c74bd1a8de57e946acb26204 | Original rollback reference |
| P2.6 readability | 5fced9d5985d72bb89e046b2b0fe93f7cd247709 | Normal push and remote HEAD verified; 40 local tests passed |
| P2.7 lifecycle | 5bb479890ad50b28287d8728bd6e4d12313eaa7e | Normal push and remote HEAD verified; 45 local tests passed |

P2.6 exact-SHA [CI run 39616959017](https://github.com/pratikto/PhotoBooth/actions/runs/39616959017):
API reports completed/success; both Navigation/audio and Synthetic Kivy jobs
independently report completed/success. Screenshot artifact:
`meong-portrait-v2-screens`, ID `12352643337`, digest
`4fa579e54b8b10abc3cea59b7ef43d141dd6b9bbb5de05af37ac680219167822`.
**Artifact download failed at the running network proxy, so its screenshots
have not been inspected. A successful CI does not close this visual gate.**

P2.7 exact-SHA [CI run 39617634875](https://github.com/pratikto/PhotoBooth/actions/runs/39617634875)
was explicitly dispatched at the verified branch HEAD. Last observed run and
both jobs: QUEUED. Do not inherit P2.6 success for P2.7 or a later docs commit.

## Local review and renderer hardening

45 tests passed again, no skips. Both render commands produced six screenshots.
The renderer now checks the expected current route, exact image dimensions,
row integrity, and writes a SHA-256/state/source-SHA JSON manifest per viewport.
Actions/captures are scheduled after the previous action completes, so slow
font/texture startup cannot collapse absolute deadlines into misleading images.

All twelve new screenshot pixel arrays equal the reviewed P2.7 PNGs exactly;
see [the raw P2.7 images](../portrait-v2-p27/README.md). Every page was inspected
at both sizes, including complete CTA labels, enabled/disabled differences,
1:3 real strips, invitation placement and tutorial scroll clipping. The fourth
tutorial step is accessible by scroll (real-widget input/geometry test).
Immediate transitions and static starfield intentionally avoid animation loops.

The local manifests here record P2.7 HEAD with `tracked_changes: true`, because
the renderer hardening was uncommitted during capture. They are transparent
local evidence, **not a claim that CI ran the final P2.8 commit**. CI-generated
manifests from a later clean checkout must record that exact checkpoint SHA.

## External blocker and required next action

`api.github.com` initially returned proxy CONNECT 403 and later became usable.
The artifact redirect host `productionresultssa2.blob.core.windows.net` still
returns proxy CONNECT 403. Existing GH_TOKEN is present and GitHub Git/API
operations now work; no duplicate credential is needed. Both exact domains
were saved additively in the environment draft, preserving package presets.
Review/save the environment settings and publish the prepared environment, then
retry the artifact download and any pending CI checks. Do not disable TLS or
use a third-party credential route.

Required continuation after access is available:

1. Check exact-SHA runs and both job conclusions for each milestone checkpoint.
2. Download the `meong-portrait-v2-screens` artifact for each required checkpoint.
3. Verify twelve original screenshots, dimensions, hashes and clean source SHA
   (where the new renderer supplies manifests), then inspect all of them.
4. Record final CI IDs, artifact URLs, results and the final stable rollback SHA.
5. Only then close non-hardware P2.6–P2.8 gates and present Windows acceptance.

No local test failures remain. Windows speaker/touch acceptance is unrun;
legacy BUG-001/007 speaker issues and BUG-009 Drive retention stay open.
No mini-game, scanner, discount, live payment, capture or production transaction
integration was enabled. Master was not changed or merged.

## Windows Acceptance Test — NOT RUN, operator checklist

- [ ] Record commit SHA, Windows version, Python/Kivy versions, screen model,
      native portrait resolution, scaling/DPI, speaker/provider and test time.
- [ ] Install requirements and run the portrait flow/audio/design/widget suites;
      record executed test counts and any failure or skip.
- [ ] Run `python tools/run_portrait_v2.py` at native 800×1280 and simulate
      452×900; inspect idle, invitation, tutorial, gallery, copy cart and preview.
- [ ] Tap all enabled CTAs at center and edges; confirm readable disabled scanner
      and payment controls cannot navigate. Check gallery swipes and copy limits.
- [ ] Scroll tutorial to step four; acknowledge once per visit, browse templates,
      return/expire to ads and confirm the next visit requires acknowledgement.
- [ ] Hear automatic tutorial/template music without pressing Test Music; confirm
      continuity across the transition and no GUI music/effects over idle media
      or game preview. Check actual ad video source audio independently.
- [ ] Suspend/resume while browsing and while an effect plays; no duplicate or
      stale sound, immediate timeout or retained touch should affect the visit.
      Close/relaunch and check no orphan playback. Exercise rapid repeated taps.
- [ ] Confirm no real game, receipt claim, discount, payment or transaction starts.
      Camera/thermal/Drive end-to-end checks require their separate integration
      scope and must not be represented as validated by this prototype.
- [ ] Record screenshots and audible/touch observations with exact SHA. Obtain
      owner acceptance before any release or promotion to master.
