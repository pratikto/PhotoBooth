# Remote QA evidence — 2026-10-22

> **Dated source/QA record, retained for traceability.** Results, “latest/current”,
> OPEN/PENDING labels, next actions and authorization limits below apply to this
> package's recorded source and report date. Later owner reports and source work
> can supersede its status; they do not rewrite these test results. Use
> [current status](../../FEATURE_STATUS.md), [test ledger](../../test_checklist.md)
> and [current handover](../../DEVELOPMENT_HANDOVER.md) for continuation. Historical
> checklists are not an instruction to repeat already accepted tests.

Only `feature/portrait-kiosk-v2-next`. All three milestone SHA/run pairs and
both jobs were verified directly through GitHub's API after environment publish.
The sanitized run, job/step, and artifact metadata are preserved alongside this file.

| Stage | Exact SHA | Run | Both jobs | Artifact review |
| --- | --- | --- | --- | --- |
| P2.6 | 5fced9d5985d72bb89e046b2b0fe93f7cd247709 | [39616959017](https://github.com/pratikto/PhotoBooth/actions/runs/39616959017) | SUCCESS | Twelve PNGs downloaded and reviewed |
| P2.7 | 5bb479890ad50b28287d8728bd6e4d12313eaa7e | [39617634875](https://github.com/pratikto/PhotoBooth/actions/runs/39617634875) | SUCCESS | Twelve PNGs downloaded, digest verified and reviewed |
| P2.8 | 0fbf15829d1537a7f18990b492b1e5934f21c0f8 | [39618540570](https://github.com/pratikto/PhotoBooth/actions/runs/39618540570) | SUCCESS | Twelve PNGs downloaded, digest verified and reviewed |

## P2.6 visual review — PASS (synthetic only)

[Artifact 12352643337](https://github.com/pratikto/PhotoBooth/actions/runs/39616959017/artifacts/12352643337),
`meong-portrait-v2-screens`. The downloaded ZIP SHA-256 equals the API digest:
`4fa579e54b8b10abc3cea59b7ef43d141dd6b9bbb5de05af37ac680219167822`.
All twelve original CI PNGs are preserved in [39616959017](39616959017/), with
individual hashes and exact image dimensions in [sha256.json](39616959017/sha256.json).

Each original image was opened and reviewed at 452×900 and 800×1280:

| Page | Observation at both sizes |
| --- | --- |
| Advertising | Both main CTAs and helper actions visible; local ad contained without clipping |
| Invitation | Inline overlay, readable labels, all three actions visible; advertising remains underneath |
| Tutorial | Text/illustrations and fixed CTAs readable; compact guide intentionally scrolls to later steps |
| Templates | Three true 1:3 strip previews, selected design and navigation visible |
| Copy cart | Count and DEMO quote visible; payment remains disabled and readable |
| Game placeholder | Rules and unavailable scanner readable; photo and return actions visible |

Stepped cards/buttons follow the shared palette; no accidental rounded v1 page
shell, obscured main CTA, unreadable disabled label or screenshot row corruption
was found. Physical touchscreen accuracy and audible sound are not certified.
CI rasterization differs from the local images, so local screenshots were not
substituted for the downloaded originals.

## P2.7/P2.8 visual review — PASS (2026-10-22)

P2.7 artifact: [12352334786](https://github.com/pratikto/PhotoBooth/actions/runs/39617634875/artifacts/12352334786),
API digest `971676ab109e9be504b7a21fc3df3023fb79f3b5f8574f5c11f7e69ac6b36244`.
P2.8 artifact: [12353357896](https://github.com/pratikto/PhotoBooth/actions/runs/39618540570/artifacts/12353357896),
API digest `a27ac09dd5e16e36431463d332b993ba0dbcce6de162156234faf1c466267a13`.
Both original ZIPs have now been downloaded, and their SHA-256 values match the
GitHub API digests above. Each contains exactly twelve original PNGs at the
approved dimensions. Original files, individual hashes, ZIP verification and
P2.8's original CI manifests are preserved in [P2.7](39617634875/) and
[P2.8](39618540570/).

The P2.8 manifests report clean source SHA
`0fbf15829d1537a7f18990b492b1e5934f21c0f8`, `tracked_changes: false`, six
expected states per viewport, and screenshot hashes that match every PNG.
Every page was reviewed at each viewport. P2.7 and P2.8 have identical pixels
in eleven images. Their compact tutorial differs only in the four-pixel-wide
scroll indicator (484 pixels at x=428..431, y=314..434); both tutorial images
were opened separately and reviewed. This is the ScrollView indicator fade,
not content/layout drift. The six-page observations in the P2.6 review above
also hold for the final P2.7/P2.8 images. Invitation and music-test CTA heights
are now at least 48dp, with reachability/bounds covered by real-widget tests.

The previously blocked hosts 13 and 9 work after the second environment publish.
No network or credential prerequisite remains for these milestone artifacts.
No further environment publication is needed to close this QA gate.

## Post-publish current-instance validation

45 local tests PASS, zero skips. Twelve new screenshots and both manifests were
verified against clean source SHA `0fbf15829d1537a7f18990b492b1e5934f21c0f8`:
`tracked_changes: false`, six states per viewport, exact dimensions and matching
PNG hashes. The manifests and local test transcript are retained here.
This confirms the published environment can run the workflow. Remote-artifact
review is now complete; Windows acceptance remains unrun.

## Closed checkpoint and remaining acceptance

P2.6–P2.8 **non-hardware gates PASS**. Stable application/renderer rollback:
`0fbf15829d1537a7f18990b492b1e5934f21c0f8`, exact-SHA CI
[39618540570](https://github.com/pratikto/PhotoBooth/actions/runs/39618540570),
both jobs successful, original artifact reviewed and verified. Original pre-task
rollback: `e888d9945bc8c0a4c74bd1a8de57e946acb26204`.
Documentation checkpoint `384b4743428425390cd03bf87b77ba563fdfe6a9` also has
its own successful [run 39684269848](https://github.com/pratikto/PhotoBooth/actions/runs/39684269848)
with both jobs successful; its sanitized metadata is retained here. A subsequent
documentation-only closure commit does not imply another CI run unless observed.

Final local regression: 45 tests PASS, zero skips (closure-tests.txt).
No new layout/navigation/audio-provider regression remains in the tested scope.
Actual Windows speaker audibility/touch and legacy BUG-001/007 and BUG-009 remain
open; nothing here certifies those hardware/cloud issues. No game, scanner,
discount, live payment, capture or production transaction integration occurred.
Master remains unchanged and no merge/release was performed.

[Final report and Windows checklist](../portrait-v2-p28/README.md).
