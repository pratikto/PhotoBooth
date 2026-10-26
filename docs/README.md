# Meong Photobooth documentation — GUI v2

Updated **26 October 2026 (Asia/Jakarta)**. Continue on
`feature/portrait-kiosk-v2-next`; the GitHub default remains `master` and
`python main.py` remains the v1 entry point.

## Find the authoritative document

| Subject | Document |
| --- | --- |
| Installation, launchers and test modes | [Repository README](../README.md) |
| Implemented roadmap and customer flow | [GUI v2 specification](portrait-kiosk-v2.md) |
| Per-booth folders and offline global/local assets | [Current storage contract](photobooth-storage-layout.md) — local source integrated; corrected numbered cloud layout still needs installed-account deployment/acceptance |
| Current implementation and acceptance boundaries | [Feature status](FEATURE_STATUS.md) |
| Modules, workers and service contracts | [Technical design](portrait-kiosk-v2-technical-design.md) · [architecture](ARCHITECTURE.md) |
| Current visual decisions and artwork provenance | [Visual specification](portrait-kiosk-v2-visual-spec.md) · [artboards](assets/portrait-v2/README.md) |
| Owner-confirmed product decisions | [Decision log](DECISIONS.md) |
| Defects and monitoring | [Bug register](bug_tracker.md) |
| Outstanding work and proposed features | [Backlog](next_step.md) |
| Resume work | [Handover](DEVELOPMENT_HANDOVER.md) · [continuation prompt](DEVELOPMENT_PROMPT.md) |
| Scope, reuse, checks and staged pushes | [AGENTS.md](../AGENTS.md) · [development protocol](DEVELOPMENT_PROTOCOL.md) |
| Tests, owner reports and manual acceptance | [Test ledger](test_checklist.md) · [QA index](qa/README.md) |
| Change history | [Changelog](CHANGELOG.md) |
| Reference branches and repository transition | [Branch audit](gui-v2-branch-audit.md) · [promotion plan](gui-v2-promotion-plan.md) |
| This documentation cross-check | [Reconciliation report](qa/documentation-consistency-2026-10-25.md) |

## Current acceptance packages

- [FEAT-009 stage 2: recovery and Ubuntu startup](qa/portrait-v2-recovery/README.md):
  Windows development/Ubuntu deployment, docs-first rule, guarded startup and
  single-instance ownership; generated user service requires manual installation.

- [Mirrored v2 output](qa/portrait-v2-mirrored-output/README.md): consistent
  review/result/printed/digital photo areas, unchanged original JPEGs/art/QR,
  all-twelve renderer checks and [five-item Submit form](qa/portrait-v2-mirrored-output/windows-checklist.html).

- [BUG-009 retention](qa/bug-009-retention/README.md): existing v1 activation
  repair, read-only diagnostic, setup/deployment guide and [eight-item Submit
  form](qa/bug-009-retention/windows-checklist.html). Source proof is separate
  from actual owning-account timer/permanent-deletion evidence.

- [Simpler photo entry](qa/portrait-v2-photo-entry/README.md): 26 October removal
  of the separate idle CARA PAKAI button; mandatory tutorial flow and short
  Windows spot checks remain.

- [Automatic print and background Drive](qa/portrait-v2-print-drive/README.md):
  owner-selected v1 reuse, ordinary --print/--drive profile, durable auto batch,
  startup queue resume and verified result QR; [eleven-item Submit form](qa/portrait-v2-print-drive/windows-checklist.html).
  Source/fixture evidence remains separate from paper/phone/cloud acceptance.

- [Operator Device Health](qa/portrait-v2-operator-health/README.md): earlier
  operator source `ea394e8`, original v1 panel/worker reuse, local safe reports;
  [eight-item form](qa/portrait-v2-operator-health/windows-checklist.html).
- [P5 baseline and runbook](qa/portrait-v2-p5/README.md): source `9433010`,
  [26-item Windows form](qa/portrait-v2-p5/windows-checklist.html), metadata import,
  new Sandbox integration checks and recovery. Its 688-test result predates the
  operator increment; [the test ledger](test_checklist.md) distinguishes both.
- [Sandbox](qa/portrait-v2-sandbox/README.md): isolated keys/backend,
  official simulator, full-price consent and durable photo admission.
- [P3 source record](qa/portrait-v2-p3/README.md) and
  [later preview/button acceptance](qa/portrait-v2-preview-redraw/README.md).
- [Original game reuse](qa/portrait-v2-meong-reuse/README.md) and
  [readable typography](qa/portrait-v2-readable-type/README.md): source-specific history.

P5 is ready for acceptance; merchant/device/cloud/privacy evidence and release
signoff remain separate. The preflight at `0dc6555` is not physical acceptance.
Safe authorized source work may continue while laptop checks wait. The operator
form does not require repeating old photo/game twenty-cycle reports.

## Historical and shared references

Dated QA records, the [P2 gate](portrait-v2-p2-6-to-p2-8-qa-gate.md),
[original integration blueprint](FEAT-021-to-FEAT-022-integration-plan.md),
and v1 release describe their original source and authorization. Their former
“not integrated”, “OPEN”, test counts and next actions do not override current
status or later owner reports. Raw evidence is retained without translation or
rewriting its results; active guidance and audit corrections are in English.

[Advertising/QR slips](advertising-and-qris.md), [printer setup](printer-setup.md),
[retention](photo-retention.md) and [dithering lab](dither-tuning-lab.md) identify
which instructions apply to v1/shared services versus v2. Newer reference-branch
features require their own authorized integration; the 19-branch audit is dated.
