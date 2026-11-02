# PP-07 automated simulation evidence — 2 November 2026

## Latest matching-source automated verification — 67dc3eb5

**Tested code:** [`67dc3eb502dbb1bb65b0a7139f728a4d05e5b664`](https://github.com/pratikto/PhotoBooth/commit/67dc3eb502dbb1bb65b0a7139f728a4d05e5b664)  
**Exact workflow:** [GitHub Actions 41393795509](https://github.com/pratikto/PhotoBooth/actions/runs/41393795509) — **all three jobs SUCCESS**.

| Actual job | Tests executed | Failures | Errors | Skips | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| Windows private-state, Python 3.12 | **493** | 0 | 0 | 0 | **PASS** |
| Ubuntu private-state, Python 3.12 | **493** | 0 | 0 | 0 | **PASS** |
| Ubuntu native Kivy/Xvfb desktop | **51** | 0 | 0 | 0 | **PASS** |
| **Total test executions** | **1,037** | **0** | **0** | **0** | **3/3 jobs PASS** |

**Do not call these 1,037 distinct functional scenarios:** 493 backend cases execute separately on Windows and Linux, and the 51 headless native cases run on Ubuntu. The canonical 112-case PP acceptance matrix and 26-case real owner Windows UAT still have separate NOT_RUN/BLOCKED status.

**Additional source fixes now tested on the matching SHA:**
- Three new preflight cases PASS on both OS, verifying a genuinely READY mocked environment, BLOCKED when FastAPI is missing, and BLOCKED when a legacy QRIS profile remains enabled. Actual preflight now checks all required Kivy/QR/backend/graphics dependencies and avoids echoing secrets.
- The native two-template paid-flow test asserts that the screen contains the explicit warning `QR DEMO • BUKAN LINK DOWNLOAD`. The opt-in real test Drive route is separately labeled `DRIVE TEST • BAYAR SIMULASI`; actual cloud access was NOT used or certified.
- Earlier five source/root startup tests continue PASS on Windows and Linux. The native payment/receipt/Drive/2+1 virtual print cycle remains one synthetic original purchase, one recovery receipt and service still `OWED` without physical-paper verification.
- GitHub CI also executes Apps Script offline syntax/retention checks and historical paid-first regression selections. No merchant Sandbox charge, real POS80, live Drive upload, customer photos or refund happened.

**Physical acceptance remains pending:** real Windows GUI with camera/touch, 30-second genuinely human-visible ticket, paper emergence and cuts, publicly accessible Drive photos/retention, actual Midtrans merchant Sandbox and original customer return under physical conditions. Software CI does not close AR-13 or authorize production.

---

**Branch:** `feature/post-preview-qris-checkout`  
**Source commit tested:** [`b071a5cc0c449f0f3bf868659f0fb0b51a56bd97`](https://github.com/pratikto/PhotoBooth/commit/b071a5cc0c449f0f3bf868659f0fb0b51a56bd97)  
**Workflow:** [GitHub Actions run 41392821079](https://github.com/pratikto/PhotoBooth/actions/runs/41392821079)  
**Evidence type:** automated **synthetic-only** Linux/Windows Python regression and Xvfb native-Kivy simulation. No genuine charge, receipt paper, camera, Drive upload or customer identity is used.

## Why this run exists

Earlier source-only micro-commits introduced `test_post_preview_pilot_preflight.py` and `test_post_preview_pilot_early_root.py`, but the explicit test-module allowlist in `.github/workflows/post-preview-qris.yml` did **not** execute them. A previously successful CI run therefore could not be cited as proof those five checks passed.

Code commit `2d3a40f048d9969998e2478d9ed3d08d6b90facb` added both modules to the Windows + Ubuntu jobs. Commit `b071a5cc` added a native integration test of an original two-template order. Only the latter containing-source run is accepted as evidence below.

## Observed results for exact source

| Job | Actual tests | FAIL | ERROR | SKIP | Status |
| --- | ---: | ---: | ---: | ---: | --- |
| Ubuntu private-state (Python 3.12) | 490 | 0 | 0 | 0 | **PASS** — CI job completed successfully |
| Ubuntu private-desktop Xvfb/Kivy | 51 | 0 | 0 | 0 | **PASS** — CI job completed successfully |
| Windows private-state (Python 3.12) | 490 | 0 | 0 | 0 | **PASS** — CI job completed successfully |

The counts are read from the exact GitHub Actions `KIOSK_UNITTEST_SUMMARY` lines, not calculated from the number of files or the workflow badge.

## New checks executed

**Preflight and data-root regression (five tests PASS on Ubuntu AND Windows):**

1. Missing required checkout files must BLOCK.
2. Wrong current Git branch must BLOCK even if files are otherwise present.
3. A previously occupied private customer root must be rejected before app/device import without changing its original file.
4. A regular file cannot be used as a directory; original bytes remain untouched.
5. A symbolic-link ancestor cannot redirect the test root, and the target data is left untouched. On this Windows runner, the symbolic-link case executed and PASSed with **zero skips**; not all Windows installations have the same symlink permissions.

**Original two-template native synthetic flow (one new GUI test, PASS on Ubuntu):**

- Native portrait Kivy test visits the original preview → CCP → single mock payment → provider-verified synthetic PAID → mandatory original Recovery Ticket → synthetic verified Drive folder → two separate paid print commands.
- Two selected designs are `template_a` (two copies) and `template_b` (one copy); capture session selection creates the original six photos rather than multiplying shots by paper count.
- The test asserts **exactly one synthetic payment charge**, **one recovery receipt job**, **two purchased print submissions with copy counts [2, 1]**, and both design outcomes `SUBMITTED`.
- It also confirms the original paid service remains `OWED` and `physical_paper_verified=False`. This is intentional: printer transport acknowledgment does not establish physical delivery.
- No duplicate paid-print action remains enabled after all original PREPARED jobs have been submitted.

The existing native suite additionally exercises smaller/larger portrait layouts, payment/claim/ticket screens, original proof-gated return, A/B privacy fencing, late callbacks, held workers and unpaid/paid lifecycle guards. This does not amount to human GUI signoff.

## What this does **not** verify

- No actual POS80 bitmap/ESC-POS transport, printer paper/cutter/USB/LAN hardware or physical output.
- No actual Midtrans Sandbox merchant QRIS/payment webhook or production money movement.
- No real Apps Script/Google Drive public folder, folder ACL, upload or retention deletion.
- No live webcam capture/touchscreen, genuine 30-second human-visible timing, actual customer proof scanning, network unplug or reboot on the owner's laptop.
- No real refund API capability, automatic refund request or finance/legal approval.
- No evidence that all **PP-001–112** are individually executed or accepted: the complete canonical matrix remains **NOT_RUN** as end-to-end owner acceptance cases.
- Owner `PP07-SUPERVISED-WINDOWS-UAT.md` 26 scenarios remain **NOT_RUN/BLOCKED** until independently observed and reported.

## Additional source increments after the verified 1,031 executions

**Do not combine these newer commits with the successful b071 counts.** Follow-on changes added the missing checkout runtime dependency checks (FastAPI/httpx/Pydantic/qrcode/cv2/ffpyplayer), fail-closed legacy checkout profile detection, three new preflight regression cases, and a visibly labeled **QR DEMO / BUKAN LINK DOWNLOAD** versus actual opt-in Drive-test header in the native mock GUI. The launcher explicitly supplies the display mode. Source SHA `67dc3eb502dbb1bb65b0a7139f728a4d05e5b664` was verified in [CI 41393795509](https://github.com/pratikto/PhotoBooth/actions/runs/41393795509): **3/3 jobs SUCCESS, 493 Windows + 493 Ubuntu + 51 native PASS**.

The earlier verified b071 run totals **1,031 executed successful test instances** (490 Windows + 490 Ubuntu + 51 native). Windows/Linux reuse many identical test cases; 1,031 does **not** mean 1,031 distinct scenarios or 112 owner PP acceptance cases.

## Release / continuation gate

Matching-source Windows/Linux/native execution is now verified as **3/3 SUCCESS** at `67dc3eb5`. If future source changes, rerun exact-source CI and update this record before carrying PASS forward. The physical-owner pilot remains strictly `--synthetic-payment-only` with a fresh private root, printer/Drive disabled by default and separate dual-consent opt-ins. Preserve all original AR/UAH, paid obligations and old customer data.

**Related:** [Supervised Windows instructions](POST-PREVIEW-QRIS-WINDOWS-PILOT.md) · [26-case owner worksheet](PP07-SUPERVISED-WINDOWS-UAT.md) · [current implementation checkpoint](POST-PREVIEW-QRIS-IMPLEMENTATION-CHECKPOINT.md).
