# PP-07 execution campaign R2 — 5 November 2026

Authorized branch: `feature/post-preview-qris-checkout`. Starting remote source independently verified as `38254738cf0724655aea61dfd3bb1beb5812b5cb`. The unrelated attached checkout remains clean on `work` at `0fbf15829d1537a7f18990b492b1e5934f21c0f8`; execution uses an independent exact-source snapshot excluding `old`.

## R2-A — close the unfinished complete-regression gate

**1,760 PASS, zero failures/errors/skips**, unittest duration **476.895s**, process duration **478.519s**, exit 0. Run began **5 November 2026 06:19:38 Asia/Jakarta** and ended **06:27:37**. Source: `3825473`; Python 3.12.14, existing task venv, Linux, SDL offscreen/software GL, dummy audio. GUI/audio/video/model opt-ins were all active, real camera/face/palm acquisition and live printer/Drive were disabled. No concurrent replay or resource probe ran.

The original delivery-helper failing method now PASS in the full run. All three real MediaPipe inference methods also PASS: this environment retained the five pinned public model/sample assets from the earlier campaign, and their byte sizes and SHA-256 values were independently verified against the versioned manifest before execution. No new download, proxy workaround, fake inference or platform-security bypass was used. R1's CONNECT-403 observation remains true for its recorded environment; it is not an ongoing asset blocker for this run.

[Machine-readable evidence](evidence/pp07-execution-r2-2026-11-05.json) contains exact command/source, UTC timestamps, asset hashes and report/log digests. Raw logs and assets remain local-only. Reproduction: use `tools/run_kiosk_unittests.py` without a module list, `PHOTOBOOTH_TEST_GUI=1`, `PHOTOBOOTH_TEST_AUDIO=1`, `PHOTOBOOTH_TEST_VIDEO=1`, `PHOTOBOOTH_PALM_TEST_ASSETS` pointing to independently verified public assets, offscreen/software rendering/dummy audio and documented virtual-device guards. Inspect actual dependency/runner requirements before a different platform run.

Matching [CI 41930961409](https://github.com/pratikto/PhotoBooth/actions/runs/41930961409) at source `3825473` is completed 3/3 SUCCESS. All three logs independently inspected: Windows **557 PASS / 446.437s**, Ubuntu **557 PASS / 179.632s**, native Kivy **67 PASS / 82.835s**, each zero failures/errors/skips. These 1,181 CI executions and 1,760 local executions are overlapping software scopes, not unique acceptance-case counts. Documentation-only publication does not require rerunning the successful workflow.

The earlier fec4f7f full FAIL (1,756 PASS / one FAIL / three SKIP) and all R1 ERROR/cancelled runs remain preserved. This exact-source retest closes their outstanding software-verification gate without claiming proof of the original occurrence's precise cause or physical acceptance.

## Next implementation boundary and unchanged gates

Proceed with a narrowly gated supported protected original-worker restoration increment. Reuse the original services, customer proof, fresh provider verification, exact isolation ACK/generation and frozen media; write meaningful independent-process regression first. Current service/claim constructors are synthetic-only, the pilot key is ephemeral and occupied roots stay refused. A scoped Windows protected mock integration must remain distinct from actual merchant support, full crash/reboot/device recovery and unsupported Ubuntu OS protection. Do not remove existing launcher restrictions or persist a plaintext fixture key.

Full 112 PP acceptance remains NOT_RUN; owner PILOT remains 24 NOT_RUN / 2 BLOCKED; no UAH/AR full acceptance promotion. Protected original-worker restoration, actual post-preview merchant profile, physical camera/touch/audio/POS80, real Drive ACL/retention, long-duration qualification and refund/account/legal gates remain outstanding. PP-101/104–110/112 required scopes remain incomplete. Actual refund and production stay disabled/unapproved.

Reviewed sources: user execution brief, current repository instructions/development protocol, R1 continuation/campaign/register/evidence, complete master/case/inherited plans, canonical acceptance matrix, complete decision ledger, security/state and refund/escalation contracts, architecture, current constructor/claim/isolation/worker paths and relevant existing tests. Historical source/status remains versioned.
