# Complete simulation campaign — 5 November 2026

**Owner request:** simulate the complete journey and failures, repair reproduced
problems, then finish software simulations before asking the owner to test.
**IN PROGRESS** — this is an incremental safety checkpoint, not a completed
campaign or physical acceptance. Dates use Asia/Jakarta.

Authorized existing branch: `feature/post-preview-qris-checkout`.
Starting/current tested source: `9ae4ec1874c43c56325bf4254679e7feaca2ba77`.
Original attached local `work` branch/index remains untouched. Exact-source
snapshot and external Git index retain the already verified delivery procedure.

## Phase 2 — BUG-041 reproduced and repaired; campaign still IN PROGRESS

**Phase 1 push verified:** `273cd802c7b930515a34a41c029111a3080e9184`.
A new actual Meong Fly DEMO win -> photo gallery probe fails at both 800x1280
and 452x900: two designs/2+1 copies advertise **Rp22,500**, while the existing
post-preview final preview/provider quote requires **Rp25,000**. The payment
backend does not accept that DEMO discount; this is a reproduced customer-price
consistency bug, not evidence of an unauthorized real charge.

The original portrait gallery reused DEMO discount eligibility in the isolated
post-preview subclass, although that profile has no trusted promotion adapter.
A small policy seam retains the original DEMO/MOCK behavior in `kiosk_v2/app.py`;
`post_preview_app.py` rejects DEMO-only gallery eligibility, matching its existing
server quote. No pricing formula, real discount authority, game attempt,
payment guard, merchant flag or legacy checkout changes.

**N27 new connected regression:** at both portrait sizes, run the actual durable
DEMO game worker/recorded win and tutorial, select two designs/2+1 copies, take
six initial shots plus one selected-slot retake per design, reject another
retake, confirm final preview and original CCP, settle one synthetic Rp25,000
order, display original ticket and dispatch one receipt, then submit two virtual
strip batches with exact 2+1 copies. Gallery, preview and provider amount must
agree; the game code remains consumed and service remains OWED because virtual
submission is not physical paper. Original DEMO/MOCK discount regression remains.

**Focused execution:** N27 plus game-offer and existing game-followup modules
**17 PASS, 0 failures/errors/skips, 9.709s**. The initial price-only probe was
**1 method / 2 failed portrait subcases** before the fix. A new full journey
closes the previously absent game-to-post-preview quote seam, rather than
replacing an existing working test with a weaker assertion.

The broad all-opt-in baseline is still running on the untouched prior source in
an independent snapshot. Its result does not verify this fix. After inspecting
it, execute the complete all-opt-in suite on this repaired source, then inspect
matching Windows/Ubuntu/native CI. Keep this campaign IN PROGRESS until those
results and all remaining simulation classifications are recorded.

```text
python tools/run_kiosk_unittests.py test_post_preview_native_journeys.NativeCustomerJourneyMatrixTests.test_n27_demo_win_retakes_and_paid_delivery_keep_one_consistent_quote test_kiosk_v2_game_offer test_kiosk_v2_game_followup
```

Partial acceptance references: PP-002/004/010/020/033/041/048/068. No full
hardware/provider acceptance row is promoted to PASS.

## Phase 1 — complete synthetic journeys and interruption cases

Executed on Linux/Python 3.12.14 with real Kivy/SQLite/test HTTP and synthetic
camera, merchant, printer and Drive. SDL offscreen/software GL and dummy audio;
no actual charge, refund, paper, public upload or customer photographs.

```text
python tools/run_kiosk_unittests.py test_post_preview_journey_matrix test_post_preview_native_journeys test_post_preview_process_crash test_post_preview_payment_crashes test_post_preview_refund_assessment
```

**51 PASS, zero failures/errors/skips, 49.747s.** This includes existing imported
admission fixture tests; it is not 51 new acceptance scenarios.

| Executed group | Methods | Covered software behavior |
| --- | ---: | --- |
| J01–J21 | 21 | All 12 templates/36 captures before payment; 2+1+3 copies; final preview; original CCP/PAID/ticket; exact fake Drive folder; virtual strip dispatch; delayed/duplicate payment; corrupt media; uncertain paper; A/B return; 12 consecutive paid visits |
| N21–N26 | 6 | Actual Kivy navigation/buttons, three-design paid journey, offline Drive recovery, protected A/B admission and checkout, all 12 previews at two portrait sizes |
| P01–P02 | 2 | Real child exit during receipt/strip SENDING; independent SQLite reopen retains OWED and no guessed paper outcome |
| Payment process-death cases | 6 | PREPARED/SENT/create-response loss, interrupted PAID GET, lost cancel result and leased inbox worker recovery |
| Refund assessment | 10 | Nonbinding eligibility only; no proof-loss-only refund, no uncertainty-based payout, correct excess-attempt identity, mandatory capability/policy fences |
| Imported admission fixtures | 6 | Safe handoff/claim, pending and worker holds, exact ACK retry, wrong QR role denial |

No failure was reproduced in this phase. Existing source fixes are retained;
there is no speculative product patch or hardware readiness upgrade.

## Remaining phases — not yet claimed complete

1. Full Python discovery with GUI/audio/video opt-ins; use only dummy/synthetic
   acquisition. Record every skip and resolve executable optional dependencies.
2. Actual MediaPipe model with the repository's pinned public sample fixtures;
   independently check model bytes/hash and keep samples outside Git.
3. Fill meaningful missing journey/failure coverage discovered by this campaign,
   repair reproduced defects, and push each tested increment immediately.
4. Review all 112 canonical PP scenarios against executed software evidence;
   distinguish automated partial coverage, absent implementation and externally
   blocked hardware/provider/security acceptance. Never turn a related unit test
   into full acceptance PASS.
5. Source-matched final regression, safe synthetic preview inspection and final
   simulation report. Owner physical UAT remains deferred until this software
   campaign finishes or identifies a precise external blocker.

The next broad command uses `tools/run_kiosk_unittests.py` with no module list,
`PHOTOBOOTH_TEST_GUI=1`, `PHOTOBOOTH_TEST_AUDIO=1`,
`PHOTOBOOTH_TEST_VIDEO=1`, SDL offscreen/dummy audio, and camera/face/palm/real
delivery disabled except for explicitly isolated fixture overrides. Native
model tests require a verified local public asset directory and the pinned
optional MediaPipe dependency before those cases are considered executed.

**Readiness remains separate:** synthetic candidate previously ready; merchant
Sandbox launch/credentials/webhook and full protected original-worker restart
remain incomplete/blocked; refunds disabled; owner hardware NOT_RUN; production
NOT_APPROVED. The [previous verified source checkpoint](PP07-CONTINUATION-2026-11-05.md)
retains Windows 544/Ubuntu 544/native 61 CI evidence at c20479d. This new campaign
must supply its own exact-source evidence and must not erase earlier failures
or assign new physical PASS results.
