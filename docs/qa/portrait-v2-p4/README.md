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


## Stage 2 — P4a native game pages

**377/377 full tests PASS**, zero failures/errors/skips, including real Kivy,
muted native audio/video and public native palm fixtures. [Transcript](stage2-full-tests.txt).
Six game widget scenarios cover win/loss, tutorial seen/unseen, restart/used code,
abandonment, stale/failed I/O, minimize and resize. The store still consumes the
code before play; there is no MAIN LAGI or live receipt scanner. No client game
score changes the existing gallery quote. BGM stays off inside the game;
existing button audio is the sole feedback owner.

Actual Kivy screenshots: **22 captures**, eleven pages at each required size.
Reviewed [800×1280 contact](game-contact-800x1280.jpg) and
[452×900 contact](game-contact-452x900.jpg), plus game/result originals.
[800 manifest](game-render-800x1280.json), [452 manifest](game-render-452x900.json)
record file hashes and the precommit base SHA with tracked changes explicitly
true. Ready/paused/win/loss states are injected for visual coverage; this does
not certify human gameplay, Windows touch/speakers or a physical scanner.
Asteroids are five static reference-rendered textures, never Pillow per frame.

Rollback for this GUI stage: `d30d921` (engine/store only). P4a is ready for
Windows device acceptance; P4b MOCK and its checklist follow in the next stage.


## Stage 3 — P4b local MOCK checkout

**406/406 final full tests PASS**, zero failures/errors/skips, with native
GUI/audio/video and public palm fixtures. [Final transcript](stage3-final-full-tests.txt).
Includes fifteen pure SQLite checkout tests and twelve native checkout widget
scenarios: real-catalog regular/win/loss quotes, frozen cart/restart recovery,
pending/unknown/cancel/expiry, concurrent retries and admissions, consumed-grant
status, actual decode of nonpayable QR text, failed/suspended I/O, bounds at
800×1280/452×900/360×640, twenty simulated checkout visits and the full existing
three-photo/review/local-result handoff. Native dummy audio is not speaker proof.

`mock_checkout.py` owns the simulated authority in the **same isolated P4 DB**.
It reads the stored DEMO result and existing catalogue tariff; the UI supplies
neither amount nor discount. One design/one copy is Rp10.000; a locally recorded
DEMO win proposes a MOCK-only Rp2.500 reduction, giving Rp7.500. One win can be
reserved by only one live/admitted order. Cancellation/expiry releases an
unused simulated reservation, never the already consumed game token. This is
not a trusted merchant promotion or a signed game result.

The stable request key returns the same order; changed payload is rejected.
Creation/admission use SQLite IMMEDIATE transactions. An outstanding order is
recovered with its frozen cart rather than replaced on restart/new selection.
PENDING expires after 180 seconds; UNKNOWN survives timeout/restart and cannot
cancel/admit until an explicit MOCK resolution. CONFIRMED is not auto-capture.
One durable admission leads only to the existing explicit P3 consent. A lost
admission response is **never replayed**: status ADMITTED offers safe return,
not another handoff. There is no production PAID state or financial journal.

All DB/QR encoding runs on the bounded worker, main-thread callbacks check page
revision, and QR pixels are cached. BGM continues once from tutorial/gallery
through MOCK checkout; game BGM remains off and active buttons use the same
single SFX owner. Camera/photo/retake/print/Drive/v1 implementations are unchanged.
[Eight legacy source comparisons](legacy-source-comparison.json).

### Reviewed GUI and browser proof

Twenty final actual Kivy checkout captures (ten states × two required sizes):
[800×1280 contact](checkout-contact-800x1280.jpg),
[452×900 contact](checkout-contact-452x900.jpg),
[800 manifest](checkout-render-800x1280.json),
[452 manifest](checkout-render-452x900.json). The initial compact pending layout
had overflow; final layout uses a flexible QR area and shared status/tool row.
All displayed amounts/quantity labels and controls fit. Game result/recovery
states are deliberately synthetic; no human game win or provider is claimed.
Manifests truthfully record the precommit SHA and tracked changes; CI supplies
clean-source artifacts after push.

[28-item Windows form with Submit](windows-checklist.html) starts empty with a
separate storage key. Chromium/Playwright at both sizes verifies reload, no
horizontal overflow, manual unchecked items, Submit/download/reset, no imported
P3 results and minimum-twenty-cycle gating. [Browser report](form-verification.json).
Submit prepares text to copy into chat; it cannot send a conversation message.
P3 owner acceptance remains valid and is not revoked by this new P4 form.

P4a matching-source CI at `cd785e1`:
[39970759606](https://github.com/pratikto/PhotoBooth/actions/runs/39970759606),
all three jobs SUCCESS; [verification](p4a-ci-verification.json).

### Run on Windows

Use the existing Windows venv and the required branch (no new branch):

```powershell
git switch feature/portrait-kiosk-v2-next
git pull --ff-only origin feature/portrait-kiosk-v2-next
.\.venv-kivy\Scripts\Activate.ps1
git rev-parse --short HEAD
python tools/run_portrait_v2.py
```

MAIN MEONG FLY → COBA GAME · KODE DEMO → new code, e.g. DEMO-P4-001.
Use a different code for each new attempt; invalid/previously used codes do not
start a game. Both outcomes continue through the normal tutorial/gallery.

For the local checkout test, close the app first:

```powershell
$env:PHOTOBOOTH_V2_CHECKOUT_MOCK = "1"
python tools/run_portrait_v2.py
```

Choose copies → **UJI CHECKOUT MOCK • TANPA PEMBAYARAN**. QR contains only
`MEONG MOCK ONLY - NOT QRIS - <id>`; never pay it. Simulate confirmation,
uncertainty/rejection or cancellation using the explicitly labelled controls.
Pending recovery appears on reopening checkout, never automatically at startup.
Print/Drive remain their existing operator opt-ins; P4 never auto-sends either.
After closing, return to the default with:

```powershell
Remove-Item Env:PHOTOBOOTH_V2_CHECKOUT_MOCK -ErrorAction SilentlyContinue
Start-Process .\docs\qa\portrait-v2-p4\windows-checklist.html
```

Keep the MOCK flag set while testing section C; removal disables its entry on
the next launch. The launcher prints HEAD and diagnostic log path; preserve it
if Windows gameplay, touch or audio fails. No new dependency beyond P3 is needed.

### Checkpoints and remaining gates

- `2d0469a`: pre-P4 accepted P3 documentation/source baseline.
- `d30d921`: engine + durable DEMO ledger only (56 targeted PASS).
- `cd785e1`: native P4a game pages (377 full PASS; matching-source three-job CI).
- This stage: opt-in P4b MOCK and Windows checklist; source SHA recorded by git
  and subsequent CI evidence. Disable the MOCK environment flag as the immediate
  reversible fallback; code rollback checkpoint is `cd785e1`.
- Preserve `data/kiosk-v2-p4/demo-attempts.sqlite3` during rollback. **Do not delete
  consumed codes/orders to manufacture another attempt or replay admission.**

**OPEN — not a completed full P4 release:** real receipt scanner/merchant
eligibility, trusted single-use promo issuer, approved commercial campaign,
provider Sandbox adapter/credentials/callback/reconciliation acceptance, Windows
human gameplay/speakers/touch and the new twenty-cycle P4 acceptance. Read-only
QRIS reference HEAD `3cc8a8e360e8c2100a3077b755664eb61d0216ea` already calculates
server quotes/idempotent orders, but has no trusted Meong Fly promo contract.
Its code/history is not merged or connected. Supplying a local game win to a
real provider would skip that gate; no real QRIS configuration is written.

No remaining known failure in the tested local MOCK scenarios. External gates
remain NOT RUN/BLOCKED, not PASS. Stop here before live/Sandbox/merchant work or
P5 certification; owner/provider configuration is needed for that next scope.
