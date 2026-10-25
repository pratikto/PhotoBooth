# Documentation consistency audit — 25 October 2026

Repository `pratikto/PhotoBooth`; authorized branch
**`feature/portrait-kiosk-v2-next`**. Initial remote HEAD:
**`5f09eff9998c942ed54feef0cf0563fc3944611b`**.
The owner requests all documentation cross-checked for obsolete/conflicting
claims and corrected in English.

## Scope and source of truth

Reviewed **all 67 pre-existing Markdown documents and 14 HTML checklists** on
this branch, including root/asset guides, current engineering/governance, dated
QA, release notes and branch references. The new report makes 68 Markdown files.
[Complete per-file inventory and validation](documentation-consistency-2026-10-25.json)
records roles and before/after hashes.

Current facts were cross-checked against ordinary/Sandbox launchers, v2
flow/photo/Drive/game/payment/health adapters, original services, provenance,
recorded raw outputs, CI metadata and owner-report records. GitHub default is
`master`, head `27f3801b235d81dc0a49ab201f3e143b62314413` at this check.
Latest functional source remains `ea394e8`; its CI 40157638369 is SUCCESS at
that exact SHA. This task does not create a new application-test result.

The 19-branch audit remains an explicitly dated inventory; current applicability
was reconciled, without claiming a fresh scan/test or editing other branch tips.
Current guidance/corrections and the two active forms are in English. Exact
application labels, original owner quotes, raw logs/JSON and historical forms
retain their original wording/language as evidence. Older status narratives
removed from current guides remain accessible through immutable Git links.

## Findings and corrections

| ID | Obsolete or conflicting statement | Correction |
| --- | --- | --- |
| DOC-001 | “Latest source” alternated between `9433010`/688 tests and `ea394e8`/780 tests | One current operator checkpoint; earlier P5 baseline clearly dated and separately linked |
| DOC-002 | Several stacked “latest” notices contradicted stale current sections | Current entry points rewritten; duplicated old status narratives moved to immutable history links |
| DOC-003 | Device Health still classified as an unported candidate | Read-only panel/backend/worker/report is integrated; staging/selection/switching remain disabled/separate |
| DOC-004 | P2 blueprint/QA stop gates still said game/camera/payment were unapproved or absent | Explicit original date/scope, later authorization/source pointers; do not restart completed P3/P4/P4b/P5 |
| DOC-005 | Older P3 top notice called 21/34 the latest report | Link later 16/16/twenty-cycle report, preserve unknown tested HEAD/device fields and original 21/34 evidence |
| DOC-006 | Earlier BUG-017 OPEN notices contradicted later 8/8 owner acceptance | Current OWNER-REPORTED PASS / MONITORING; original failures retained; no decoder fix/root cause invented |
| DOC-007 | V1 gear menu, payment ads/slips, DEMO payment/audio rules appeared to apply to v2 | Shared/legacy guides and asset notes now identify v1 controls versus current v2 behavior |
| DOC-008 | Artwork provenance still claimed game/reward were unimplemented; static asset note denied game dependencies globally | Actual original game and local/MOCK reward are integrated; trusted QRIS promo and real scanning remain absent; asset extraction scope clarified |
| DOC-009 | Legacy lab Threshold and branch's later Dizzy/Auto Tune documentation could be mistaken for one UI | Distinguish this checkout's lab/backend from newer reference-branch lab and independent JSON presets |
| DOC-010 | Zero quantity/digital-only and copy/session language ambiguous | Zero deselects; 1–9 means identical copies from one three-photo session/design; mixed-template source tariff already implemented |
| DOC-011 | Legacy uploads-during-retention-setup guidance conflicted with v2 upload guard | Separate v1 behavior from RetentionGuardedSync; acknowledgement still does not prove cloud deletion; BUG-009 OPEN |
| DOC-012 | Preflight/old reports/CI success could be read as current hardware PASS or zero CI skips | Source/owner/preflight/provider/physical gates distinguished; optional CI skip preserved; missing metadata stays unknown |
| DOC-013 | Public webhook and trusted promotion appeared as local trial/transition prerequisites | Current loopback simulator/status-check trial needs neither public deployment nor game promo; future scope/transition conditions remain explicit |
| DOC-014 | Old wait-before-all-source-work and new-branch instructions contradicted later owner direction | Continue safe approved work on existing v2 branch while laptop acceptance waits; no repeated approval per small authorized change |
| DOC-015 | Forms were Indonesian while current guidance was English | Active P5/operator copy/report text translated; IDs/storage keys/questions' intent/cycle logic preserved. Historical forms labeled and retained |
| DOC-016 | Audio release provenance implied all listed tracks existed in v1 | Distinguish original core bank from later v2 soft shutter/game tracks; no asset changes |

## Validation performed

- All local Markdown/HTML link targets and Markdown/HTML anchors checked;
  **zero missing targets / zero invalid anchors**. Final count is in the JSON.
- All repository JSON files parsed; the reference table retains exactly 19
  original branch rows. Current tables/commands/paths were checked against source.
- **1,152 tracked non-document files are byte-identical to the initial HEAD**:
  application/launchers/tests/dependencies/workflows/assets/raw JSON/text evidence.
- All **228** functional-source hashes in the latest operator manifest match;
  all **26** original game files and **11** health reference files match; the
  extracted original health worker method hash matches. QRIS reference has **27**
  matching files plus the already documented trial-helper compatibility adapter,
  unchanged by this audit. No new source drift is introduced.
- Both active forms retain identical JavaScript structure outside string literal
  content. The 26/8 IDs, storage keys and cycle membership remain unchanged.
- Node VM checks with minimal DOM/storage fixtures passed: initially unchecked,
  metadata import without auto-passing, English partial Submit, persistence/restore,
  P5 twenty-cycle qualification, no added operator cycle requirement, download
  handler and reset. These are **form-logic fixtures, not browser rendering**.
- `git diff --check` and documentation-only scope checks pass. No full GUI suite
  or Actions rerun was requested for these documentation-only commits.

**Validation limit:** Chromium was absent; its attempted download returned an
invalid archive. Browser pixel/layout validation of the translated forms is
**NOT_RUN**, including actual Windows rendering. Existing browser/layout evidence
belongs to the earlier form/source. No hardware/provider or cloud deletion test
was performed by this task, and no such PASS is inferred.

## Delivery and rollback

1. [`da375b3`](https://github.com/pratikto/PhotoBooth/commit/da375b3ace7048785bc558e45d10cf5a859709a1):
   current README/index/roadmap/status/architecture/handover/backlog/test ledger;
   pushed and remote HEAD verified before the next stage.
2. [`e4d0e89`](https://github.com/pratikto/PhotoBooth/commit/e4d0e8947c82821f5480615c0f689630a438d425):
   English engineering/visual contracts, decisions/protocol/prompt, current bug
   context and branch applicability; pushed and remote HEAD verified.
3. Final documentation stage: historical/shared-guide context, English active
   forms, QA indexes, changelog and this audit/inventory. Its exact delivery SHA
   is the commit containing the final version of this report; verify remote HEAD.

Rollback uses scoped inverse documentation commits after inspection. Preserve
all transaction journals, consumed attempts, photo/print manifests and raw reports.
No new branch, master/default/tag/release modification, merge, deployment,
production payment, trusted merchant promo or scanner/POS activation occurred.
