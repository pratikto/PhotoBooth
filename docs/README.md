# Meong Photobooth - Documentation index

## Current feature-branch work, 2026-10-20

**FEAT-020 automatic QRIS is now connected to the main Kivy GUI for an explicit mock trial on feature/qris-payment.** It is not production-enabled and is not merged into master. The default master/v1.0.0 release baseline remains separate. Dated pre-QRIS records describe their original baseline, not the current feature implementation.

Start with **[QRIS_TRIAL.md](QRIS_TRIAL.md)** to run the main GUI without merchant credentials; physical printing is disabled by default. [Current QRIS architecture/status](FEAT-020-QRIS.md) explains the Sandbox boundary, recovery behavior and remaining gates.

| Need | Canonical record |
| --- | --- |
| Current implementation vs hardware evidence | [FEATURE_STATUS.md](FEATURE_STATUS.md) |
| Owner-confirmed approval and boundaries | [DECISIONS.md](DECISIONS.md) |
| Active feature ordering and prerequisites | [next_step.md](next_step.md) |
| Operational defects and severity | [bug_tracker.md](bug_tracker.md) |
| Reproducible test results and remaining acceptance | [test_checklist.md](test_checklist.md) |
| Next safe engineering/operator action | [DEVELOPMENT_HANDOVER.md](DEVELOPMENT_HANDOVER.md) |
| Actual commits and changes | [CHANGELOG.md](CHANGELOG.md) |
| Architecture | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Binding development governance | [DEVELOPMENT_PROTOCOL.md](DEVELOPMENT_PROTOCOL.md) |
| Reusable continuation prompt | [DEVELOPMENT_PROMPT.md](DEVELOPMENT_PROMPT.md) |

**Latest verified source:** 7cf90ea95a32b4cf2feee16c21232069bc1aa9bb. Backend **124 PASS / 0 SKIP**; full GUI **364 PASS / 2 optional native-model SKIP**, **87 existing + 6 QRIS renders**, two exact screenshot QR decodes. [Exact-SHA acceptance and artifact IDs](qa/FEAT-020-acceptance-20261020.md). These are synthetic/loopback checks, not real merchant or Windows hardware certification.

Earlier chronological records are preserved verbatim beside the current files as `*.pre-qris-20261020.md`; their existing relative links remain in the same docs directory. Current pages link to their own history. Historical isolated PASS claims without execution evidence are not current acceptance. The bug tracker is unchanged; BUG-001/007 audio and BUG-009 retention remain open, and monitored device successes are not upgraded to release certification.

## Supporting references

[Advertising and DEMO QR-slip setup](advertising-and-qris.md), [photo retention](photo-retention.md), [dither tuning lab](dither-tuning-lab.md), [FEAT-001/BUG-011 owner evidence](qa/FEAT-001-BUG-011-acceptance.md), [historical Kiosk QA](qa/KIOSK-GUI-REGRESSION-2026-10-18.md), [QA index](qa/README.md), [legacy NEXT_STEPS pointer](NEXT_STEPS.md), [immutable v1.0.0 source release](releases/v1.0.0.md).

No further feature, merge, production payment, cloud deletion or public deployment is authorized by this index. Other branches and their separate approvals remain untouched.
