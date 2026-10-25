# GUI v2 — intended primary-branch transition

Owner direction, **25 October 2026**: GUI v2 is intended to become the primary
branch. This plan prepares that transition; no repository operation has occurred.

| Role | State at this documentation audit |
| --- | --- |
| Active development/commit target | `feature/portrait-kiosk-v2-next` |
| GitHub default | `master` (the earlier branch audit pinned `27f3801`) |
| Immutable v1 source baseline | `v1.0.0` / `07ce51d` |
| Latest tested functional v2 source | Print/Drive `266b2c8`; earlier operator `ea394e8` and P5 source/evidence `9433010` / `0dc6555` |
| Intended next primary product/branch | GUI v2, subject to specified gates and owner instruction |

## Evidence to assess

| Area | Current evidence / remaining boundary |
| --- | --- |
| Source/reuse | [Dated 19-branch audit](gui-v2-branch-audit.md); game, QRIS and read-only health reused |
| Regression | [Current test ledger](test_checklist.md): 800 local PASS/zero skips, matching-source three-job CI SUCCESS with one optional native model-assets skip covered locally, 133 verified PNGs |
| Windows metadata | Preflight `0dc6555` ready; not physical/provider acceptance |
| Current Windows integration | Earlier owner reports retained within their limits; [P5 form](qa/portrait-v2-p5/windows-checklist.html) not supplied for the new integration |
| Operator increment | Read-only panel/report in source; [eight-item form](qa/portrait-v2-operator-health/windows-checklist.html) separate |
| Merchant Sandbox/recovery | Source connected; actual official simulator/account acceptance pending |
| Game promotion | Local MOCK works; trusted QRIS promo contract absent. Full-price Sandbox is the current scope |
| Physical printing | Ordinary operator opt-in; uncertain-send/paper evidence separate from spool success |
| Drive/privacy/retention | BUG-009 OPEN; 30-day cloud deletion unverified |
| Repository operation | Default/protection/PR/rename/merge/launcher/release operation not performed |

A trusted QRIS game promotion or every reference-branch experiment is not an
automatic prerequisite for a repository transition. The owner must specify the
transition scope and any accepted outstanding limitations. Read-only Device
Health is already integrated; device switching, AI, WhatsApp and newer lab work
remain separate candidates. Default selection does not certify production use.

## When the owner requests the transition

1. Refresh repository/default/source state; preserve v1 refs and final v2
   checkpoint without touching operational data.
2. Identify the requested operation: set the existing v2 branch as default,
   rename, or PR/merge. These are distinct; this plan does not select one.
3. Review protection/required checks, open PR bases, CI filters, clone/update
   guidance and launcher policy. Default change alone does not change `main.py`.
4. Perform only the instructed operation, verify resulting remote/settings and
   update launch/rollback/release documentation with actual evidence.
5. Production QRIS, real scanning/POS, trusted promotions, deployment and release
   need their own scope. Do not activate them because the branch moved.
