# Meong Photobooth — current feature status

Updated **25 October 2026** against audit baseline `5f09eff` on
`feature/portrait-kiosk-v2-next`. Latest functional source: **`ea394e8`**.
The earlier **`9433010` / `0dc6555`** pair is the P5 source/evidence baseline,
not the latest operator checkpoint. GitHub's default remains `master`.

IN SOURCE means implemented; VERIFIED AUTOMATED means a recorded source-specific
check passed; OWNER-REPORTED means a physical observation with the recorded
metadata limits; PENDING/NOT_RUN means acceptance has not been demonstrated.
None of these alone means production-certified or formally released.

| Feature | Current GUI v2 source | Evidence and boundary |
| --- | --- | --- |
| Advertising/tutorial/twelve templates | Responsive media, inline invitation, tutorial once per visit, swipe gallery, native captions and animated header | Source screenshots; final owner visual/audio 8/8 at unknown HEAD |
| Camera/face/optional palm | Async camera and preview, display-only mirror, existing face/palm services; manual SIAP retained | Owner-reported preview/button/palm PASS and prior twenty cycles; missing source/device fields stay unknown |
| Capture/review/retake | Three original photos per selected design, one retake per design, local composition | Quantity 0 deselects; 1–9 means identical copies, not more sessions. New integration acceptance remains separate |
| Audio | Single v2 owner; GUI loop for still ads/photo journey, video's own audio, distinct game loop; one cue per action | Owner-reported normal. BUG-017 is monitoring after the later report, not a proven decoder fix; v1 BUG-001/007 stay separate |
| Thermal photo printing | Existing backend, operator opt-in, multi-copy batch and uncertain-send guards | Source/fixtures pass; prior owner paper reports retained at unknown HEAD. Dedicated Sandbox launcher forces printer off |
| Drive/download | Opt-in adapter, assigned folder QR and retention-acknowledgement upload guard | Default local; dedicated Sandbox launcher forces Drive off. BUG-009 cloud deletion remains OPEN |
| Meong Fly — FEAT-021 (game) | Original Stage/Flow/renderer/assets/emitter reused; persistent one-use v2 DEMO ledger | 26 reference files pinned to `672e3f7`. V2 uses manual DEMO entry; standalone camera scanner is not mounted |
| Local MOCK checkout | Local SQLite quote/promotion/admission; nonpayable QR and simulated confirmation | Win discount Rp2,500 once per order, capped at subtotal; no bank settlement |
| FEAT-020 QRIS Sandbox | Reused service/client/journal plus native v2 adapter/isolated launcher | Server quote, provider verification, one-use grant/ACK/recovery in source. Actual merchant simulator evidence pending; no trusted game-promo API |
| P5 readiness | Read-only CLI, safe metadata JSON, 26-item Submit/import form, rollback package | Owner preflight `0dc6555` = READY_FOR_MANUAL_TEST, not hardware/provider PASS |
| FEAT-008 operator Device Health | Original v1 backend/panel/worker reused with small v2 adapters and safe report export | F12/header hold at idle or Sandbox RECOVERY; manual refresh only; eight-item acceptance pending. Selection/switching disabled |
| Other reference features | Device staging/switching, AI Background Studio, WhatsApp, newer dithering lab | Separate branches; not automatically in v2. [Reference map](gui-v2-branch-audit.md) |
| Production payments, merchant POS/scanner, trusted QRIS promo | Disabled/not delivered in v2 | Require their own approved scope, trust contract and acceptance |

## Latest recorded automated evidence

| Checkpoint | Local full regression | Matching-source CI | Screenshot evidence |
| --- | --- | --- | --- |
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
