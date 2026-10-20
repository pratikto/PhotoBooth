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
