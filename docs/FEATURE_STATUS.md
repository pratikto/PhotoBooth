# Meong Photobooth — current feature status

Updated **26 October 2026** after documentation baseline `f36ebad` on
`feature/portrait-kiosk-v2-next`. Latest functional source **53e7b4c** is the coordinated [storage integration](qa/feat-004-storage/README.md), after mirrored v2 **fc26e3d**, following BUG-009 diagnosis `887ba39`, tutorial entry `20453fe` and print/Drive `266b2c8`.
The earlier **`9433010` / `0dc6555`** pair is the P5 source/evidence baseline,
not the latest operator checkpoint. GitHub's default remains `master`.

IN SOURCE means implemented; VERIFIED AUTOMATED means a recorded source-specific
check passed; OWNER-REPORTED means a physical observation with the recorded
metadata limits; PENDING/NOT_RUN means acceptance has not been demonstrated.
None of these alone means production-certified or formally released.

**Owner flow refinement, 26 October:** idle no longer has a separate CARA PAKAI
button. Direct/invitation photo entry still requires the four-step tutorial for
a fresh visit, using the existing navigation/actions. [Current change and
validation](qa/portrait-v2-photo-entry/README.md).

**Latest owner retest, 25 October:** targeted R01–R04 **4/4 checked**, zero
unchecked and no issue notes. BUG-018 moves to **OWNER-REPORTED PASS / MONITORING**:
rapid/mixed clicks, close while busy, reopen/minimize and next input/restart are
reported working. Preserve the earlier contradictory raw 8/8/hang report.
Tested HEAD/device fields remain unknown; no exact-source verification, formal
closure or external P5 acceptance is inferred. No new runtime patch is needed.
[Reports and correction](qa/portrait-v2-health-clicks/README.md).

| Feature | Current GUI v2 source | Evidence and boundary |
| --- | --- | --- |
| Advertising/tutorial/twelve templates | Responsive media, inline invitation, tutorial once per visit via photo entry (no separate help button), swipe gallery, native captions and animated header | Source screenshots; final owner visual/audio 8/8 at unknown HEAD; later entry refinement has its own source checks |
| Camera/face/optional palm | Async camera and preview, display-only mirror, existing face/palm services; manual SIAP retained | Owner-reported preview/button/palm PASS and prior twenty cycles; missing source/device fields stay unknown |
| Capture/review/retake | Three original photos/design, one retake/design; v2 review and photo areas in the shared result/print/digital PNG mirror | Raw JPEGs retain original orientation/resolution; template/text/QR and v1 defaults stay normal. Old outputs unchanged; quantity means copies, not more sessions. [Mirror proof/form](qa/portrait-v2-mirrored-output/README.md) |
| Audio | Single v2 owner; GUI loop for still ads/photo journey, video's own audio, distinct game loop; one cue per action | Owner-reported normal. BUG-017 is monitoring after the later report, not a proven decoder fix; v1 BUG-001/007 stay separate |
| Thermal photo printing | Existing v1 backend/config; --print auto-sends one durable batch per approved design, --manual-print optional; uncertainty/no-replay guards | New-source fixtures pass; actual current paper/copy/QR acceptance pending. Prior owner paper reports stay at unknown HEAD. Merchant trial forces printer off |
| Drive/download | --drive resumes existing isolated queue on startup/after visits; offline-safe admission, background binding/retry and large verified on-screen QR, original retention guard | New-source fixtures/pixel decode available; actual phone access/offline/restart and cloud deletion unverified. Default local; merchant trial off. BUG-009 OPEN |
| BUG-009 retention activation | Reused v1 setup/cleanup; real CLOCK required for active registration ACK, incorrect trigger setup repaired; read-only redacted CLI/status and eight-item Submit form | 807 full Python PASS/zero skips; 19 actual-Code.gs VM PASS. Owner setup/deployment unconfirmed. Google timer/deletion NOT_RUN; bug stays OPEN. [Guide/evidence](qa/bug-009-retention/README.md) |
| Meong Fly — FEAT-021 (game) | Original Stage/Flow/renderer/assets/emitter reused; persistent one-use v2 DEMO ledger | 26 reference files pinned to `672e3f7`. V2 uses manual DEMO entry; standalone camera scanner is not mounted |
| Local MOCK checkout | Local SQLite quote/promotion/admission; nonpayable QR and simulated confirmation | Win discount Rp2,500 once per order, capped at subtotal; no bank settlement |
| FEAT-020 QRIS Sandbox | Reused service/client/journal plus native v2 adapter/isolated launcher | Server quote, provider verification, one-use grant/ACK/recovery in source. Actual merchant simulator evidence pending; no trusted game-promo API |
| P5 readiness | Read-only CLI, safe metadata JSON, 26-item Submit/import form, rollback package | Owner preflight `0dc6555` = READY_FOR_MANUAL_TEST, not hardware/provider PASS |
| FEAT-008 operator Device Health | Original v1 backend/panel/worker reused with small v2 adapters and safe report export | Later R01–R04 owner retest 4/4, no issues: BUG-018 monitoring at unknown HEAD/device metadata. Selection/switching disabled |
| Other reference features | Device staging/switching, AI Background Studio, WhatsApp, newer dithering lab | Separate branches; not automatically in v2. [Reference map](gui-v2-branch-audit.md) |
| FEAT-004 ads + BUG-009 booth storage/content | Ordinary v2 launcher uses PB00X roots, 25 empty reserves, Photo/NN/raw,color,bw, saved 1-bit print and verified global/local caches; Code.gs supplies scoped reservations/binding/content/cleanup | 824 full local PASS/zero skips, 24 Code.gs PASS, matching three-job CI SUCCESS; [stage package](qa/feat-004-storage/README.md). Actual Google setup/deploy, phone/paper and deletion NOT_RUN. BUG-009 stays OPEN until real expiry evidence |
| Production payments, merchant POS/scanner, trusted QRIS promo | Disabled/not delivered in v2 | Require their own approved scope, trust contract and acceptance |

## Latest recorded automated evidence

| Checkpoint | Local full regression | Matching-source CI | Screenshot evidence |
| --- | --- | --- | --- |
| Mirror source `fc26e3d` | **808 PASS / zero failures/errors/skips**, 230.670s; earlier focused 42 PASS, renderer/template 19 PASS | [40263151709](https://github.com/pratikto/PhotoBooth/actions/runs/40263151709), all three jobs SUCCESS; native 103 PASS/one optional model-assets skip covered locally | Sixteen clean-source native captures verified, eight selected views and two form views reviewed at required sizes. Actual paper orientation NOT_RUN. [Proof](qa/portrait-v2-mirrored-output/README.md) |
| Storage/content source `53e7b4c` | **824 PASS / zero failures/errors/skips**, 241.156s; 24 Code.gs VM PASS; cold ordinary launcher offline PASS | [40273343183](https://github.com/pratikto/PhotoBooth/actions/runs/40273343183), all three jobs SUCCESS; optional CI model skip covered by the full local run | 133 CI PNGs / source reports checked; 28 final native captures + two form views published. [Proof/setup/checklist](qa/feat-004-storage/README.md). No cloud/paper/phone acceptance inferred |
| BUG-009 source `887ba39` | **807 PASS / zero failures/errors/skips**, 238.684s; 44 focused Python and 19 Node VM PASS | [40255716011](https://github.com/pratikto/PhotoBooth/actions/runs/40255716011), all three jobs SUCCESS; native 103 PASS/one optional model-assets skip covered locally | No main GUI layout change; four native CI and two form views reviewed at 800×1280/452×900, 360px form overflow check; [proof](qa/bug-009-retention/README.md). Fixtures are not Google acceptance |
| Photo-entry source `20453fe` | **800 PASS / zero failures/errors/skips**, 217.888s | [40248962384](https://github.com/pratikto/PhotoBooth/actions/runs/40248962384), all three jobs SUCCESS; native 103 PASS/one optional palm-assets skip covered locally | Twelve clean-source PNGs hash/dimension verified; six affected idle/invitation/tutorial views reviewed at both required sizes; [proof](qa/portrait-v2-photo-entry/README.md) |
| Print/Drive source `266b2c8` | **800 PASS / 0 failures / 0 errors / 0 skips**, 213.823s | [40208966127](https://github.com/pratikto/PhotoBooth/actions/runs/40208966127), all three jobs SUCCESS; delivery 17 PASS, health 80 PASS, Sandbox 139 PASS, native 103 PASS/1 optional model-assets skip | 133 PNGs verified; delivery views reviewed at both sizes, large QR screenshot pixels decoded; [proof/form](qa/portrait-v2-print-drive/README.md) |
| BUG-018 source `ebb53fd` | **785 PASS / 0 failures / 0 errors / 0 skips**, 321.181s | [40189694738](https://github.com/pratikto/PhotoBooth/actions/runs/40189694738), three jobs SUCCESS; health 80 PASS, Sandbox 139 PASS, native 97 PASS/1 optional model-assets skip | 119 PNGs source/hash/dimension verified; operator views reviewed at 800×1280/452×900; [proof](qa/portrait-v2-health-clicks/README.md) |
| Operator source `ea394e8` | **780 PASS / 0 failures / 0 errors / 0 skips**, 270.671s | [40157638369](https://github.com/pratikto/PhotoBooth/actions/runs/40157638369), three jobs SUCCESS; health 80 PASS, Sandbox 139 PASS, native 92 PASS/1 optional palm-model-assets skip | 119 PNGs source/hash/dimension verified; required views reviewed; 15 local operator PNGs reviewed |
| Earlier P5 source `9433010` | **688 PASS / 0 failures / 0 errors / 0 skips**, 211.646s | [40109206417](https://github.com/pratikto/PhotoBooth/actions/runs/40109206417), three jobs SUCCESS; native includes one optional palm-model-assets skip | 109 PNGs source/hash/dimension verified; required views reviewed |

The optional CI model case is covered by each recorded local full run with
supplied assets. Three successful CI jobs do not mean zero skipped cases.
These are Linux/software-GL/dummy-audio/offline-fixture results, with the Windows
CI audio job also using dummy output. They are not physical acceptance.
[Operator proof](qa/portrait-v2-operator-health/README.md) · [P5 proof](qa/portrait-v2-p5/README.md).

## Outstanding acceptance

P5 is ready for acceptance, with current Windows integration, actual merchant
Sandbox, physical paper/uncertain-job handling, Drive/download/offline/cloud
retention, privacy and release signoff still awaiting complete evidence. Keep
prior owner reports at their known or unknown tested HEAD; never attribute them
to a newer commit. Safe approved source work continues independently of laptop
availability. [Test ledger](test_checklist.md) · [bug register](bug_tracker.md).

## Historical record

The [pre-audit version](https://github.com/pratikto/PhotoBooth/blob/5f09eff9998c942ed54feef0cf0563fc3944611b/docs/FEATURE_STATUS.md) preserves the complete dated history. Its former “current”, approval, branch and next-step statements apply only to their recorded stage. Use the current documents linked above for continuation.
