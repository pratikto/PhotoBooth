# Meong Photobooth — Development handover

> Owner reports resize-related fast/variable waves; BUG-015 is reproduced and fixed in adapter, 25 focused native checks PASS. Next: separately center gallery controls/header and add requested flying logo/title overlay. [Scope/evidence](qa/portrait-v2-motion-correction/README.md).

> Current resize follow-up (2026-10-24): compact gallery pushed as 60ab3cf (CI SUCCESS). Responsive original-art stage now passes 529 full local tests, zero skips; 80 PNGs hash-checked with four-size visual review. Original 26 reference files unchanged. Source 5c81ea1 has matching-source CI 40056129151: all three jobs SUCCESS. Next is Windows retest with the new Submit form. [Evidence, source hashes and rollback](qa/portrait-v2-responsive-scene/README.md).

> Current owner resize follow-up: compact gallery stage passes 20 native checks; next adapt actual original game components to window bounds, replacing separate filler. [QA/rollback](qa/portrait-v2-responsive-scene/README.md).

> **Current owner follow-up (2026-10-24):** Staged `4896d51` fixes game background/window/footer/mouse; `16bc7c6` fixes winning quote display/consumption. Dedicated game BGM at `f3172a5` now reuses the existing owner and synth instruments; [matching-source CI 40051193648](https://github.com/pratikto/PhotoBooth/actions/runs/40051193648) has all three jobs SUCCESS, final 527 full PASS, 39 focused audio PASS and 50 screenshots verified. Restart the existing launcher after pull so pointer config/new WAV load. All original reference modules remain unchanged. [Current proof, rollback and retest](qa/portrait-v2-game-followup/README.md).

> **Current functional correction (2026-10-24):** Latest original Meong Fly Stage/Flow is mounted directly at `d267d89`; custom game view removed. [CI 40043552747](https://github.com/pratikto/PhotoBooth/actions/runs/40043552747) has all three jobs SUCCESS. Reference remains `672e3f7`, 26 files byte-identical, 14 native FBO matches, 512 full PASS and 30 reviewed screenshots. Use MAIN GAME / VALIDASI DEMO 1X / II / PILIH LAYOUT FOTO. Preserve v2 async consumed ledger, native tutorial/12 templates, P3 acceptance and MOCK guards. Read [reuse proof/rollback](qa/portrait-v2-meong-reuse/README.md) and root AGENTS.md; no reinvented renderer or redundant doc-only GUI CI.

> **Owner reuse/cost rule (2026-10-24):** Do not reinvent an existing working feature. Inspect the latest relevant branch first, reuse its actual renderer/assets/animations as well as logic, and use a small adapter for integration. Record source SHA and concrete exceptions. Root [AGENTS.md](../AGENTS.md) makes this persistent for future sessions. Use small tested/pushed stages, local focused checks, one final full regression and matching-source CI; avoid redundant runs. Documentation-only portrait pushes are filtered, PR/manual checks retained, superseded runs cancelled by concurrency. This does not waive code validation or authorize other branches/production integration.

> **Current owner correction (2026-10-24):** Reuse the latest complete Meong Fly implementation; the prior custom game view is insufficient. Reference `672e3f7` verified at remote HEAD. Stage 1 imports original modules/tests (98 PASS); next mount the original renderer and flow through a narrow safe v2 adapter, test visual parity and push separately. [Current correction contract](qa/portrait-v2-meong-reuse/README.md).

> **Current P4 handover (2026-10-23):** P4a DEMO game and P4b opt-in local MOCK checkout are implemented at `97b5596`; final 406 full PASS, matching-source [three-job CI SUCCESS](https://github.com/pratikto/PhotoBooth/actions/runs/39973934595), 42 hash-verified/reviewed P4 CI captures and browser-verified 28-item Submit form. Run the existing v2 launcher; set PHOTOBOOTH_V2_CHECKOUT_MOCK=1 only for section C. P3 owner acceptance stands. Next is P4 Windows game/MOCK acceptance; real provider Sandbox/merchant promo contract remains external and is not enabled. Keep the same branch and push checkpoints. [Commands/evidence/open gates/rollback](qa/portrait-v2-p4/README.md).

> **P4a source checkpoint (2026-10-23):** Native DEMO game pages are connected after the accepted P3. 377 full PASS, 22 reviewed captures; preserve P3 photo/audio behavior. Continue P4b isolated MOCK on the same branch, then provide a P4 checkbox form with Submit. Real merchant/provider acceptance remains external. [Evidence and rollback](qa/portrait-v2-p4/README.md).

> **Current work — P4 (2026-10-23):** Owner says “p3 kan udah diuji.. lanjut p4 aja lah”. Continue P4a DEMO game → tutorial-once → existing gallery, then guarded P4b MOCK work, on the same required branch. P3 metadata does not block development. Stage-1 engine/ledger has 56 targeted PASS; connect native pages next, test and push in stages. P3 optional session-checklist WIP is saved locally in a named stash and is not shipped. Preserve the accepted camera/audio/photo behavior. [P4 contract and rollback](qa/portrait-v2-p4/README.md).

> **Latest P3 Windows owner acceptance (2026-10-23):** Owner submits all sixteen focused checks plus twenty cycles, no issue notes. Preview/button regression and optional physical-print cases are owner-reported PASS; monitor BUG-013/014 without speculative runtime changes or another mandatory twenty-cycle retest. Preserve unknown HEAD/OS/resolution/scaling/camera/index/speaker rather than borrowing earlier metadata. Collect metadata when available; full P3 unavailable-camera/reconnect and Drive/retention gates remain separate. Existing source and rollback checkpoints unchanged. [Acceptance record](qa/portrait-v2-preview-redraw/README.md). No payment/scanner/discount/game or further roadmap phase is activated.


> **Latest P3 handover (2026-10-23):** Approved P3a/P3b source work is connected on the required v2 branch; do not restart it. Next action is Windows P3 device acceptance using [the 34-item form with Submit](qa/portrait-v2-p3/windows-checklist.html). Start launcher → tutorial → gallery → select copies → UJI FOTO → consent. Default local; printer and Drive require operator opt-ins. Evidence, commands, source checkpoints, outstanding physical tests and BUG-009 boundary are in [P3 QA](qa/portrait-v2-p3/README.md). P4 game/receipt/payment integration and P5 physical certification are not complete/authorized by this source work. Older handovers below are history.


> **P3 execution authorized (2026-10-23):** Owner explicitly requests P3. Continue sequential P3a/P3b on `feature/portrait-kiosk-v2-next`, preserving commit/test/push/remote-HEAD gates. P3a uses one asynchronous camera and existing offline face/hold services; 86 focused PASS, full 321 run / 319 PASS / 2 optional skips, twelve unchanged captures. P3b must use explicit nonfinancial test admission and isolated storage for photo/print/Drive; payment/scanner/discount/game and master merge remain outside scope. [Evidence and remaining physical checks](qa/portrait-v2-p3/README.md). No repeated approval is needed for the authorized P3 implementation.

> **Current portrait v2 continuation (2026-10-23):** Stay on `feature/portrait-kiosk-v2-next`. Owner replied “sudah oke” after the return-to-advert correction/diagnostic instructions: BUG-012 is OWNER-REPORTED PASS / MONITORING. Keep the original 33/35 five-cycle failure report as history; post-update HEAD/cycles remain unknown. No further crash patch while it works. F05/F06 twenty-cycle and exact-HEAD acceptance remain pending. [Confirmation, source checkpoint and recurrence instructions](qa/portrait-v2-return-ad-crash/README.md). Do not expand into gameplay/payment/scanner or merge to master.

> **Current portrait v2 continuation (2026-10-22):** Work only on `feature/portrait-kiosk-v2-next`; do not create another branch or merge. Owner's ten-cycle Windows retest reports startup/swipe/audio/resize success but leaves tested HEAD unknown and twenty-cycle duration unverified. Gallery now emphasizes the strips, uses floating arrows, real image motion and display-only Meong Fly pixel typography; response warmup is source `67e9da8` (three-job CI SUCCESS). Local visual-stage checks: 71 focused PASS, full 306 run / 304 PASS / 2 optional skips, three 150% density checks and thirty reviewed PNGs. Visual source `5a568bf` also has exact-SHA three-job CI SUCCESS (39803887478); its original artifact is downloaded, digest/hash verified and visually reviewed. [Evidence, rollback references and pending Windows retest](qa/portrait-v2-gallery-focus/README.md). Keep new owner acceptance open and real transactions/scanner/gameplay inactive.

> **CURRENT RELEASE BASELINE (2026-10-19):** Default branch `master` contains Meong Photobooth Kivy GUI. Immutable source snapshot `v1.0.0` / `07ce51d2022ab5673a7a27e744e5e5757fbb3d08` is published as a [GitHub pre-release](https://github.com/pratikto/PhotoBooth/releases/tag/v1.0.0). Release-SHA CI: [Kiosk GUI 39185986245](https://github.com/pratikto/PhotoBooth/actions/runs/39185986245) (**233 pass, 2 skipped, 87 synthetic renders, 0 errors**) and [Dither 39185986273](https://github.com/pratikto/PhotoBooth/actions/runs/39185986273) (**48 tests pass**). Linux mock/screenshot QA is **not** certification on Windows hardware or customer deployment. Outstanding: BUG-001/007 audio speaker retest, BUG-009 30-day Drive cloud retention **OPEN**; QRIS is DEMO/non-payable (FEAT-020 not implemented), receipt scanner FEAT-002 not implemented. The earlier `feature/kivy-gui` branch and dated narratives below are **historical** where they conflict with this baseline.

> **Next continuation (2026-10-21):** Read the CURRENT FEAT-022 handover below before any portrait GUI work. Owner Windows audible speaker/10.1-inch touch and existing BUG-009 retention checks are still priorities. Historical PR #3 promotion is complete; no portrait v2 merge to master is approved.

**Repository:** https://github.com/pratikto/PhotoBooth  
**Target baseline:** `master` for stable code; new approved changes go to a dedicated task branch (`fix/*`, `feature/*`, or `docs/*`) and through PR review. **Tag:** `v1.0.0` stays unchanged.  
**Handover updated:** 2026-10-21 for FEAT-022 branch follow-up; older sections preserve their dated historical evidence from 2026-10-17 onward.

## CURRENT HANDOVER — FEAT-022 portrait GUI v2 + approved artboards (2026-10-21)

**Task authorization:** owner approved starting fresh greenfield GUI / isolated audio and using **a new branch**, then expressly requested **comprehensive feature-branch documentation including the last approved mockup images**. Current working branch: **feature/portrait-kiosk-v2-next**, created from the previously developed **feature/portrait-kiosk-gui** (39 pre-existing commits); the released **master/v1.0.0 remains unchanged**. This documentation-only continuation does not authorize camera/QRIS/game code integration, payment activation or master merge.

**Read first, in this order:** [primary FEAT-022 specification with both images](portrait-kiosk-v2.md) → [latest corrected nine-screen game + main visual spec](portrait-kiosk-v2-visual-spec.md) → [current technical/adapter boundaries](portrait-kiosk-v2-technical-design.md) → [feature status](FEATURE_STATUS.md) → [detailed test checklist](test_checklist.md) → [DEC-022 and DEC-003 tutorial-once decisions](DECISIONS.md) → [prioritized backlog](next_step.md). [Artwork checksums and archived older game board](assets/portrait-v2/README.md) document the provenance of the image evidence.

### Source and actual current behavior

- **New standalone v2 package:** photobooth/kiosk_v2/{app,flow,theme,audio}.py; launcher tools/run_portrait_v2.py. **python main.py continues to run legacy v1**.
- **Functional prototype:** idle advertising (reusing catalog and player), buttons for direct photo and Meong Fly, *manual visual* face invitation overlay on that same ad surface, four-step tutorial with acknowledged-once-per-visit state, real 12 original 80×240 mm three-photo + photo-QR templates with paper-copy count and DEMO quote. Existing game entry goes only to a clearly unavailable notice.
- **Audio source hardening:** SDL2-first valid-duration native WAV loading, SoundLoader fallback, fail-soft handling and stopped-after-play check (source commit [2b743da0](https://github.com/pratikto/PhotoBooth/commit/2b743da060b0493456bb810e32b61d8a9cc331dc); focused tests [caad0e0d](https://github.com/pratikto/PhotoBooth/commit/caad0e0dcd89be575942871f915f1a6bd910a003)). Does not close v1 BUG-001/007.
- **Not integrated in v2:** actual face detection, real Meong Fly game/struk reader/durable promo/discount, QRIS or Midtrans, camera capture/one-retake, physical printing, Drive upload/digital QR delivery, customer subscription licensing. Separate mature v1 and feature-branch implementations are not proof of v2 capability.

### Owner-approved visual source of truth and fixes

- [Main GUI concept](assets/portrait-v2/meong-main-flow-approved.webp): idle, invitation, tutorial, template carousel, QRIS concept, camera, review, final 3-photo strip.
- **[LATEST revised Meong Fly concept](assets/portrait-v2/meong-fly-revised-approved.webp): nine-screen board, now explicitly including MASUK MINI GAME before struk scan**. The earlier [eight-screen game board](assets/portrait-v2/meong-fly-flow-approved.webp) is **archival/superseded**, not the current target.
- Owner's subsequent functional corrections override sample mockup arrows and prices: both foto/game CTA live on the **same advertising/inline invitation**; a dedicated mini-game intro leads to struk; one unique struk = one consumed play, no Main Lagi; Win Rp2.500 candidate / Lose no discount; **both results → tutorial iff unseen → select original 12 templates → authoritative payment**. Final strip QR is for photos, never a payment QRIS; old concept Rp25.000 price is illustrative only. No app-code or payment integration is implied by storing the images.

### Actual QA evidence

[Portrait workflow run 39548798578](https://github.com/pratikto/PhotoBooth/actions/runs/39548798578) at code-plus-initial-artwork SHA **6e7f29a769b2ca19d09efa99b3bef21fb7b8bc86**: **21/21 Python unit tests PASS, compile PASS, Kivy widget smoke PASS, 12 synthetic screenshots PASS** at 800×1280 and 452×900, both jobs SUCCESS. The subsequent **revised game artboard and document-only commits do not change the code under test**, but must have their own Actions/contents status checked when preparing a PR. The older prototype [run 39522764587](https://github.com/pratikto/PhotoBooth/actions/runs/39522764587) (16 tests) is historical.

**No Windows physical speaker/test UI evidence** has been provided for this source. Do not confuse SDL2 play acknowledgement, virtual 452×900 Xvfb screenshots, simulated Video/UI or a GitHub PASS with operator audio, touchscreen, camera, payment, printer or Drive signoff. BUG-009 photo-retention cleanup remains open.

### Required next action (do not silently broaden code scope)

1. **Owner Windows trial:** git fetch origin, git switch feature/portrait-kiosk-v2-next, git pull; record git rev-parse HEAD; run python -m unittest tests.test_kiosk_v2_flow tests.test_kiosk_v2_audio tests.test_kiosk_v2_widgets -v; launch python tools/run_portrait_v2.py.
2. Verify idle advertisements (image/video and optional source audio), inline invite (currently manual), tutorial-once and carousel, accurate approved strip masters, game unavailable label, portrait 10.1-inch tap/scroll, **audible music automatically** on Tutorial/Template and truthful UJI MUSIK. Provide exact source SHA, speakers/provider, screenshots and PASS/FAIL feedback.
3. Compare actual 800×1280 screenshots with [approved visual spec](portrait-kiosk-v2-visual-spec.md) and record visual gaps. Then request the owner's explicit scope approval before building further P3 camera/face/print/Drive adapters or P4 standalone game/QRIS integration.
4. Preserve existing paid/uncertain visit journals, receipt attempt ledger, printer profile, photo files and v1 return path; no destructive reset or unapproved master merge. Resolve duplicate FEAT-021 labels (Meong Fly vs Background Studio) before cross-branch registry integration.

**Rollback:** simply return to master / launch legacy python main.py; do not revert/deploy master, remove branches, or force rewrite customer data. Branch CI/source success is not v2 release acceptance.

## Historical QA handover — Kiosk GUI Regression FULL CI PASS (2026-10-18)

**Owner-approved remediation completed:** Prior **Kiosk GUI regression FAIL** is now **VERIFIED PASS** on [run 39144464476](https://github.com/pratikto/PhotoBooth/actions/runs/39144464476) at source/test SHA [`f129dd9e`](https://github.com/pratikto/PhotoBooth/commit/f129dd9ecb14b2d554dd83022745452764f5282d). The full Kivy `unittest` suite performed **232 tests: 230 passed, 2 skipped, 0 failed/errors**; the visual renderer produced **87 scenarios / 0 errors** and the workflow concluded **SUCCESS**. A later [**HEAD `c40f33f5` CI run 39145145762](https://github.com/pratikto/PhotoBooth/actions/runs/39145145762) also completed SUCCESS**. Reconciliation documentation commits after that snapshot must be verified separately.

**Diagnosis:** Kivy swallowed unittest stderr in GitHub logs; `tools/run_kiosk_unittests.py` now captures a full standard unittest report to OS stdout and a CI artifact. The readable full-suite baseline exposed **17 outdated assertions**, reduced to four then zero. Repairs affected test expectations for FEAT-001 base-plus-copy pricing and one capture per template; ad → tutorial → layout flow; current Settings → Audio submenu and explicit music audition restart; deterministic fake completion of async print batches; mock Windows QR print routing without touching the real host OS. A one-off intermediate `payment-enlarged-800x600` visual decode failure was not reproduced in the final complete **87/87** render; continue monitoring rather than falsely claiming a separate QR production fix.

**Touched code is QA-only:** `.github/workflows/kiosk-gui.yml`, `tools/run_kiosk_unittests.py`, selected `tests/test_*.py`. **Zero production `photobooth/` modules**, zero `Code.gs`, no payment or printer modifications, no branch merge/deployment. The earlier physical FEAT-001/BUG-011 print and FEAT-003 mirror successes remain owner-tested evidence, independent of this Linux CI pass. Deferred BUG-009 Google Drive retention and BUG-001/007 speaker/audio symptoms are **not** closed.

**Next work:** no additional Kiosk CI remediation is warranted while the latest SHA stays green. Verify the current reconciliation's final HEAD workflow, then return to the backlog after fresh approval; FEAT-008 health checks remains the next normal feature candidate. No further development is approved merely because the CI quality gate is green. Canonical evidence: [Kiosk GUI full regression record](qa/KIOSK-GUI-REGRESSION-2026-10-18.md) and [test checklist](test_checklist.md). Roll back only QA tooling/tests if needed; never reset the accepted printer/camera branch to a pre-feature state.

## Historical FEAT-003 implementation/acceptance detail — CURRENT PASS remains valid (2026-10-18)

**Scope/approval:** Owner explicitly requested proceeding with FEAT-003 on the existing `feature/kivy-gui` branch. Baseline `c0cb0d84`. The present GUI implements only **capture-page** live camera previews; FEAT-002 receipt scanner and detection bounding boxes are **still backlog**. The user wants **all current and future live camera views mirrored**, but the approved delivery here implements only the existing live screen and establishes the shared rendering policy for later screens.

**Code delivered:** [`6f8c8ddf`](https://github.com/pratikto/PhotoBooth/commit/6f8c8ddfcb53d35070213c6fda72b8485232f280) adds `PhotoBoothUI._new_display_texture(..., mirrored=False)`, the existing mandatory vertical UV flip and an opt-in horizontal UV flip. Both first Pillow/ready/countdown/retake preview `update_live_preview` and streamed BGR `update_live_frame` request mirrored=True. There is **no `cv2.flip` on the shared frame**: capture, face/palm recognition, JPEG, review, final layout, QR and thermal printing remain unmirrored. No changes to `app.py`, `camera.py`, payment, printer or `Code.gs`. Synthetic GPU test committed in [`e99cbb26`](https://github.com/pratikto/PhotoBooth/commit/e99cbb26b485d7497642953c04e09c223dab0c6c) with callback cleanup; [dedicated CI workflow `feat003-mirror.yml`](../.github/workflows/feat003-mirror.yml).

**Verified independent CI and field evidence:** [FEAT-003 run 39139208320](https://github.com/pratikto/PhotoBooth/actions/runs/39139208320) at `307e779e` **PASS**, 1 focused synthetic Kivy GPU test plus Python compile on Ubuntu/Python 3.12/Xvfb. It checks preview UVs, texture reuse and resize, unmodified BGR/Pillow inputs, saved/review/result orientation. **The owner has now separately tested the feature on Windows and explicitly said "sip udah sesuai. PASS"**. The assistant did not operate a physical camera or receive the exact checkout SHA or a per-case recorded test matrix. **Status: FEAT-003 IN SOURCE — OWNER TESTED PASS for current capture preview**, not a full Kiosk GUI regression/release signoff. **HISTORICAL failure is SUPERSEDED:** the full Kiosk GUI workflow later PASSED at `c40f33f5`; this does not represent a Windows hardware or release signoff.

**Next safe step:** FEAT-003 current capture behavior **is owner-tested PASS**; no further camera-mirror patch is warranted while working. For formal release evidence, collect exact local Windows SHA, per-case initial/countdown/retake checks and original saved/photo print comparison when convenient; a user acceptance statement alone should not be misrepresented as an instrumented matrix. The next normal backlog item is **FEAT-008 device health**, subject to explicit owner approval and existing CI gates. The future FEAT-002 receipt scanner/overlay remains separate and unimplemented. Full checklist: [test_checklist.md](test_checklist.md). **Do not change stable FEAT-001/BUG-011 printer logic.**

**Priorities unchanged otherwise:** FEAT-008 device health and FEAT-009 auto-start are still normal pending priorities, with FEAT-003 an owner-selected exception. Audio BUG-001/007 deferred; BUG-011 owner-tested PASS/monitoring; BUG-009 Drive 30-day-retention risk still OPEN/deferred with FEAT-004. FEAT-020 real QRIS deferred. More detailed current scope: [next_step.md](next_step.md) and [FEATURE_STATUS.md](FEATURE_STATUS.md).

## Historical FEAT-001 delivery and BUG-011 resolution — OWNER TESTED PASS (2026-10-18)

> **HISTORICAL / SUPERSEDED incident narrative below:** Initial copy-count failure and earlier Kiosk CI failures are retained as the debugging timeline. Current: owner-confirmed copies work; full Kiosk CI is green. This section is not an active repair instruction.

### BUG-011 paper-copy mismatch — owner confirms working after Windows RAW fix

Owner reports FEAT-001 **pricing correct but printed-sheet count wrong** on Windows (actual requested/output counts not yet recorded). Read-only investigation of `photobooth/printer.py` found **concrete RAW Windows spool finalization error**: `_send_windows_raw()` called `ClosePrinter` twice and **never called `EndDocPrinter`**. Fixed at [`41a51b5b`](https://github.com/pratikto/PhotoBooth/commit/41a51b5b31f6ef442557a1caec9bf9a9ae88da93). FEAT-001 previously sent N independent RAW jobs; changed to **one Windows RAW spool document** with N complete, identical image+cut payloads in [`4608fcc9`](https://github.com/pratikto/PhotoBooth/commit/4608fcc9ec96c8eabeb01ddbd64059830af2bf62) and [`e6d2f684`](https://github.com/pratikto/PhotoBooth/commit/e6d2f6840d4b5838e719f904bcc3b8443291193a). Mock Windows spooler and payload tests exercise one StartDoc/Write/EndDoc and N cut sequences; [targeted FEAT-001 Actions 39134970707](https://github.com/pratikto/PhotoBooth/actions/runs/39134970707) **PASS**, but does not establish successful actual paper output.

**Latest owner physical retest (2026-10-18):** After printer changes, the owner first replied **"sip udah bener"**, then explicitly confirmed **"bug 11 udah aku test dan lolos"**. Treat this as **OWNER TESTED PASS** on the Windows physical print-copy defect, alongside the accepted DEMO pricing; it is not merely inferred from the screen. Retain BUG-011 **MONITORING / not formally CLOSED or RELEASED** and FEAT-001 **IMPLEMENTED / owner-tested core behavior**. Exact per-case 1/2/3 cut-sheet counts, tested local SHA and printer queue name were not supplied, so do not retroactively mark each hardware checklist row VERIFIED. The [canonical QA dossier](qa/FEAT-001-BUG-011-acceptance.md) separates field report, targeted 15-test CI PASS ([run 39134970707](https://github.com/pratikto/PhotoBooth/actions/runs/39134970707)), and current full [Kiosk GUI CI FAIL 39135186022](https://github.com/pratikto/PhotoBooth/actions/runs/39135186022) at source/documentation baseline `f2f52e33`. **No further changes to the now-working print transport are recommended unless a regression is observed.** Other tasks (BUG-001/007 audio, BUG-009 Drive photo retention, FEAT-020 QRIS) retain their prior deferrals.

**The owner explicitly requested "kita lanjut feat1 aja"**, approving FEAT-001 as a narrowly scoped exception to general P3 transaction/payment feature sequencing. Do not infer approval for FEAT-007 durable paid-state recovery, FEAT-020 real QRIS, FEAT-002 promo settlement or any actual merchant charge. The QR shown at checkout must continue to say DEMO / non-payable.

**Current source:** `catalog.py` defines Rp5.000 per selected template/session plus Rp5.000 per physical copy; `workflow.py` quotes one 3-shot session per chosen template; `ui_kivy.py` labels copy counts; `app.py` sends **one batch per saved layout** with requested copy count; `printer.py` repeats N identical ESC/POS image+cut streams and finalizes Windows via `EndDocPrinter`/single `ClosePrinter`; `transaction_store.py` persists the copies and a `demo_order_pricing` record. This supersedes the earlier separate N-job print implementation described by historical commits. No automatic replay when transport status is uncertain. A manual `CETAK ULANG` is a deliberately requested **one extra sheet**, not a paid transaction. [Detailed code/test map and field-evidence gaps](qa/FEAT-001-BUG-011-acceptance.md).

**Print navigation:** `ui_kivy.show_result` now locks NEXT/SELESAI while `print_busy=True` and unlocks after `_finish_print_job` reports that the batch has stopped/completed; `test_kivy_gui.py` validates this gate, while the template-navigation test uses a deterministic stub printer. **Isolated FEAT-001 headless CI** was added via [`.github/workflows/feat001-pricing.yml`](../.github/workflows/feat001-pricing.yml) (commit `35775128`), to distinguish quote/session/manifest test results from the pre-existing Kiosk GUI full-suite failure. **Verified CI result:** [FEAT-001 pricing run 39131731784](https://github.com/pratikto/PhotoBooth/actions/runs/39131731784) on `dfd6e5fb` = **11 tests PASS, 0 errors/failures**. Initial broad lightweight QR test failed from absent `cv2` and was narrowed to the pricing/session/manifest suite; full Kivy/physical printing not certified.

**Quality/risk:** Owner-reported physical paper success is now recorded, but does not provide a per-case 1/2/3 log or certify all configurations. Formal release still needs mixed-template paper checks, crash/fault behavior, full GUI regression (subsequently **PASS at `f129dd9e` on [run 39144464476](https://github.com/pratikto/PhotoBooth/actions/runs/39144464476)**), supported printer variations and explicit release approval. No live QRIS payment was implemented. Pre-implementation rollback reference: [`5842a09f`](https://github.com/pratikto/PhotoBooth/commit/5842a09f6a4c6c771ef7f5f0d1a330d0b1040b42); a hard reset would discard many later unrelated commits, so use a **targeted reviewed revert only if ever necessary**.

**Other priorities unchanged:** FEAT-008/009 remain normal top-of-backlog features after this owner-selected work. BUG-001/007 postponed, BUG-008 monitoring, BUG-009 still OPEN/deferred alongside FEAT-004 with cloud privacy risk. Current canonical prioritization and FEAT-001 exception: [next_step.md](next_step.md).

## Earlier priority handover — owner decision 2026-10-18 (superseded by FEAT-001/BUG-011 update above)

**Target:** `feature/kivy-gui`; use the [unified execution board](next_step.md) rather than historical sections below. Owner explicitly deferred **all payment, transaction, checkout/pricing, receipt-promo settlement and paid-reprint development to execution P3 LOW** while real QRIS is absent. **NEW FEAT-020** captures future provider-backed real QRIS; the existing QR and payment confirmation are DEMO / non-payable. Before any real-money release, FEAT-001 pricing, FEAT-007 durable paid-state recovery and FEAT-020 provider verification must be coordinated. **This is a documentation decision, not approval for code or deployment.**

**CURRENT proposed nonpayment queue:** (1) FEAT-008 device health, (2) FEAT-009 generic Windows auto-start/crash recovery **without paid-transaction resume**, (3) **FEAT-003 already owner-tested PASS (removed from pending work)**, (4) FEAT-012 diagnostics, (5) FEAT-010 per-machine nonpayment config/identity, (6) FEAT-004 Drive advertising sync together with deferred, still-unverified BUG-009 cloud-photo retention, then visual/campaign features. GitHub Kiosk GUI CI remains an independent test gate, not proof of a payment defect.

**Existing owner deferrals and acceptance:** BUG-001/007 Windows audio remains failing but intentionally deferred; BUG-008 Settings currently responds and is MONITORING; BUG-004/010 print quality and dither-scroll are owner-reported PASS; BUG-009 remains OPEN/deferred to FEAT-004 with unresolved 30-day Drive privacy risk. Old handover notes below (including 'BUG-004 OPEN' and an isolated lab not yet merged) are **historical**, superseded by later [bug tracker](bug_tracker.md), [feature status](FEATURE_STATUS.md) and current branch commits. No new hardware validation, unit tests, payment onboarding, gateway changes or release is claimed by this documentation update.

## Isolated owner-authorized experiment — `feature/dither-tuning` (2026-10-18)

The owner expressly requested a **NEW branch** specifically for configuration of dithering algorithms and tuning parameters, overriding the usual no-new-branch default **for this task only**. New branch `feature/dither-tuning` originates from `feature/kivy-gui` at `5e0a8980968430b85f04ebac1b6c1574c2191a69`. First isolated FEAT-011 source commit: [`07dcb1a`](https://github.com/pratikto/PhotoBooth/commit/07dcb1a5115f978e70b90c08e5a3666e077bb229). Lab instructions in [dither-tuning-lab.md](dither-tuning-lab.md). [Dedicated CI 39110869478](https://github.com/pratikto/PhotoBooth/actions/runs/39110869478) PASS (compile + targeted unit tests); Windows GUI, native printer output and quality still require owner verification. Kivy GUI app, printer transport and payment QR code are not modified. **Do not merge to `feature/kivy-gui` or `main` without new owner authorization.** This temporary exception does not authorize branching other features.

**FEAT-011 next steps:** test Windows `python tools/dither_tuning_gui.py`; compare actual saved photo PNG and zoomed raster using preset, export binary PNG; confirm the outputs on real paper (same width/brightness/density). Retain BUG-004 OPEN. Known BUG-008 (Settings hang) and BUG-009 (Drive retention deployment) remain unrelated active operational issues; building a standalone lab does not fix them.

## Historical handover snapshot — reconciled 2026-10-18 (superseded by v1 top section)

**Read this first rather than treating the dated 2026-10-17 notes below as an active work order.** Source-of-truth documents:

- [Documentation index](README.md), [reusable development prompt](DEVELOPMENT_PROMPT.md), and root [README](../README.md) (current status banner and historical project setup).
- [DECISIONS.md](DECISIONS.md): owner-confirmed commercial/product behavior versus proposals.
- [FEATURE_STATUS.md](FEATURE_STATUS.md): actual source implementation versus user-reported physical acceptance.
- [bug_tracker.md](bug_tracker.md): operational defects and stable IDs.
- [test_checklist.md](test_checklist.md): evidence classifications and real on-device acceptance.
- [next_step.md](next_step.md): **one unified provisional feature queue** plus parked business ideas. Detailed old intake ranks are historical, not authorization.

**Current latest owner feedback (2026-10-18):** BUG-002 video in idle/payment, BUG-003 payment QR paper, BUG-005 tutorial route and BUG-006 opening ad size are **OWNER REPORTED PASS** and not in active fix queue. BUG-007 Settings test taps now receive events, button SFX and shutter SFX work, but `Uji Musik` emitted only the standard click; BUG-001 tutorial/layout background music remains inaudible while SDL2 reports `state=play gain=0.59`. The user explicitly approved targeted BUG-001/007 code+documentation changes. BUG-004 thermal print blur remains OPEN and outside the audio patch. Pre-existing CI full-suite run 39101639665 failed despite 87 successful synthetic renders. Audio change requires actual Windows speaker retest; do not infer physical pass from provider state.

**Current source verified by file inspection, NOT physical test:** `photobooth/printer.py` and `printer_settings.py` are already integrated into `feature/kivy-gui` with Windows USB queue/LAN/Wi-Fi and Floyd–Steinberg/Bayer/threshold. `photobooth/qris_print.py` receives saved GUI `PrinterConfig`; legacy LAN-only fallback is for direct callers. Payment remains a *non-payable demo*. `photobooth/catalog.py` still uses IDR 5,000 per independent session/quantity, and `workflow.py` captures 3 photos **per quantity**. Do not describe proposed per-copy pricing as working.

**Future direction is documented, not delivered:** FEAT-001 base fee + per-physical-copy pricing (still 3 captures per chosen session); FEAT-002A dummy external receipt scanner and FEAT-005A standalone ordering demo with automatic same-device photo promo; FEAT-003 mirrored live preview only; FEAT-004 per-machine local-first Drive ads; FEAT-006 GUI themes; FEAT-007–018 reliability, promotional reporting and fleet enhancements; BIZ-001/FEAT-019 sale of hardware with mandatory assigned Free/Business/Enterprise tier. Free remains commercially usable and all its ads belong to Meong; paid users may control some ads while Meong retains **unspecified** reserved slots on every tier. No paid-tier licensing, ad quota enforcement, merchant POS integration, or live QRIS is represented as shipped.

**Funding rule:** merchant pays the waived base-fee promotion only when redeemed; the settlement recipient is the Meong-operated booth owner or a separate sold-machine operator according to who funded the discount and the contract. Do not call every merchant reimbursement Meong revenue.

**Execution gate:** Bug reproduction, device evidence and documentation review first. Before implementing any fix or feature, secure **separate explicit user approval of that code scope**. Use only `feature/kivy-gui`, preserve the thermal-printer branch, avoid accidentally overwriting local Windows changes, run targeted tests + full regression after authorized code, and require real device/owner signoff for printing/audio/video. This housekeeping made **documentation edits only**.

## Audio scope authorized and applied — 2026-10-18 (BUG-001 / BUG-007)

- Base commit: `06dd977c06657c9b56e1de0ad18042b65515bd64`; changes on existing `feature/kivy-gui` only. Audio patch and paired tests/docs committed together; see branch history for the resulting commit.
- `audio.py`: full-gain SDL2 music restart after returning from ad fade, deliberate music audition that reacquires the mixer channel while honoring mute/paused/ad rules. `ui_kivy.py`: Uji buttons bypass the generic click and explicitly audition music, button or shutter; diagnostic text uses a real newline.
- Added unit and real-widget regression expectations. **Post-change CI for code SHA `b69d3837`:** [run 39104614520](https://github.com/pratikto/PhotoBooth/actions/runs/39104614520) had Python compile PASS, full `unittest discover` FAIL (exit 1, test identity not exposed in job log), GUI render PASS (87 renders, no reported render errors), visual summary PASS. The preceding baseline CI already failed the same broad test step; a targeted audio suite has not been independently verified. No Windows speaker verification performed by GitHub Actions.
- **New owner Windows audio-unit evidence (2026-10-18):** `python -m unittest tests.test_audio -v` = **14 run, 13 pass, 1 skipped, 0 failures** in 2.539 s; Windows with Python 3.12.10, Kivy 2.3.1. Includes PASS for both the fade-after-ad test and forced music-audition test. Native audio opt-in check was skipped. Working-tree SHA was not present in shared command output. This test evidence **does not prove speaker audibility**.
- Next owner test: verify `git status` / current HEAD, launch `python main.py`; idle ad -> tutorial -> layout (music must be heard without Settings); open Sound Settings and tap Uji Musik, Uji Tombol, Uji Efek kamera; verify each emits only its intended sound; test 0%/restored music volume, advert muted application BGM and next user round. Record both result and diagnostics if still silent.
- Next repair queue: BUG-004 thermal print blur and independent CI regression investigation only with their own approvals.

## Recommended next engineering investigations (historical 2026-10-18 list; now superseded by owner feedback)

1. Audio settings pointer/touch diagnostic (BUG-007) and application audio lifecycle (BUG-001), with logs distinguishing missed button events from mute/routing.
2. Idle/payment MP4 decoder and texture playback on actual Windows hardware (BUG-002). Test visible moving frames with supported codec; the user's original sample files were noted to lack audio streams.
3. Payment QR print worker and selected saved Windows queue (BUG-003). Collect worker result, spooler messages and paper; never claim successful print from an ESC/POS file alone.
4. Native-width source-to-raster photo quality comparison (BUG-004); compare existing dither modes and physical output, separate photo from QR printing.
5. Manually verify tutorial route, ad stage sizing and complete payment/capture/print flow (BUG-005/006), then revisit feature priorities.

## Resume checklist

1. Read [this updated handover](#current-handover--reconciled-2026-10-18), [Architecture](ARCHITECTURE.md), [Feature status](FEATURE_STATUS.md), [Decisions](DECISIONS.md), [Bug tracker](bug_tracker.md), [Feature backlog](next_step.md), [root README](../README.md), and [Advertising and QRIS](advertising-and-qris.md).
2. Fetch the **current** branch head and inspect working files before editing. Never assume older chat claims are committed.
3. Only after explicit owner authorization, address reported defects **one by one** in small, reviewable commits. Keep detailed English comments. Do not modify the separate thermal-printer branch.
4. Run targeted unit tests, then broad regression suite and real Kivy screen checks; document commands/results and unverified physical tests.
5. Update `FEATURE_STATUS.md` and this file after each fix, then verify commit/push and link the resulting SHA.

## Historical initial coding priorities (2026-10-17; superseded by current bug tracker)

**A. Video playback fails on both idle and payment (partial configuration fix committed 2026-10-17).** Inspect `ui_kiosk.py`, `advertising.py`, `requirements.txt`, ad playlist paths and Kivy video provider/ffpyplayer lifecycle. Distinguish absent local video media, failed decoder, texture not attached, muted media and stalled playback. Ensure payment playback is **muted**, not disabled. Add diagnostic logging and tests for both placements. The bundled playlist now auto-discovers video files from the repository-root `ad_video/` directory (alphabetical order, arbitrary filenames and supported extensions), for both placements. Still-image poster entries remain as fallback. Videos are NOT committed to GitHub; local decoder and actual playback remain to be verified. Custom `PHOTOBOOTH_AD_CONFIG` playlists remain explicit and do not use automatic discovery. Runtime decoder/frame testing is still outstanding; do not claim videos have been uploaded or playback fixed.

**B. Enlarge the initial ad area (source change committed 2026-10-17).** The idle page now uses up to 1920dp width, narrow gutters and a shorter header; video retains `contain` sizing, and Start/face-offer controls remain outside/on the stage. Real-widget render checks at 800×600, 1200×800 and 1920×1080 are still pending.

**C. Fix music initialization (fade-in fix committed 2026-10-17; device verification pending).** Trace `KivyHost.build/on_start`, `AudioManager.start`, initial advertising audio ownership and transition into the guide. Check why opening Settings appears to initialize playback. The audio fade now explicitly restarts music as volume rises from zero, without requiring Settings. Preserve intentionally silent application music while source-video advertising is active; verify this fix on the user's speaker and when entering tutorial/photo flow.

**D. Enforce ad -> tutorial -> layout picker (source change committed 2026-10-17; device QA pending).** Both advertising manual Start and face-invitation acceptance now open the illustrated tutorial. The tutorial's Start control continues to invoke the existing layout-selection controller. Regression coverage added in `tests/test_tutorial_entry.py`; test execution and hardware UI navigation verification remain pending.

## Acceptance criteria

- Both configured image and compatible local MP4 ads render/advance on idle and payment pages; payment ad audio remains muted.
- Idle video is visibly larger without cropping/distorting or hiding Start.
- Music begins on entry to tutorial/photo flow without touching Settings; user-selected mute is respected.
- Both Start routes lead to tutorial before the user can select a layout.
- Existing template/session/retake/QR demo/Drive flows and their tests continue to pass.
- Status and handover docs reflect **observed** behavior, not aspirations.

## Important limitations

Physical machine speakers, local media/codec setup, camera, Google Drive and LAN thermal printer cannot be validated from GitHub alone. Real QRIS is not yet supported. Previous automated QA results are historical, not validation of the four newly reported defects.

## Historical copy/paste prompt (2026-10-17; superseded — use DEVELOPMENT_PROMPT.md)

The maintained full and quick prompts are in [DEVELOPMENT_PROMPT.md](DEVELOPMENT_PROMPT.md). The compact starter below references that single canonical prompt rather than maintaining a divergent second checklist:

> Historical 2026-10-17 resume advice (superseded): the then-current `feature/kivy-gui` branch was the development target. **Do not copy this old branch instruction.** Use the maintained [reusable prompt](DEVELOPMENT_PROMPT.md), start from `master`/`v1.0.0`, and seek explicit task approval for new changes, PR merges, deployment and physical signoff.

## Current blocker: audio remains silent (reported 2026-10-17)

The prior music fade-in commit has **not** solved output on the user's machine. Do not mark audio done. The original three sample clips are documented as silent video sources, so test advertising sound with a **known audio-bearing video**. On the user's machine, collect console/Kivy provider logs, check `PHOTOBOOTH_AUDIO`, `KIVY_AUDIO`, persisted `data/audio/levels.json`, actual selected sound output, and run `PHOTOBOOTH_TEST_AUDIO=1` native Kivy test with the real output (not dummy SDL driver). Verify whether the music sound handle enters `play` on tutorial and whether it reaches audible output. Fix based on those observations, add targeted regression test and update status.

## Retest after fade-gain fix — 2026-10-17

A Windows test run reported 1 failure in `test_music_autostarts_when_advertising_fades_into_tutorial`: sound state was `play` instead of expected `stop` before gain increased. A follow-up change defers `_ensure_music` when `_music_mix <= 0`. Next run `python -m unittest tests.test_audio -v`; then run the opt-in native audio checks with `$env:PHOTOBOOTH_TEST_AUDIO='1'` and `python -m unittest tests.test_audio.AudioTests.test_real_provider_starts_music_and_loads_every_cue_from_a_fresh_install -v`. Clear this environment flag afterward. For advertising audio, test a video that genuinely contains an audio track. Report whether the tutorial song and Settings' Uji music are audible.

## Audio diagnostic update — Windows checks passed 2026-10-17

The user ran all standard audio unit tests: 12 passed, 1 opt-in native test skipped. The separately enabled native audio test passed and logs show all five WAV handles loaded via SoundSDL2, with ffpyplayer and SDL2 providers available. No assertion failures remain in these checks. This does **not** verify speaker output. Next obtain one direct observation from user: is the song audible when entering the tutorial and/or pressing `Uji Musik` in Settings? If still silent, check Windows Volume Mixer and current output device, user preferences, environment flags, and Kivy logs before more source changes. Advertising samples were documented as containing no audio track; verify with ffprobe or another known audio-bearing video.

## Speaker diagnostic — 2026-10-17

User confirms no audible music in the full app despite passing native provider tests. Added `tools/check_audio_output.py` to isolate SDL2 audio output without Kivy GUI/page ownership. Run `python tools/check_audio_output.py` from repo root, listen for five seconds, and inspect Windows Volume Mixer for Python and the selected device. If direct test sounds, investigate full-app audio lifecycle/mute settings; if it is silent, investigate Windows/SDL2 routing or device. Do not mark the bug fixed based on native `play` state alone.

## Diagnostic script import correction — 2026-10-17

The first attempt at `python tools/check_audio_output.py` stopped with `ModuleNotFoundError: No module named 'photobooth'` before any music playback, because direct script execution excluded the repository root from `sys.path`. Fixed the script to insert its checkout root. The user's report of no sound from that attempt does **not** establish an audio-device failure. Rerun after pulling and report output and whether 5 seconds of audio are audible.

## In-app diagnostic update — 2026-10-17

User confirms `python tools/check_audio_output.py` makes audible music, whereas `python main.py` remains silent. Therefore SDL2 can deliver audio on their machine; actual app audio is **not fixed**. Added a live Settings diagnostic line showing `provider`, `state`, `gain`, persisted `level`, fade `mix`, `advert`, `paused`, `started`, number of loaded `sounds` and `enabled`. Reproduce with Settings open on **tutorial** and report the complete diagnostic line and whether `Uji` is audible. `advert=1` on the opening advertising screen is expected (app music suppressed); a silent source MP4 has no ad audio to output. Do not claim audible application music until user confirms.

## Integration staging — 2026-10-17

The latest advertising/tutorial GUI is the integration base. Thermal printer
modules, saved settings, Windows RAW spooler, three dithering modes, operator
settings popup, test print callback and result-page print worker/reprint have
been copied and adapted to `feature/kivy-gui`. The separate printer branch is
kept as a backup; PR #2 shows the unmodified branch-to-branch merge conflicts.
Hardware tests are pending; the real video/audio bug remains unresolved.

**Do not delete old branches.** Before publishing to `master`, run
`python -m unittest discover -s tests -v`, launch `python main.py`,
verify entry via ad/tutorial, checkout demo and printer settings, and test
Windows RAW paper output. A successful print spooler job does not prove paper
output. Check UI screenshots at desktop resolutions and the persistent
`data/printer_settings.json`. Importantly, this branch now integrates printer
features from the older printer branch without replacing recent advertising
or payment behaviors.

## Windows QA feedback (2026-10-17)

User's local Windows `python -m unittest discover -s tests -v` reported
172 tests, four errors and 69 skips. Three printer import errors originate
from **local unresolved merge artifacts** (`<<<<<<< HEAD` in
`tests/test_printer.py`, and a 661-line `photobooth/printer.py` with an
unterminated string) rather than the current GitHub `feature/kivy-gui` files
(which contain no conflict markers and whose printer module has 625 lines).
Do not overwrite uncommitted local edits; inspect `git status`, abort only
an active unfinished merge/rebase if appropriate, then refresh the working
tree safely. The fourth error was a Windows permission restriction when
creating a symlink in the retention test; that specific `WinError 1314`
condition now skips the symlink-specific test while preserving other errors.
Re-run full and opt-in GUI tests before merging PR #3 into `master`.


## FEAT-022 — Portrait GUI v2 owner-approved independent branch (2026-10-21)

Target: feature/portrait-kiosk-gui, originating from master SHA 27f3801b235d81dc0a49ab201f3e143b62314413; do not merge to master. Owner chose greenfield portrait 10.1-inch GUI and new sound lifecycle because v1 music audibility remains unresolved, while reusing stable backend services. Status: initial GUI prototype source (advertising/media, invitation preview, tutorial, 12-template gallery/quantities) and audio controller/tests committed; Windows speaker, actual face detection, game integration, payment/camera/Drive/printing all unverified or intentionally disconnected. Entry: python tools/run_portrait_v2.py; python main.py still launches original v1. Technical/QA stages in portrait-kiosk-v2.md. Complete the new branch CI and Windows portrait/touch/audio checks before expanding into actual camera/transaction integration. Existing BUG-001/007 and BUG-009 are not closed by this work; record exact test result/commit before any acceptance. The DEC-003 tutorial-once addendum from docs branch commit 980af997 was brought into this branch, without merging that documentation branch or master.

### FEAT-022 first prototype CI review — 2026-10-21

P0–P2 Python and synthetic Kivy verification is now available at [portrait CI 39522764587](https://github.com/pratikto/PhotoBooth/actions/runs/39522764587): 16/16 navigation/fake audio tests PASS, Kivy widget smoke PASS, 12 screenshot states recorded at 800x1280 and 452x900. Real photos/printing/QRIS and audio speaker not included. Previous compact 450x900 screenshots were corrupted by Xvfb RGB alignment; the renderer detects row corruption and uses 452-wide aligned evidence, **not** a physical 450-wide QA substitute. Source at `d85bb62a` additionally removes unsupported arrow glyphs. Next safe work: owner Windows walkthrough of `python tools/run_portrait_v2.py` including visible actual ad video, correct interactive controls, actual audible music with UJI MUSIK, and portrait 10.1-inch responsiveness. Then continue visual polish and introduce backend adapters only under tested, separately approved integration stages. [Draft PR #10](https://github.com/pratikto/PhotoBooth/pull/10) remains unmerged.


### FEAT-022 — follow-up branch and new PCM audio acceptance gate (2026-10-21)

To avoid overwriting 39 existing prototype commits, follow-on work now uses `feature/portrait-kiosk-v2-next` based on `feature/portrait-kiosk-gui`. Source commits: workflow `ab551ba3`, SDL2-first/v2 PCM loader `2b743da0`, regression additions `caad0e0d`; documentation in `docs/portrait-kiosk-v2.md`. `master` remains unchanged; no game/QRIS/photo backend integration is implied. Inspect fresh Actions results for this new branch (not its ancestor), then run Windows operator audible speaker and portrait touch validation using the documented command. Only after evidence-backed v2 audio/screen acceptance, continue staged photo-service adapters. BUG-001/007 (old v1) and BUG-009 remain unresolved/unaffected. Never merge without explicit owner approval.

### FEAT-022 P2.5 follow-up — polished real Kivy prototype / verified CI (2026-10-21)

**Active branch:** `feature/portrait-kiosk-v2-next`; master/v1 unchanged and no merge approval. **Current source:** `photobooth/kiosk_v2/illustrations.py` added; `theme.py` updated with Pixel Arcade Space stars/buttons/cards; `app.py` now renders advertisement-first dual photo/Meong Fly access plus Cara Pakai; nonmodal manual face invitation, four illustrated tutorial steps, three simultaneous genuine thermal strip previews with proper paper-copy count and horizontal swipe gesture, and a responsive **dedicated Meong Fly INTRO**. Scan Struk CTA is disabled and `LANJUT FOTO TANPA GAME` safely reaches the normal tutorial/12-template flow. Four routes only (advert/tutorial/templates/game_preview), no game result/QRIS/camera/print/Drive implementation.

**Test source:** [Actions 39555036023](https://github.com/pratikto/PhotoBooth/actions/runs/39555036023) on SHA `c4e4703a` — 21 pure tests PASS; modified Kivy widget smoke PASS; 12 synthetic portrait states at 800×1280 / 452×900 PASS, both jobs SUCCESS. Screenshots from CI artifacts were inspected; the compact Meong Fly intro no longer shrinks the mascot. No speaker/touchscreen hardware acceptance. The previous temporary failure on 39edb3ab's old widget assertion has been superseded by new 3-preview tests and a later green run.

**Next action:** Operator checks Windows speaker autoplay, source ad video/audio, real 10.1-inch landscape-to-portrait orientation, four tutorial cards reachable by vertical scrolling at compact heights, direct Foto/Game and in-ad invitation callbacks, swipe left/right vs vertical scroll, 12 1:3 preview identities and DEMO cart copy totals. Use commands in [test_checklist.md](test_checklist.md), capture exact SHA/versions/logs and sanitize any real photos. Verify sound with ears, not just SoundLoader state.

**Next code gate:** After on-device acceptance, request explicit owner approval for isolated P3 camera/retake/thermal/Drive adapters, then separately for live face invitation and P4 Meong Fly ledger + QRIS/discount; preserve 1 receipt = 1 consumed attempt, no replay, tutorial once then 12 templates, no free voucher issued via GUI text. Fix duplicate FEAT-021 registry before merging other branches. Keep BUG-001/007 Windows music and BUG-009 photo retention open until device/cloud evidence. Never merge to master or delete branches without owner instruction.
