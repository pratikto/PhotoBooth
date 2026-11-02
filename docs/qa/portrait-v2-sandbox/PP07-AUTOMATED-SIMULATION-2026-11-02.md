# PP-07 automated simulation evidence — 2 November 2026

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
| Windows private-state (Python 3.12) | — | — | — | — | **PENDING** — do not infer PASS before log verification |

The counts are read from the exact GitHub Actions `KIOSK_UNITTEST_SUMMARY` lines, not calculated from the number of files or the workflow badge.

## New checks executed

**Preflight and data-root regression (5 tests on Ubuntu, Windows separately pending):**

1. Missing required checkout files must BLOCK.
2. Wrong current Git branch must BLOCK even if files are otherwise present.
3. A previously occupied private customer root must be rejected before app/device import without changing its original file.
4. A regular file cannot be used as a directory; original bytes remain untouched.
5. A symbolic-link ancestor cannot redirect the test root, and the target data is left untouched. On Windows, this case may SKIP if the runner cannot create symlinks; record the outcome accurately.

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

## Release / continuation gate

Complete the Windows result and update this record with exact `run/tests/failures/errors/skipped`. If any job fails, fix the underlying issue and re-run exact-source CI before claiming an automated PASS. The physical-owner pilot remains strictly `--synthetic-payment-only` with a fresh private root, printer/Drive disabled by default and separate dual-consent opt-ins. Preserve all original AR/UAH, paid obligations and old customer data.

**Related:** [Supervised Windows instructions](POST-PREVIEW-QRIS-WINDOWS-PILOT.md) · [26-case owner worksheet](PP07-SUPERVISED-WINDOWS-UAT.md) · [current implementation checkpoint](POST-PREVIEW-QRIS-IMPLEMENTATION-CHECKPOINT.md).
