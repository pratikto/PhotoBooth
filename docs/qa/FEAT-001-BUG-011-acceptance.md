# FEAT-001 and BUG-011 — DEMO pricing, thermal copy count and Windows acceptance

> **CURRENT ACCEPTANCE (2026-10-19): FEAT-001 DEMO base-per-template + copy pricing and **BUG-011 Windows paper copy-count owner-tested PASS / monitoring**; targeted [15/15 CI PASS](https://github.com/pratikto/PhotoBooth/actions/runs/39134970707). The **full Kiosk GUI CI later passed** at SHA `c40f33f5` ([run 39145145762](https://github.com/pratikto/PhotoBooth/actions/runs/39145145762): 230 PASS/2 SKIP/87 renders). Old FAIL runs and the initial paper mismatch below are **HISTORICAL**. No recorded per-case count matrix or formal release signoff.**

**Evidence date:** 2026-10-18  
**Repository / branch:** [`pratikto/PhotoBooth`](https://github.com/pratikto/PhotoBooth) / `feature/kivy-gui`  
**Baseline before FEAT-001:** [`5842a09f`](https://github.com/pratikto/PhotoBooth/commit/5842a09f6a4c6c771ef7f5f0d1a330d0b1040b42)  
**Source fix present by:** [`41a51b5b`](https://github.com/pratikto/PhotoBooth/commit/41a51b5b31f6ef442557a1caec9bf9a9ae88da93)  
**Latest owner feedback:** "**pricing udah bener**" followed by a print-count failure; after the Windows RAW fixes, "**sip udah bener**" and subsequently the explicit on-device test confirmation **"bug 11 udah aku test dan lolos"**.  
**Current classification:** **FEAT-001 IMPLEMENTED / OWNER-TESTED CORE BEHAVIOR; BUG-011 OWNER TESTED PASS — MONITORING**, **not formally CLOSED/RELEASED**. The precise Windows checkout SHA, measured counts per test, printer driver/queue name, device log and paper photographs were not supplied. A user report is field evidence but does not imply every regression scenario ran.

## 1. Product contract and limits

- A **selected template** means **one photo session**, taking three pictures and allowing the already-defined single retake; there is **one saved final composition** per selected design/session.
- The template picker **+ / − controls requested physical paper copies** of that same completed composition, not additional camera sessions. Quantity `0` deselects the design.
- DEMO price per selected template: **Rp5,000 base fee + Rp5,000 × requested copies**. No payment-provider or settlement integration exists. The payment QR is explicitly **DEMO/non-payable** and separate from the Google Drive photo-folder access QR.
- Multiple selected templates each have their own base fee and one photo session; copying one template must not silently recapture or change another.
- The ordinary photo-printing path retains the owner-approved Floyd–Steinberg image processing; batch copies reuse the same generated ESC/POS image+cut stream. Non-Floyd comparison modes, QR-slip behavior and audio/advertisement policy were not targeted by BUG-011.

| Planned order | Expected photo sessions | Expected physical sheets | Expected DEMO total | Field evidence available |
| --- | ---: | ---: | ---: | --- |
| Template A × 1 copy | 1 | 1 | Rp10,000 | Owner confirms pricing and overall copy-count behavior; no per-case log |
| Template A × 2 copies | 1 | 2, identical | Rp15,000 | Owner confirms pricing and overall copy-count behavior; no per-case log |
| Template A × 3 copies | 1 | 3, identical | Rp20,000 | Owner confirms pricing and overall copy-count behavior; no per-case log |
| A × 2 plus B × 1 | 2 | 3 total, by selected layout | Rp25,000 | Automated model/manifest tests; actual mixed-template paper scenario not individually documented |

These are **acceptance expectations**, not invented claims that every row was individually observed.

## 2. History: symptoms, investigation and resolution evidence

1. **Initial FEAT-001 implementation:** session fee and print-copy fee were separated; one `SessionPlan` per selected design; `print_copies` and `demo_order_pricing` persisted. The first print-worker implementation called `print_image` repeatedly and created **N independent Windows RAW spool documents**.
2. **Owner finding:** pricing was correct on the local Windows booth, **physical printed-sheet count did not match** the chosen quantity. At that point, the exact requested/output pair was unavailable. The defect was registered as **BUG-011 (provisional S1)**.
3. **Source review:** Windows `_send_windows_raw` in `photobooth/printer.py` **omitted `EndDocPrinter` and called `ClosePrinter` twice**. That is a concrete printer-document lifecycle bug; absence of device telemetry prevents proving it was the *only* reason for the observed paper shortfall.
4. **Patch A:** [`4608fcc9`](https://github.com/pratikto/PhotoBooth/commit/4608fcc9ec96c8eabeb01ddbd64059830af2bf62) repeats a **complete rendered ESC/POS image + cut stream** for each copy, then sends **one payload** via LAN/Wi-Fi/USB. [`e6d2f684`](https://github.com/pratikto/PhotoBooth/commit/e6d2f6840d4b5838e719f904bcc3b8443291193a) changes the kiosk controller from N transport calls to **one batch**.
5. **Patch B:** [`41a51b5b`](https://github.com/pratikto/PhotoBooth/commit/41a51b5b31f6ef442557a1caec9bf9a9ae88da93) restores **`StartDocPrinter → StartPagePrinter → WritePrinter → EndPagePrinter → EndDocPrinter → ClosePrinter`**, closing the handle once and finalizing the RAW document.
6. **Regression:** focused print tests now require one transport submission with N image/cut sequences, one Windows RAW document and `EndDocPrinter` invocation. An initial workflow failure **exposed** the missing `EndDocPrinter`, then the corrected run passed; that failing check was not suppressed.
7. **Latest owner retest:** after the fixes, the owner first replied **"sip udah bener"** and then expressly clarified **"bug 11 udah aku test dan lolos"**. Record this as an **affirmative owner's hands-on PASS of BUG-011's physical copy-count behavior**. No automatic test run, screenshot, precise per-case count, queue name or exact local checkout SHA was supplied with that confirmation, so do not portray each 1/2/3 scenario or fault test as separately logged or declare a general release.

## 3. Source-of-truth map

| Module / path | Actual responsibility |
| --- | --- |
| `photobooth/catalog.py` | `PRICE_PER_SESSION=5000`, `PRICE_PER_PRINT_COPY=5000`; existing frame artwork and Floyd tuning remain separate |
| `photobooth/workflow.py` | `quote_order` computes DEMO totals; `build_session_plans` maps each nonzero design to one three-capture session with `print_copies` |
| `photobooth/ui_kivy.py` | Labels print-copy selection; displays cart amount; disables NEXT/SELESAI while print batch is reported busy |
| `photobooth/app.py` | Sends DEMO quote to payment screen, saves one final PNG, schedules one printer batch with requested copies, reports transport outcome; operator manual reprint sends one extra sheet |
| `photobooth/transaction_store.py` | Persists per-session `print_copies` and additive `demo_order_pricing`; **not a real payment or durable paid-fulfillment ledger** |
| `photobooth/printer.py` | Creates native ESC/POS raster using configured dithering; repeats full image+cut bytes `copies` times; transmits one batch; correctly finalizes Windows RAW spool job |
| `tests/test_workflow.py` | Business-rule/retake/manifest quote tests |
| `tests/test_printer.py`, `tests/test_windows_printer_spooler.py` | Mock LAN/USB batch count, cut commands, Windows spool lifecycle and invalid quantities |
| `tests/test_controller_flow.py`, `tests/test_kivy_gui.py`, `tools/render_gui.py` | Synthetic controller, navigation, price display and print-busy/UI scenarios; not equivalent to physical paper acceptance |
| `.github/workflows/feat001-pricing.yml` | Repeatable headless FEAT-001 tests independent of live camera, printer and QRIS |

## 4. Exact verification evidence and scope

| Evidence | Revision / environment | Outcome | What it does **not** establish |
| --- | --- | --- | --- |
| [FEAT-001 pricing & copy-count CI 39131731784](https://github.com/pratikto/PhotoBooth/actions/runs/39131731784) | `dfd6e5fb` · GitHub Actions Ubuntu / Python 3.12 | **PASS: 11 tests** (quote, session planning, retake and persisted manifests) | Windows spooler, physical camera, paper, real payment |
| [Initial expanded print CI 39134857847](https://github.com/pratikto/PhotoBooth/actions/runs/39134857847) | `dbeab0e7` · GitHub Actions Ubuntu / Python 3.12 | **FAIL:** Windows RAW mock test found absent `EndDocPrinter` | Not evidence the printer hardware itself failed on that runner |
| [Corrected multi-copy & spool CI 39134970707](https://github.com/pratikto/PhotoBooth/actions/runs/39134970707) | `41a51b5b` · GitHub Actions Ubuntu / Python 3.12 | **PASS: 11 business/manifest + 4 batch/spool tests = 15 tests**, syntax checks pass | Real Windows printer paper count, thermal cut, QR scannability, camera session |
| [Dither lab CI 39135186017](https://github.com/pratikto/PhotoBooth/actions/runs/39135186017) | `f2f52e33` · GitHub Actions Ubuntu | **PASS** at prior documentation baseline | Kiosk/device/thermal output acceptance |
| [Kiosk GUI CI 39135186022](https://github.com/pratikto/PhotoBooth/actions/runs/39135186022) | `f2f52e33` · GitHub Actions Ubuntu, synthetic desktop/Xvfb | **FAIL:** `unittest discover` step; overall workflow not green | Does **not** overturn the owner's local-paper report, but blocks claiming full regression PASS |
| **Operator Windows printer retest** | Owner's booth; **exact local SHA/queue/driver and per-order counts not recorded** | **OWNER TESTED PASS**: pricing correct; BUG-011 printing now explicitly confirmed tested and passed by owner | Every 1/2/3/mixed-template/fault case independently tested, full QA or production release |

Automated tests used mock transports and no live payment provider, customer data or real paper. The **15-test CI pass** is reproducible source evidence; the **operator statement** is the only new physical-quantity evidence, and they must remain independently labeled.

## 5. Safety properties, residual risks, and compatibility

- **One print job is not one sheet:** the N copies are separate ESC/POS image+cut sequences inside one submitted RAW document. Driver/firmware/buffer/cutter capabilities may differ across printers and transports.
- **Do not auto-retry a failed or partial RAW batch:** some prints may already have come out. A single manual `CETAK ULANG` sends one additional explicit sheet only after checking physical paper. This is not FEAT-016 paid reprinting.
- `PrintResult.success` means transport accepted the data; it is **not a physical paper counter**. Kivy stops holding the result-page action once transport submission finishes, not necessarily when the last paper clears the cutter; operators should wait for physical completion.
- Persisted pricing records document **DEMO**, not verified paid transactions. Real QRIS (FEAT-020), paid print recovery/idempotency (FEAT-007) and promo/settlement remain deferred. Do not use DEMO confirmation as money movement.
- This fix did not intentionally alter Floyd parameters, ad playback, music, Drive photo-retention cleanup or `Code.gs`. **BUG-001/007 audio remain deferred, BUG-008 Settings monitoring, BUG-009 30-day Drive deletion unverified and deferred with FEAT-004**.
- **HISTORICAL / SUPERSEDED:** the GUI Actions workflow failed at historical `f2f52e33`. The later QA-only repair resolved its test assertions; the **full suite PASSED at `c40f33f5`** ([Actions](https://github.com/pratikto/PhotoBooth/actions/runs/39145145762)). Historical failure is preserved as a dated observation only.

## 6. Outstanding signoff and future regression matrix

The **core symptom is explicitly owner-tested and reported resolved**, so BUG-011 exits the *active repair queue* but should remain **MONITORING / not formally CLOSED** until repeatable evidence is captured, preferably before selling a kiosk or merging a release.

- [ ] Record the **exact local Windows checkout SHA**, printer model, saved queue name and connection route; no serial numbers or credentials in public GitHub.
- [ ] Capture **requested vs actual cut sheets** for 1, 2, 3 copies, with one template, before considering that full test matrix VERIFIED. Existing overall owner's confirmation does not fill these three individual boxes.
- [ ] Capture mixed templates (A×2, B×1): two capture sessions, three sheets, correct frame/Drive folder QR and Rp25,000 DEMO amount.
- [ ] Test interrupted spooler/network send and paper-out; no accidental automatic duplicate or silently skipped paper, manual reprint requires operator decision.
- [ ] Review full Kiosk GUI CI failures independently and run camera/retake, Floyd print quality, ad video, QR-slip, Windows UI/Settings and Drive folder regression; audio BUG-001/007 remains intentionally deferred.
- [ ] **Separate owner approval** required before formal `CLOSED`, production `VERIFIED/RELEASED`, any merge to `main` or new code changes.

**Rollback reference:** The pre-FEAT-001 source baseline is [`5842a09f`](https://github.com/pratikto/PhotoBooth/commit/5842a09f6a4c6c771ef7f5f0d1a330d0b1040b42). Do **not** hard-reset an operator's working branch or discard subsequent commits. If a regression occurs, plan a **narrow revert** of the relevant printer changes on a controlled review branch/commit with explicit approval, and keep the printer profile/settings backup. The old Floyd image-processing path can separately be selected through `PHOTOBOOTH_PHOTO_TUNING=legacy`; **that switch is not a rollback of print-copy dispatch or Windows spooler finalization**.

## 7. Status discipline

- **BUG-011:** `OWNER TESTED PASS — MONITORING` (fixed-in-source, explicitly tested on the user's Windows printer per the user's confirmation; exact per-case field-test matrix, local SHA and driver/config remain undocumented). Do **not** relabel `CLOSED`/`RELEASED` or treat every stress/failure test as passed.
- **FEAT-001:** `IMPLEMENTED / OWNER TESTED CORE DEMO PRICING AND PRINT-COPY BEHAVIOR`; full *synthetic GUI regression now PASS*, while wider physical negative-case matrix and explicit production release remain pending.
- **GitHub changes for this status reconciliation:** documentation only. No code, `Code.gs`, payment gateway, credentials, runtime deployment or physical test is carried out when recording this acceptance.

Related current records: [bug tracker](../bug_tracker.md), [feature status](../FEATURE_STATUS.md), [checklist](../test_checklist.md), [backlog](../next_step.md), [decisions](../DECISIONS.md), [handover](../DEVELOPMENT_HANDOVER.md), [changelog](../CHANGELOG.md).
