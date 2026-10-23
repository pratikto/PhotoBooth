# FEAT-022 P4 — staged DEMO game and checkout integration

Owner authorization, 2026-10-23 Asia/Jakarta: **“p3 kan udah diuji.. lanjut p4 aja lah”**.
Baseline: `2d0469aff696c23f000bf225c3d66a3aa2d006a5` on
`feature/portrait-kiosk-v2-next`. P3 owner acceptance remains valid; missing
metadata does not block P4 and no additional P3 acceptance tool is shipped.

## Approved sequence and boundaries

1. P4a: reuse the existing pure Meong Fly engine from read-only reference
   `feature/meong-flappy-challenge` / `672e3f7089bb40940e5b41644ceb656aa63aafbb`.
   New v2 pages use the established branding, portrait viewport and input/audio
   lifecycle. No standalone App, camera scanner or branch history is merged.
2. Persist one use of each manual DEMO token before play; no replay after
   win/loss, early exit or restart. Preserve the consumed token when returning
   to advertising. Win/loss continue through tutorial-once to the same gallery.
3. P4b: isolated MOCK quote/checkout guards only; production payment, actual
   discounts and scanner remain off. Real merchant eligibility, Sandbox
   credentials/provider acceptance and commercial promo policy are external
   gates, never inferred from an offline mock or GUI score.
4. Each stage: tests, scoped commit, normal push to the required branch and
   remote HEAD verification. Review actual screenshots at 800×1280/452×900.

All new DEMO state lives under `data/kiosk-v2-p4`; never use v1 customer,
receipt, paid/uncertain print or production order journals. No master change,
new branch, merge, deployment or real transaction. Before P4 rollback:
`2d0469a`. Existing P3 source checkpoint `ef0fcb0` remains unchanged.

## Stage status

Stage 1 backend/engine: **56 targeted tests PASS**, zero failures/errors.
[Transcript](stage1-core-tests.txt). Engine matches the read-only reference
byte-for-byte: [provenance](engine-reference.json). New SQLite DEMO ledger
atomically claims before play, rejects concurrent/restarted reuse and preserves
terminal results. Bounded background jobs cannot queue repeated start taps or
call a retired GUI. Existing GUI/audio/photo source is unchanged at this stage;
new pages and physical Windows acceptance are not yet claimed. Screenshot
review and a P4-specific checkbox form follow when the new pages are connected.
