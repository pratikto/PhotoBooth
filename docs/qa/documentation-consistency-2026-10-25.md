# Documentation consistency audit — 25 October 2026

Repository: `pratikto/PhotoBooth`; authorized branch:
`feature/portrait-kiosk-v2-next`; initial remote HEAD:
`5f09eff9998c942ed54feef0cf0563fc3944611b`.

The owner requests a cross-check of all documentation for obsolete or conflicting
claims, with corrections in English. This is documentation-only work. Application
code, test implementation, workflows, dependencies, asset bytes and raw evidence
are outside the edit scope.

## Scope and sources

Review all 67 existing Markdown documents and the HTML acceptance forms on this
branch. Compare current guidance with launchers, v2 adapters/services, reference
provenance and recorded raw outputs/CI metadata. Dated records on other branches
remain pinned references, not edit targets or automatically integrated features.
The existing 19-branch audit is historical; do not present it as a fresh scan of
all branch tips. No application or hardware/provider regression is rerun for docs.

## Findings and corrections

| Finding | Correction |
| --- | --- |
| Conflicting latest source: `9433010`/688 tests versus `ea394e8`/780 tests | Current status/handover/test ledger distinguish the operator checkpoint from the earlier P5 baseline |
| Duplicated “latest” notices above stale current sections | Replace with one current entry and links to dated evidence |
| Device Health still classified as an unported candidate | Read-only panel/backend/worker/report are integrated; selection/staging/switching remain separate |
| P2/blueprint/P3/P4 “not authorized” or “not integrated” statements appear active | Identify their original scope and link current roadmap/status; preserve historical evidence |
| Earlier BUG-017 OPEN notices conflict with later owner acceptance | Current status is OWNER-REPORTED PASS / MONITORING, unknown tested HEAD; no decoder fix inferred |
| Preflight or earlier owner reports could be read as current-device certification | Keep source, preflight, owner-reported and physical/provider acceptance distinct |
| Zero quantity/digital-only and copy/session wording ambiguous | Zero deselects; 1–9 selects copies from one three-photo session per selected design |
| Public webhook listed alongside local-trial acceptance | Public deployment is separate; current isolated loopback simulator/polling trial does not require it |
| Mixed-language active guidance and duplicated historical instructions | Current guidance/corrections in English; history retained in dated records or immutable Git links |

## Delivery stages

1. Current README/index/status/roadmap/architecture/handover/test ledger/backlog.
2. Engineering, decisions/governance, branch/reference and historical guide context.
3. Full documentation inventory, link/anchor/evidence/source checks and final audit.

This report is updated with final checks and delivery commits when all stages finish.
