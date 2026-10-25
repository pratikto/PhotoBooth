# GUI v2 — reference-branch documentation audit

Original snapshot: **25 October 2026 (Asia/Jakarta)**, repository
`pratikto/PhotoBooth`, **19 branches**. The original audit used
`git ls-remote --heads origin` and read-only `git show <SHA>:<path>`; no reference
branch switch/merge/push. Its
[manifest](reference/branch-doc-audit-2026-10-25.json) preserves document paths,
source SHAs and hashes. It is a dated inventory, not a perpetual latest-tip list.

**Current applicability reconciled against `5f09eff`:** read-only operator
Device Health/report has since been integrated at `ea394e8`. The original
candidate classification is superseded for that bounded scope. The original
manifest remains unchanged. This reconciliation does not claim a new scan/test
of all 19 branch tips; refresh relevant remote source before future reuse.

Active development/intended future primary branch is
`feature/portrait-kiosk-v2-next`. GitHub default remains `master`; `main.py` is v1.
[Current status](FEATURE_STATUS.md) · [transition plan](gui-v2-promotion-plan.md).

## All branches in the original snapshot

| Branch / snapshot | Pinned document | Finding at source | Current implication for GUI v2 |
| --- | --- | --- | --- |
| `backup/feature-kivy-gui-pre-printer-separation-20261017` · `1c717b9` | [README.md](https://github.com/pratikto/PhotoBooth/blob/1c717b940802c0f3f4d20ef26d7ea55960cb66e7/README.md) | Historical pre-separation printer/GUI/audio snapshot. | Archive only; do not restore old pricing or entire runtime. |
| `backup/feature-thermal-printer-pre-rebase-20261017` · `105e9b3` | [README.md](https://github.com/pratikto/PhotoBooth/blob/105e9b3c323973c61b0134b042fd6b55d2a1ea03/README.md) | Historical printer transport before rebase. | Archive only; newer batching/uncertain-send rules take precedence. |
| `backup/master-pre-v1-20261019` · `d4852cb` | [README.md](https://github.com/pratikto/PhotoBooth/blob/d4852cb56d2eea92ae135a5ab38ce3676e2f3381/README.md) | Early Tkinter/single-photo master backup. | Historical rollback reference, not the starting point for v2. |
| `docs/feat-021-whatsapp-photo-delivery` · `aebde84` | [docs/DECISIONS.md](https://github.com/pratikto/PhotoBooth/blob/aebde8438833d27aeed25f3873229aca64d11636/docs/DECISIONS.md) | WhatsApp proposed as an extra delivery channel; retain Drive QR. | Design only; no v2 WhatsApp integration. |
| `docs/meong-fly-tutorial-gate-20261021` · `980af99` | [docs/DECISIONS.md](https://github.com/pratikto/PhotoBooth/blob/980af99798b67084aff517f36d76e2c1af767c02/docs/DECISIONS.md) | Mandatory tutorial once per visit, including postgame. | Implemented in v2 VisitFlow; design-only label describes this old branch. |
| `docs/post-v1-release-reconciliation-20261019` · `359e8e5` | [docs/README.md](https://github.com/pratikto/PhotoBooth/blob/359e8e56cee8c049ff927433cab562804d082f41/docs/README.md) | Separates source status, owner reports, CI and v1 release evidence. | Documentation discipline retained; old counts/deferrals are historical. |
| `feature/ai-background-studio` · `eb368c1` | [docs/DEVELOPMENT_HANDOVER.md](https://github.com/pratikto/PhotoBooth/blob/eb368c11b52ee4e88d5644b07a79b7bdd9178f2d/docs/DEVELOPMENT_HANDOVER.md) | Offline AI backend and Original/Clean Studio v1 controls with cache/fallback. | Separate candidate; not ported to v2; latency/model/Windows/paper gates remain. |
| `feature/device-health` · `dbbe055` | [docs/device-health.md](https://github.com/pratikto/PhotoBooth/blob/dbbe055bb1281ad065a5ba0c3593cfbfbd388bd3/docs/device-health.md) | Original read-only health panel/worker, staged restart selection and discovery. | Read-only panel/backend/worker/report now reused in v2 at ea394e8; staging/switching remain disabled. No automatic hot-swap/restart. |
| `feature/dither-tuning` · `e89e6ee` | [docs/dither-gui-parameter-guide.md](https://github.com/pratikto/PhotoBooth/blob/e89e6ee1c758abc169ee250ee9285022f41cfc3b/docs/dither-gui-parameter-guide.md) | Newer Floyd/Bayer/Dizzy lab, Auto Tune/enhancement and parameter guide. | Newer lab is not automatically in v2. Preserve the existing printer profile. |
| `feature/kivy-gui` · `38fbaa5` | [README.md](https://github.com/pratikto/PhotoBooth/blob/38fbaa5c8f3d599848d33c82c2b2af5cf3aa6f8f/README.md) | V1 original templates, session/copy pricing, RAW batches and preview mirror. | Selected shared backends reused; main.py/UI/audio v1 remain separate from v2. |
| `feature/local-photo-session-mvp` · `a3c1618` | [README.md](https://github.com/pratikto/PhotoBooth/blob/a3c161856eab22c5d98790aa1ab03c015fa2e8c2/README.md) | Tkinter transaction/folder/counter/upload prototype; quantity once meant sessions. | Historical; v2 quantity means identical copies, not extra sessions. |
| `feature/meong-flappy-challenge` · `672e3f7` | [docs/features/FEAT-021-meong-fly.md](https://github.com/pratikto/PhotoBooth/blob/672e3f7089bb40940e5b41644ceb656aa63aafbb/docs/features/FEAT-021-meong-fly.md) | Original renderer/flow/sprite/emitter and local DEMO camera scanner. | 26 original files reused directly in v2; manual DEMO input only, scanner/POS not mounted. |
| `feature/portrait-kiosk-gui` · `92101d9` | [docs/portrait-kiosk-v2.md](https://github.com/pratikto/PhotoBooth/blob/92101d9f778e0c8f282a616bb815b52dda1d37b2/docs/portrait-kiosk-v2.md) | Initial portrait P0–P2 and isolated audio/UI foundation. | Ancestor; placeholder/no-camera status is obsolete for v2-next. |
| `feature/portrait-kiosk-v2-next` · `0dc6555` | [docs/qa/portrait-v2-p5/README.md](https://github.com/pratikto/PhotoBooth/blob/0dc6555d299cdab19d952e92df2ae660cdc4676d/docs/qa/portrait-v2-p5/README.md) | P5 snapshot: source 9433010/evidence 0dc6555, photo/game/MOCK/Sandbox. | Active development branch has since added operator source ea394e8/evidence 5f09eff; this row remains the original audit snapshot. |
| `feature/qris-payment` · `3cc8a8e` | [docs/QRIS_SANDBOX_TRIAL.md](https://github.com/pratikto/PhotoBooth/blob/3cc8a8e360e8c2100a3077b755664eb61d0216ea/docs/QRIS_SANDBOX_TRIAL.md) | Server quote/auth, provider reconciliation, journal/grant and isolated merchant trial. | Service/client/journal reused with native v2 host; no trusted game-promo API or production activation. |
| `feature/thermal-printer` · `a38d4a6` | [README.md](https://github.com/pratikto/PhotoBooth/blob/a38d4a67e0f4938ac33d8c165c2dd52f0baf8ca7/README.md) | Early printer backend/operator UI, with some old quantity/pricing text. | Relevant backend already present; do not replace current v2 with old UI/business rules. |
| `fix/kivy-music-playback` · `27f3801` | [docs/DEVELOPMENT_HANDOVER.md](https://github.com/pratikto/PhotoBooth/blob/27f3801b235d81dc0a49ab201f3e143b62314413/docs/DEVELOPMENT_HANDOVER.md) | Same tip as master at the original audit; v1 music and health-revert history. | V1 reference; preserve separate v2 audio ownership. |
| `master` · `27f3801` | [docs/README.md](https://github.com/pratikto/PhotoBooth/blob/27f3801b235d81dc0a49ab201f3e143b62314413/docs/README.md) | Default at original audit, v1 baseline after fixes/revert. | Default still master at this audit; not the documentation commit target. |
| `revert/feat-008-stage-a-20261019` · `57ff555` | [docs/DEVELOPMENT_HANDOVER.md](https://github.com/pratikto/PhotoBooth/blob/57ff555e15fbe6a0150900fe3d6c5177a11e46d6/docs/DEVELOPMENT_HANDOVER.md) | Records rollback of an unauthorized FEAT-008 merge. | Governance history; reference existence is not merge permission. Later approved read-only v2 reuse is a distinct scope. |

## Reconciliation rules

- Source on another branch is not automatically active in v2. Original game,
  QRIS and read-only health are reused with documented adapters; device selection,
  AI, WhatsApp and newer lab updates remain separate.
- Preserve historical source/CI/owner results at their recorded date/SHA; do not
  transfer them into a new hardware/provider PASS. Latest operator 780-test
  source and earlier P5 688-test source are distinguished in the
  [test ledger](test_checklist.md), including CI optional skips.
- Quantity zero deselects; 1–9 means copies from one three-photo session/design.
  Tariff Rp5,000/design + Rp5,000/copy; local/MOCK win discount Rp2,500 once/order.
  Sandbox requires full-price/no-promo consent until a trusted backend API exists.
- FEAT-021 names game, AI and WhatsApp on different historical branches. Append
  topic/branch; do not combine approvals or silently renumber history. V2 is FEAT-022;
  QRIS is FEAT-020.
- Refresh source, inspect actual working UI/controller/renderer/assets/tests and
  reuse them. Record hash/provenance and concrete compatibility exceptions.
  This audit authorizes no new port, branch deletion, merge, production or deployment.
