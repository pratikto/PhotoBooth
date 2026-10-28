# GUI v2 Operator Settings — owner decision register and supersession history
**29 October 2026 | OWNER-APPROVED DESIGN | NOT IMPLEMENTED.**

This document reconciles the full discussion, including earlier recommendations that were later refined. The owner explicitly **approved all suggestions and decisions across the discussion**, asked for exhaustive English Codex-ready documentation, and reaffirmed that **AR-00 through AR-13 remain the TOP PRIORITY**. Earlier statements are not erased; when superseded, both the original and current contracts are recorded.

## Decision ledger (canonical source for OPS work)

| ID | Decision / approved recommendation | Status and implementation boundary |
| --- | --- | --- |
| OS-DEC-001 | Existing secret Device Health shortcut becomes entry to **Meong Settings** | Approved future GUI v2 design; not mounted yet |
| OS-DEC-002 | Existing touch header long-press / F12 remains the hidden entry mechanism, with no customer-visible Settings control | Reuse current input behavior; touch variant essential for tablet |
| OS-DEC-003 | Before seeing Settings, operator must authenticate by **scanning QR with kiosk's camera** | QR replaces normal Settings login PIN; QR scanner required |
| OS-DEC-004 | For development, QR login is **static**, not dynamic | Static, high-entropy, unique per booth; reusable across login sessions until revoked |
| OS-DEC-005 | Static operator QR is a secret bearer credential: stored privately, hashed verifier locally, offline validation, revocation/rotation | Accepted security safeguards; never commit credential or show on kiosk |
| OS-DEC-006 | Future operational phase can upgrade to dynamic QR, one-use ~30–60s, issued by authenticated operator/admin app, optional challenge-response and roles | Future recommendation, not a prerequisite/production capability now |
| OS-DEC-007 | Full Settings accessible **only from the first Advertising/Idle page** | Later owner restriction **supersedes** older “any safe page/RECOVERY Health” access for **full Settings** |
| OS-DEC-008 | Advertising alone is insufficient: check **SAFE_IDLE** and current visit/payment/fulfillment leases; recheck after QR verification | Approved P0 guard; SAFE_IDLE never inferred only from a page label |
| OS-DEC-009 | Protected AR-09 RECOVERY operator inspect/resolve and PIN are separate; no full Settings access from RECOVERY | Compatibility exception; do not remove audited AR operator rescue |
| OS-DEC-010 | Camera broken? Preserve **OS-authenticated emergency maintenance**, not public on-screen PIN bypass | Operator-only physical/local maintenance fallback |
| OS-DEC-011 | While QR login is active, pause advertisement video/sound, GUI BGM where needed, face invitation and detector callbacks | Resume only if safe on cancel/logout; no audio overlap or lost visitor |
| OS-DEC-012 | Use one existing camera manager/owner; scanner shows mirrored live preview but decodes raw frame, bounded asynchronous detection | Reuse existing services and no second camera handle |
| OS-DEC-013 | Wrong/foreign QR, timeout, Back, minimize or new visit fail closed; no previous private photos | Error UX and session-generation guard required |
| OS-DEC-014 | Settings closes/logout immediately and returns to Advertising; **3-minute idle auto-logout** | Session ephemeral; restart never stays logged in |
| OS-DEC-015 | Settings has **exactly three tabs: Device Health, Audio Settings, Emulate Ticket** | Final visible labels; no dedicated fourth QRIS slip tab |
| OS-DEC-016 | Device Health tab preserves existing original reused v1 diagnostic and async worker, safe report and no device switches | Reuse, no regression; preserve BUG-018 rapid-input fix |
| OS-DEC-017 | Add grounded status + last test time and optional **Copy Diagnostic Report** (redacted as existing report) | Approved suggestion; no upload and sensitive data excluded |
| OS-DEC-018 | Settings footer includes non-sensitive Booth ID, version/build, current local/MOCK/Sandbox mode, last health check | Approved operator usability improvement |
| OS-DEC-019 | Audio includes owner's **Music**, **Button SFX** and **Other SFX** independently | Original requirements; mandatory |
| OS-DEC-020 | Also add **Master Volume**, **Mute** and **Test Sound** | Owner accepted assistant improvement; Game SFX separate slider only later if needed |
| OS-DEC-021 | Per-booth volume preferences persist across restarts; range/volume labels and bounded values, restore normal audio lifecycle | Approved; defaults in visual mockups are illustrative, not hard requirements |
| OS-DEC-022 | Retain independent ad-video sound owner and Meong Fly music, preserve Windows SDL audio repair, no rebuild | Approved regression/non-rewrite guard |
| OS-DEC-023 | Settings ticket tab is **Emulate Ticket**, replacing *Ticket Master* | Latest explicit rename; use “Emulate Ticket” in code/UI/docs |
| OS-DEC-024 | Emulate Ticket has **Merchant Promo — DEMO** category | For merchant receipt/discount scanner test; not real merchant proof |
| OS-DEC-025 | Emulate Ticket has **Meong Fly Entry — DEMO** category | One game attempt per test visit; original Meong Fly renderer/flow |
| OS-DEC-026 | **Both DEMO ticket QR payloads are static and reproducible across preview/print/restart in development** | Later owner's explicit choice; supersedes initially proposed unique QR per print and globally one-use test ticket |
| OS-DEC-027 | A static Meong Fly QR can be used **once in visit A**, and **again once in truly new visit B**; duplicate within A rejects even after restart | Separate immutable/static ticket from durable visit-scoped game admission |
| OS-DEC-028 | Merchant Promo static QR may be reused in another MOCK test visit; only one effect per visit, not twice in a checkout | Protect quote and per-visit promotion ledger |
| OS-DEC-029 | Provide presets: Merchant **Eligible / Not Eligible / Invalid**, Fly **Valid Entry / Already Used in Current Session / Invalid** | Approved test simulation scope |
| OS-DEC-030 | “Already Used” must rescan the **actually consumed valid QR**, not create a fake invalid “USED” payload | Approved realistic durable-ledger test |
| OS-DEC-031 | Distinct versioned QR namespaces for login, DEMO promo, DEMO Fly, recovery, payment, download, payment slip and possible future support | Each scanner accepts only its explicit purpose; no universal fallback |
| OS-DEC-032 | DEMO payloads never activate production discounts or real merchant claims; Midtrans Sandbox quote cannot be changed from GUI fixtures | Required P0 billing fence |
| OS-DEC-033 | For the initial scenario, **do not stack Merchant Promo with Meong Fly Rp2,500 win discount** | Accepted recommendation; precise future campaign policy needs later approval |
| OS-DEC-034 | Illustrative Merchant Promo: Rp50,000 purchase waives one Rp5,000 base/template fee; printing costs unaffected | Example/testing only, NOT a signed merchant business deal or fixed production threshold |
| OS-DEC-035 | Meong Fly one chance, win may give Rp2,500 discount in local MOCK, loss gives none, no “Main Lagi”, result continues to Template | Preserve original game/test reward, do not rebuild engine |
| OS-DEC-036 | Emulate Ticket supports QR preview and explicit **80-mm thermal print** using existing printer services | No automatic print on tab selection or login; same QR bytes across prints |
| OS-DEC-037 | Thermal print attempts need durable tracking, clear PREVIEW/SENT/UNCERTAIN distinction and no automatic retry on ambiguous delivery | Accepted safety; paper only verified physically |
| OS-DEC-038 | Existing dedicated Midtrans Sandbox **printer/Drive OFF** remains intact; DEMO print testing must be isolated and separately opted in | No silent enabling physical output or payment slip in Sandbox |
| OS-DEC-039 | Ticket/Test History for type, preset, print, scan, validation/consume, safe timestamps; clean expired DEMO records only | Approved usability and diagnosis, bounded PII-free retention |
| OS-DEC-040 | QRIS Payment Slip v2 checkout button **CETAK QRIS** remains its separately planned feature | Existing v1 shared printer source, same active provider order/QR, never auto-confirm PAID or prolong expiry; see GUI v2 roadmap |
| OS-DEC-041 | Recovery QR stays unique, secure, booth/order bound and customer-controlled; QR scanner for recovery remains AR-07 scope | **Never use static demo QR** for private recovery or bypass AR-06 verification |
| OS-DEC-042 | Optional Support/Service Ticket is only a future exception/remedy concept | Not a currently-issued ticket and not a new feature implementation authorization |
| OS-DEC-043 | Future real merchant validation must verify receipt/POS server-side with anti-replay; real Meong Fly entry uses unique transaction entitlement | Deferred operational migration; do not declare DEMO tests equivalent |
| OS-DEC-044 | Both Windows mini-PC/Ubuntu and full-tablet mobile deployment need separate camera/print/audio acceptance | Device-specific, not implied by mock tests |
| OS-DEC-045 | Preserve original portrait identity, layouts 800×1280 and 452×900, QR unmirrored, accessibility | Mandatory GUI regression; no rebuilt art/game |
| OS-DEC-046 | Test existing components before coding, audit implementation vs docs, use feature flags and strict privacy/rollbacks | Owner's docs-first and reuse-first governance |
| OS-DEC-047 | **Frequent micro-commit + immediate push, verify remote HEAD and update handover** to survive five-hour Codex/ChatGPT cutoff | Owner governance; do not save only unpushed local source |
| OS-DEC-048 | **No new branch, no master merge, no production enablement, no physical Sandbox payment-print test without separate permission** | Mandatory boundary |
| OS-DEC-049 | **AR-00–AR-13 remains highest development priority**, including AR-12 validation/AR-13 readiness and unresolved external gates | OPS queued after AR; documentation publication is not a directive to drop AR |
| OS-DEC-050 | This request is to **publish complete documentation**, not to execute the new OPS runtime feature immediately | OPS phases documented, ALL acceptance tests initially NOT_RUN |

## Exact correction/supersession log

| Earlier discussion | Later explicit owner correction | Reconciled requirement |
| --- | --- | --- |
| Optional PIN before Settings / login PIN | **Login must be QR** | Normal Settings login uses camera QR; separate AR-09 PIN remains for financial exception; OS emergency maintenance fallback, not an on-screen customer bypass |
| Dynamic operator QR with short validity and single use | **For now, static QR** | Use random per-booth static secret offline and rotatable; dynamic QR is planned operational upgrade only |
| Secret Settings access allowed whenever safely idle, potentially various pages | **Only Advertising first page** | Both **page = ADVERT** AND **SAFE_IDLE**, not either condition; no Settings in RECOVERY/face invite |
| Existing Device Health shortcut from protected Sandbox RECOVERY | Owner's strict page restriction on new Settings | Recovery exception remains a distinct AR-09 authenticated inspect/release flow, not full Settings |
| Tab originally named “Ticket Master” / “Print Ticket Master” | **Rename to “Emulate Ticket”** | Final GUI label Emulate Ticket; retain old name only in historical decision notes |
| Generate unique single-use promo/game ticket for every test | **Static until operations** | Stable versioned DEMO payload across restarts, prints and visits; avoid generating each time |
| One ticket one chance globally for game | Static reusable dev fixture + anti-replay requirement | One chance **per logical visit** for static fixture, durable consumed state even after restart; one globally unique claim per real operational ticket later |
| Fake “Already Used” QR | Genuine replay validation suggested and accepted | Print/scan actual valid QR once, rescan exact same QR within same visit, assert rejection |
| Separate merchant and game benefits potentially stack | “Don't stack yet” suggested and accepted | Explicit initial policy no stacking; future promotional stacking separate owner/business scope |
| Device Health was standalone popup | Settings becomes one menu with 3 tabs | Reuse original Device Health under QR-gated Settings, no second device manager |
| User requested 3 audio categories | Assistant recommended Master/Mute/Test and owner accepted all suggestions | Include **Master + Music + Button + Other + Mute + Test**, no compulsory separate Game SFX yet |
| QRIS Payment Slip included in next v2 plan | Settings now adds Emulate Ticket thermal print | Two independent features: payment slip from live provider order versus DEMO ticket emulator; not the same QR/print right |

## Proven current source vs proposed future feature

At the time of design audit (29 October 2026), read-only source showed:

- `photobooth/kiosk_v2/operator_health.py` provides **direct** Health popup on F12 or long-hold in Advertising and a protected Sandbox RECOVERY exception; it does **not** yet enforce QR authentication or a three-tab Settings shell.
- `photobooth/kiosk_v2/audio.py` provides original v2 PortraitAudio/music/effects; not yet the full persistent Master/Music/Button/Other operator mixer.
- `photobooth/kiosk_v2/demo_game.py` and `game_views.py` have a one-use `DEMO-` entry/ledger and original game; reusable per-visit QR ticket fixtures and Ticket emulator are **not** present as owner-approved implemented behavior.
- `photobooth/kiosk_v2/devices.py` has one AsyncCamera mailbox. Existing recovery code has **one-frame** scanner decode at a user action, not necessarily the new continuous operator QR camera UX.
- `photobooth/qris_print.py` exists for reusable thermal QR payment slips; that does **not** imply demo ticket printing is already mounted under GUI v2.
- The AR implementation is actively changing and may have progressed; **never pin OPS build decisions to this dated observation**. Refresh source, actual branch history and AR checkpoint before code.

These observations are documentation findings, **not** a fresh full regression or physical acceptance result.

## Explicitly deferred choices to resolve in OPS-00 or prior to operational launch

The owner's broad approval confirms the behavior above, but **does not fix arbitrary implementation constants**. Codex may safely choose testable nonfinancial defaults where needed, document them, and request approval for materially different customer-facing business behavior:

- Operator scanner timeout exact number and frame budget; 30–60 s is a suggestion for scan UX, while dynamic production QR lifetime 30–60 s is a different future concept.
- Static operator QR provisioning/user handoff mechanism (admin OS CLI vs maintenance console), storage format, auth hash implementation and safe printable operator credential channel (not through Emulate Ticket).
- Volume default percentages, slider step 1% vs 5%, write-on-change vs Save, video-ad Master gain coverage consistent with existing ownership.
- Demo static fixture values and exact namespace contents, invalid negative-QR library design, per-booth sharing policy, test-visit identity and inactivity timeout for a DEMO visit.
- Which merchant scenario, if any, wins when the no-stacking rule conflicts with an existing local game reward; don't silently choose financial priority in real payment.
- Whether history can be copied/exported, how many entries are shown, and per-fixture retention policy; no production PII.
- The exact user-facing message when a printer has an UNCERTAIN outcome, with operator confirmation and no silent retransmission.
- Production QR/merchant implementation, dynamic operator auth, role granularity, real promo stacking/settlement and hardware QR camera placement require **separate operational approval**.

## Do-not-lose checklist before closing an OPS task

- [ ] AR-00–AR-13 status and highest priority unchanged; AR docs/checkpoint linked.
- [ ] Exact three tabs and final name **Emulate Ticket** in all new GUI labels.
- [ ] Access by QR after hidden action, Advertising **AND SAFE_IDLE**, no Settings in Recovery.
- [ ] Static booth-bound operator QR is a secret; no token in GitHub/test report; rotation and OS fallback.
- [ ] Static reusable Merchant Promo and Meong Fly QR have distinct namespaces, MOCK-only enforcement, persisted one-per-visit consumption and true Already Used tests.
- [ ] Correct audio buses/Master/Mute/Test, app and ad-video sound ownership, durable config and regression.
- [ ] Reuse Device Health, game, camera, thermal printer; no unlocked device staging/duplicate handle.
- [ ] Print preview/80mm, attempt durability/uncertain-no-replay, no Sandbox printer bypass.
- [ ] Separate payment QRIS, payment slip, Drive download and unique customer Recovery Ticket.
- [ ] Meong Fly win reward Rp2,500, example merchant Rp50,000/Rp5,000 waiver, no stacking initially; example not production contract.
- [ ] Real hardware, current functional SHA, test evidence and permissions explicitly NOT_RUN until actually exercised.
- [ ] Reviewed micro-commits pushed to **existing branch** and exact handover state published when Codex begins actual work.

[Master contract](README.md) · [Implementation stages](IMPLEMENTATION-ROADMAP.md) · [129+ cases](ACCEPTANCE-MATRIX.md) · [Codex prompt](CODEX-HANDOVER.md).
