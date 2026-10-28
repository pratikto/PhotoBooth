# Codex handover / implementation prompt — future Meong Settings GUI v2

**Status:** OWNER-APPROVED DESIGN REFERENCE, not implementation authorization in this documentation-only task. Dated 29 October 2026. No source or runtime changes have been made under this documentation package.

## Mandatory priority, scope and source-of-truth

**Work sequence:** Current **AR-00 → AR-13** autonomous recovery is **TOP PRIORITY**. A Codex session opened now must **continue its first actually unfinished AR micro-increment from the latest verified remote checkpoint**, not start OPS just because a new document was published. See:

1. `AGENTS.md` and `docs/DEVELOPMENT_PROTOCOL.md` for docs-first, safe micro-commits, regression, branch and release rules.
2. `docs/qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md` for latest verified source and next exact action.
3. `docs/qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-ROADMAP.md` and `AUTONOMOUS-RECOVERY-MASTER-PLAN.md` plus provider/test/operations contracts for authoritative AR dependencies and NOT_RUN gates.
4. `docs/DEVELOPMENT_HANDOVER.md`, `docs/FEATURE_STATUS.md`, `docs/README.md` and `docs/next_step.md` for current evidence, unfinished work and owner decisions.
5. **Only after separate owner direction to implement post-AR Settings:** [complete master spec](README.md), [OPS-00..OPS-10 roadmap](IMPLEMENTATION-ROADMAP.md), [test matrix](ACCEPTANCE-MATRIX.md), [full decision/supersession register](DECISION-REGISTER.md).

Never assume stale dated “AR-09.c1” header or a docs-only commit is the current functional source. Verify `git status`, actual remote branch/HEAD and recent commits. Preserve other processes' source changes and never overwrite a running AR task. Read every linked affected document completely before code, update docs after. Repository name: `pratikto/PhotoBooth`; authorized branch: `feature/portrait-kiosk-v2-next`; `master` and `main.py` remain unchanged.

## Copy/paste prompt to begin only AFTER AR priority has been respected

```text
PROJECT: Meong Photobooth GUI v2
Repository: pratikto/PhotoBooth
Existing branch only: feature/portrait-kiosk-v2-next
TASK: Implement the approved Operator Settings / Static Operator QR Login / Audio
Settings / Emulate Ticket specification in independently tested increments,
but ONLY after verifying AR-00 through AR-13 have received their prioritized
completion/readiness treatment, and after obtaining the required authorization
for this OPS implementation phase. Do not start OPS if AR work still takes priority.

READ BEFORE CODE:
- AGENTS.md, docs/README.md, docs/DEVELOPMENT_PROTOCOL.md,
  docs/DEVELOPMENT_HANDOVER.md, docs/FEATURE_STATUS.md, docs/DECISIONS.md,
  docs/next_step.md, docs/portrait-kiosk-v2.md;
- docs/qa/portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md,
  AUTONOMOUS-RECOVERY-ROADMAP.md, AUTONOMOUS-RECOVERY-MASTER-PLAN.md and
  linked Midtrans provider/recovery test/operations contracts;
- docs/qa/portrait-v2-operator-settings/README.md,
  IMPLEMENTATION-ROADMAP.md, ACCEPTANCE-MATRIX.md, DECISION-REGISTER.md,
  CODEX-HANDOVER.md;
- docs/qa/portrait-v2-operator-health/README.md and current source.

ABSOLUTE REQUIREMENTS:
1. Full Settings available only from first ADVERT/Advertising screen AND from
   authoritative SAFE_IDLE. Existing F12/1.5s header hold opens Operator QR
   Login, NEVER Settings directly. Recovery/checkout/photo/game/face invitation
   cannot reach full Settings. Do not break existing AR-09 separate authenticated
   operator PIN and recovery exception.
2. Development operator login by SECRET STATIC booth-unique high-entropy QR,
   scanned through existing single camera. Local hash/verifier, offline use,
   rotate/revoke, no credentials in GitHub/logs/QR demos/screenshot. Resume ads
   after cancel/timeout; close/minimize/logout revokes session; 3-minute idle
   logout. OS-authenticated emergency maintenance for failed camera.
3. Exactly three tabs: Device Health, Audio Settings, Emulate Ticket. Use the
   final name "Emulate Ticket", NOT "Ticket Master".
4. Device Health must REUSE working native v1/controller diagnostics, keep
   read-only selection/health reporting, prevent rapid tap hang, optionally add
   redacted Copy Diagnostic Report. Non-secret Booth ID/version/current mode footer.
5. Audio Settings: Music, Button SFX, Other SFX plus Master Volume, Mute and
   Test Sound. Persist bounded per-booth values across restart, preserve Kivy
   one-sound-owner, Windows SDL channel correction, original Meong game music,
   still-ad BGM and video-ad own-audio lifecycle. Optional future separate Game
   SFX is not mandatory now.
6. Emulate Ticket in development: TWO reusable STATIC QR categories: Merchant
   Promo DEMO and Meong Fly Entry DEMO. Same payload each preview/print/restart.
   Presets:
   - Merchant: Eligible, Not Eligible (below minimum), Invalid.
   - Meong Fly: Valid Entry, Already Used This Session, Invalid.
   "Already Used" is ACTUAL REPLAY OF SAME VALID QR after a successful consume,
   NOT a fake QR containing "USED".
7. Static DEMO Meong Fly QR is usable once per logical test visit (survives
   restart) and again in truly new visit. Existing original DEMO one-use ledger,
   original game assets/engine, one game chance, Rp2,500 MOCK win discount,
   no replay and result-to-Template remain intact.
8. Example simulated merchant Rp50,000 qualifying receipt waives one Rp5,000
   base/template fee but never print fees. It is not production campaign
   authority. Do not stack Merchant Promo with Meong Fly reward in initial
   test policy. DEMO never changes real Midtrans Sandbox/production quote.
9. Reuse QR generator and 80-mm POS thermal printer for preview / explicit
   "Print Demo Ticket" / optional test history; safe attempt/uncertain/no
   automatic replay, no QR mirroring. Dedicated Midtrans Sandbox printer and
   Drive remain OFF and cannot be bypassed. QRIS Payment Slip is a DIFFERENT
   planned future checkout feature; Recovery Ticket stays private/unique.
10. One existing camera owner, mirrored LIVE PREVIEW with original raw-frame
    QR decoder, bounded worker, typed namespace validation and no stale
    callbacks. No QR cross-purpose acceptance, no private photo exposure.
11. Render and inspect 800x1280 and 452x900, test Windows mini-PC, Ubuntu
    and later Android tablet independently. No code/test/release claims from
    documentation alone.

PROCESS:
- Audit current source, branch, AR staging and bugs; do not rebuild existing
  camera, original game, Device Health, audio owner or printer.
- Implement OPS-00 to OPS-10 in dependency order ONLY after authorized.
- Break stages into safe micro-increments (OPS-XX.a/b/c).
- After EVERY safe meaningful increment: run focused tests, update related
  English docs, commit and PUSH immediately to existing feature branch,
  verify remote HEAD, record exact test evidence and handover. Do not defer
  pushes to end of stage or five-hour chat limit. Do not push broken code or
  credentials just to checkpoint; local-only work is not saved remotely.
- Final full applicable regression after final functional code change; real
  merchant, camera/phone, printer paper, Drive, Ubuntu and tablet evidence must
  be truthfully PASS/FAIL/SKIP/NOT_RUN rather than assumed.
- Never create a branch, force-push, merge master, deploy production, enable
  real payments, refund, silently alter pricing, print a live Sandbox QRIS or
  reset a customer database without explicit corresponding approval.

START BY REPORTING:
1. Existing remote branch and pinned functional SHA / dirty state.
2. Which AR stage is really unfinished and why it retains top priority.
3. If OPS is authorized and ready: OPS-00 audit and first micro-test plan.
4. Original modules to reuse vs identified gaps/risks.
5. Proposed exact safe commit, focused tests and rollback boundary.
```

## Expected deliverables when OPS implementation is approved

- Typed auth/config/schema contract and secure provisioning/rotation guide; no QR secrets in repository.
- Native lifecycle and the exact three Settings tabs behind Advertising + SAFE_IDLE.
- Audio config/mixer and correct ad/game/music ownership regression.
- Reusable static DEMO QR fixture definitions, receipt/game Mock validation, actual ledger-consumption negative cases, safe separated payment boundaries.
- Native QR preview and 80-mm printer worker integration, durable attempt/no-replay and redacted test history.
- Evidence of all applicable cases from [the acceptance matrix](ACCEPTANCE-MATRIX.md), native snapshots and real device gates.
- Reconciled English documentation, precise rollback and micro-pushed verified checkpoints. No release or production integration unless separately authorized.

## Checkpoint content (never omit)

```text
Timestamp / work environment:
Branch / local HEAD / actual origin HEAD / dirty state:
AR-00..AR-13 status; exact first unfinished AR substep:
Work stage/substep (OPS only when separately authorized):
Paths inspected and changed / migration + compatibility:
Test commands and actual PASS FAIL SKIP NOT_RUN counts:
Midtrans Sandbox / printer paper / Drive / phone camera / Windows /
Ubuntu / tablet acceptance and exact evidence:
Known failures, privacy/payment concerns and owner decisions outstanding:
Last verified pushed commit SHA / next safe action:
Any unpushed local changes and whether they can be recovered remotely:
```

**Documentation-only handover from this request:** OPS code **NOT_STARTED**. Tests **NOT_RUN**. All core decisions are recorded in the complete master and the explicit supersession table. **Never mark AR-13 complete because this package exists.**
