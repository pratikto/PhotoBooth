# Remote QA evidence — 2026-10-22

Only `feature/portrait-kiosk-v2-next`. All three milestone SHA/run pairs and
both jobs were verified directly through GitHub's API after environment publish.
The sanitized run, job/step, and artifact metadata are preserved alongside this file.

| Stage | Exact SHA | Run | Both jobs | Artifact review |
| --- | --- | --- | --- | --- |
| P2.6 | 5fced9d5985d72bb89e046b2b0fe93f7cd247709 | [39616959017](https://github.com/pratikto/PhotoBooth/actions/runs/39616959017) | SUCCESS | Twelve PNGs downloaded and reviewed |
| P2.7 | 5bb479890ad50b28287d8728bd6e4d12313eaa7e | [39617634875](https://github.com/pratikto/PhotoBooth/actions/runs/39617634875) | SUCCESS | BLOCKED by artifact host 13 |
| P2.8 | 0fbf15829d1537a7f18990b492b1e5934f21c0f8 | [39618540570](https://github.com/pratikto/PhotoBooth/actions/runs/39618540570) | SUCCESS | BLOCKED by artifact host 9 |

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

## P2.7/P2.8 visual review — BLOCKED

P2.7 artifact: [12352334786](https://github.com/pratikto/PhotoBooth/actions/runs/39617634875/artifacts/12352334786),
API digest `971676ab109e9be504b7a21fc3df3023fb79f3b5f8574f5c11f7e69ac6b36244`.
P2.8 artifact: [12353357896](https://github.com/pratikto/PhotoBooth/actions/runs/39618540570/artifacts/12353357896),
API digest `a27ac09dd5e16e36431463d332b993ba0dbcce6de162156234faf1c466267a13`.
These are metadata digests only; no downloaded-ZIP verification is claimed.

GitHub redirects their downloads to `productionresultssa13.blob.core.windows.net`
and `productionresultssa9.blob.core.windows.net`. Both downloads returned proxy
CONNECT 403. Exact hostnames were added to the draft, preserving the existing API,
host 2 and package-manager rules. Save/publish the updated network configuration,
then retry these two downloads. No additional secret is required.

## Post-publish current-instance validation

45 local tests PASS, zero skips. Twelve new screenshots and both manifests were
verified against clean source SHA `0fbf15829d1537a7f18990b492b1e5934f21c0f8`:
`tracked_changes: false`, six states per viewport, exact dimensions and matching
PNG hashes. The manifests and local test transcript are retained here.
This confirms the published environment can run the workflow; it does not replace
the outstanding remote-artifact visual review or Windows acceptance.

The stable application/renderer checkpoint is `0fbf158`; its CI succeeded.
Until its artifact is reviewed, this remains a tested checkpoint with an open
visual gate. Original pre-change rollback remains `e888d9945bc8c0a4c74bd1a8de57e946acb26204`.
The current documentation-only commit must not inherit a new CI PASS without
an exact-SHA run. Windows checklist: [P2.8 report](../portrait-v2-p28/README.md#windows-acceptance-test--not-run-operator-checklist).
