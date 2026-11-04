# Complete simulation campaign — 5 November 2026

**Owner request:** simulate the complete journey and failures, repair reproduced
problems, then finish software simulations before asking the owner to test.
**IN PROGRESS** — this is an incremental safety checkpoint, not a completed
campaign or physical acceptance. Dates use Asia/Jakarta.

Authorized existing branch: `feature/post-preview-qris-checkout`.
Starting/current tested source: `9ae4ec1874c43c56325bf4254679e7feaca2ba77`.
Original attached local `work` branch/index remains untouched. Exact-source
snapshot and external Git index retain the already verified delivery procedure.

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
