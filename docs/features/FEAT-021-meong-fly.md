# FEAT-021 — Meong Fly isolated prototype

Status: IN PROGRESS — prototype source only; NOT GUI/hardware verified.
Approved 2026-10-20: isolated prototype in feature/meong-flappy-challenge; no master merge.
Priority: P2 product enhancement, after core operational bugs; commercial integration BLOCKED.

## Scope
A standalone Kivy mini game inspired by tap-to-fly arcade mechanics, with a gray cat, rainbow trail, pipes, score, loss and win states. Entry point: `python -m photobooth.meong_fly_demo`. No receipt scan, welcome-screen integration, discount, merchant ledger, or Midtrans payment in this prototype.

## Proposed future business rules (NOT IMPLEMENTED)
Model A: scan valid cafe receipt first, then one game attempt. A win may grant IDR 2,500 off the photobooth total. Subsidy is shared between Meong and cafe; 50:50 is a proposal, not a confirmed split. Only successful paid redemption is eligible for cafe settlement. Receipt validation must use verifiable unique tokens and atomic redemption; never trust GUI score alone.

## Acceptance and test plan
- Offline engine: start, flap, collision, one-time pipe scoring, win, reset.
- On Windows with Kivy: verify 25-second play, tap input, layout scaling, and restart.
- Future phases require GUI regression and device testing, receipt replay tests, transaction/idempotency tests and explicit separate authorization.
- No hardware, POS, or payment acceptance asserted.

## Changes
- `photobooth/meong_fly.py`: isolated simulation engine.
- `photobooth/meong_fly_demo.py`: standalone Kivy visualization.
- `tests/test_meong_fly.py`: offline unit tests.

## Evidence and limitations
Commits: `5499ae1c`, `ba3748df`, `9c43aa9e`.
Tests have NOT been verified passing. Attempted remote Git clone for local test execution failed; follow up with GitHub CI or a checked-out local workspace. No merge to master.

## 2026-10-21 — Space Edition and single-use demo flow
Owner approved implementing the space-themed game and one play per receipt on the isolated feature branch. The game now shows a dark space background, stars, asteroid-field obstacles, pixel camera-cat with blue lens and rainbow exhaust. This is a programmatic approximation of the reference logo, NOT yet the exact approved artwork asset.

The standalone Kivy demo accepts local `DEMO-...` identifiers. `DemoReceiptLedger` stores each consumed identifier in SQLite in the user's home directory; consumption occurs before game start, survives restart, and no retry button is presented. A result is informational only: the prototype DOES NOT create a redeemable voucher, verify a real cafe POS receipt, change QRIS pricing, or integrate with the production welcome screen.

Run: `python -m photobooth.meong_fly_demo`.
Targeted tests: `python -m unittest tests.test_meong_fly tests.test_meong_fly_receipts -v`.
Tests and physical GUI verification have NOT yet been executed/confirmed for these commits. Further work must validate the demo engine, actual artwork, kiosk screen scaling and collision fairness. Do not merge to master without owner approval.
