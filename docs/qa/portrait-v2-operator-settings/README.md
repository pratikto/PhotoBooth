# Meong Photobooth GUI v2 — Operator Settings, QR Access and Emulate Ticket
## Authoritative owner-approved design specification (29 October 2026)

> **STATUS: OWNER-APPROVED DESIGN / DOCUMENTATION ONLY / NOT IMPLEMENTED IN GUI v2.**
> This document captures the complete operator-settings discussion, later corrections, risks and recommendations accepted by the owner. It is a **future follow-up**, NOT a new AR stage and NOT permission to interrupt autonomous recovery.
>
> **NON-NEGOTIABLE EXECUTION PRIORITY:** Finish and verify the existing **AR-00 → AR-13 autonomous QRIS and photo-session recovery roadmap first**, continuing from its **latest verified micro-checkpoint**; never restart completed AR stages or jump ahead to Settings. AR-13 is a readiness/owner-decision gate, not permission to activate production. Do not use these Settings documents as evidence of completed AR tests or device acceptance. Follow [the authoritative AR roadmap](../portrait-v2-sandbox/AUTONOMOUS-RECOVERY-ROADMAP.md), [current AR checkpoint](../portrait-v2-sandbox/AUTONOMOUS-RECOVERY-CHECKPOINT.md), [handover](../../DEVELOPMENT_HANDOVER.md) and [development protocol](../../DEVELOPMENT_PROTOCOL.md).
>
> **Repository:** `pratikto/PhotoBooth` | **Existing development branch:** `feature/portrait-kiosk-v2-next`. No new branch, no `master` merge, no default-branch change, no deployment, production payment or physical Sandbox printer activation in this task. **All changes under this request are documentation only.**

### Navigation for Codex

- **This file**: authoritative UX, architecture, security, individual tab behavior, QR semantics and phase boundaries.
- [IMPLEMENTATION-ROADMAP.md](IMPLEMENTATION-ROADMAP.md): dependency-based, micro-commit execution plan **after** AR-00–AR-13.
- [ACCEPTANCE-MATRIX.md](ACCEPTANCE-MATRIX.md): positive/negative/restart/device security and functional tests; initially **NOT_RUN**.
- [DECISION-REGISTER.md](DECISION-REGISTER.md): complete dated owner decisions, supersessions, open choices and future operational migration.
- [CODEX-HANDOVER.md](CODEX-HANDOVER.md): copy/paste development prompt, initial investigation, checkpoint format and prohibition against implementing ahead of AR.
- Existing owner-confirmed native health reuse: [Device Health QA](../portrait-v2-operator-health/README.md); QRIS payment slip follow-up: [GUI v2 roadmap](../../portrait-kiosk-v2.md); AR-09 operator exception flow and PIN: [AR master](../portrait-v2-sandbox/AUTONOMOUS-RECOVERY-MASTER-PLAN.md).

---

## 1. Intent, scope and the decision hierarchy

Create **one operator-only Meong Settings menu** rather than adding separate secret shortcuts as new features arrive. The existing secret action that previously opened Device Health must instead open **Operator QR Login**, and only on the first **Advertising / Idle page** when **SAFE_IDLE** is proven. The authenticated menu contains exactly **three tabs**:

1. **Device Health** — reuse the existing read-only diagnostic functionality.
2. **Audio Settings** — per-booth Master Volume, Music, Button SFX, Other SFX, Mute and Test Sound, plus persistent audio configuration.
3. **Emulate Ticket** — final approved name, replacing the earlier names *Ticket Master*, *Print Ticket Master* and *Demo Ticket Generator*. It creates/previews/prints **static DEMO QR tickets** for (a) Merchant Promo validation and (b) Meong Fly entry, with controlled test presets and a non-sensitive ticket/test history.

Do **not** add a fourth Settings tab to hold ordinary QRIS payment printing. **QRIS Payment Slip** is a distinct previously approved GUI v2 **future checkout action**, already tracked in `docs/portrait-kiosk-v2.md` / `docs/next_step.md`, with separate provider-order, thermal-printer and Sandbox-off requirements. Do not conflate it with Emulate Ticket.

The accepted **development** design supersedes earlier *dynamic/unique ticket per scan* proposals where explicitly stated. Recommendations for eventual production remain documented, not silently discarded.

| Area | Development decision (approved design) | Operational evolution (future, not built) |
| --- | --- | --- |
| Settings access | Secret gesture → camera scans **static operator QR** → Settings; only Advertising + SAFE_IDLE | Optional short-lived dynamic per-operator QR with stronger authorization |
| Operator credential | One high-entropy **static secret QR per booth**, hash/config stored locally, offline validation, revocable/rotatable | Expiring 30–60 s, single-use QR issued by authenticated operator administration; optional challenge-response/role model |
| Merchant Promo test | **Static, reusable DEMO QR** and test presets; repeatable in future separate test visits | Real merchant receipt/API verified eligibility, unique use, redemption audit |
| Meong Fly entry test | **Static, reusable DEMO QR**, at most **one claimed attempt in the same customer visit/session** | Real unique receipt/ticket → one attempt globally per merchant-verified entitlement |
| Recovery Ticket | **Never static**: existing high-entropy per-order customer recovery capability / private claim | Preserve secure per-order uniqueness, current-provider verification and privacy |
| Menu identity | Exactly Device Health, Audio Settings, **Emulate Ticket** | Extra operator features only by a new owner-approved scope |
| Menu entry page | **Only Advertising/Idle** with a separate SAFE_IDLE guard | May be revisited explicitly; not loosened by a new state name |
| Deployment | GUI v2 future development, no production or merchant activation | Security, hardware and independent release acceptance |

### Scope exclusions

- No alteration to, cancellation of or bypass around existing **AR-00–AR-13** stages, AR-09 backend **operator PIN/resolve/release** flow, or recovery-ticket ownership check.
- No production QRIS, real refund, merchant payout, trusted receipt promotion, POS connectivity or entitlement grant derived from a DEMO QR.
- No separate camera handle, independent rewritten photo engine, game engine, thermal transport, Device Health controller or audio owner.
- No hardware switching from Device Health, no speculative driver restart, no automatic printer replay or hot swap.
- No real customer data in fabricated tickets, screenshots, source-controlled fixtures or diagnostics.
- The QR login is a **convenience/authentication** feature, not an override of SAFE_IDLE and not proof that a payment succeeded.

## 2. Exact customer-safe entry and navigation contract

### 2.1 Normal flow

```text
ADVERTISING (first page, customer-safe, SAFE_IDLE)
  |
  | existing SECRET OPERATOR ACTION only
  v
OPERATOR QR LOGIN (camera live preview + visible scan area)
  |          | invalid / timeout / cancel / minimize
  |          +-------------------------------------> ADVERTISING
  |
  | recognized valid booth-bound static operator QR
  v
MEONG SETTINGS (authenticated, single operator-owned UI)
  |-- Device Health
  |-- Audio Settings
  +-- Emulate Ticket
  |
  | Close / Logout / inactivity timeout / suspend
  v
ADVERTISING (fresh private state, normal ad/audio lifecycle)
```

The existing operator secret entry is **F12 on supported desktop keyboards** or **long-press Meong header for ~1.5 seconds** on touchscreen, as currently implemented in `photobooth/kiosk_v2/operator_health.py`. Preserve the no-accidental-entry guard: a short tap, drag, or right-click should not enter; do not place a large customer-visible Settings button on the advertisement. On Android tablet, rely on the touch gesture rather than assuming a hardware F12 key.

**Strict allowed entry:** both conditions below must be true at **gesture time** and **immediately before authenticated transition**:

- `navigation.page == ADVERT` (the real first Advertising page), with no face invitation overlay/transition; AND
- authoritative `SAFE_IDLE == true`, established from relevant current kiosk visit/camera/checkout/fulfillment ownership state, not just a cosmetic page name.

Do **not** allow Settings entry from Face Invitation, Tutorial, Template Carousel, Meong Fly intro/receipt/game/result, MOCK checkout, Midtrans QRIS checkout, Photo Confirm, Capture, Review, Result, or Customer Recovery pages. In particular, **an advertising page displayed while a previous payment/fulfillment owns the live booth does not by itself establish SAFE_IDLE**.

### 2.2 Defining SAFE_IDLE without breaking recovery

Codex must inspect current AR-09 service isolation/fencing and real owner/lease metadata when implementing; do not create an independent boolean that becomes true after resetting a screen. The admission predicate must reject at least:

- An active customer visit or face invitation; a pending terminal navigation callback.
- Local photo capture, retake, composition, printing side effect or open mutable media transaction that still owns this camera/kiosk.
- Active payment flow with current customer ownership, uncommitted startup/grant transfer, pending checkout admission, unresolved active local session.
- An unsafe/ambiguous recovery/ownership transfer not yet durably isolated.
- Busy or overlapping operator action, active scanner, a stalled UI job that still owns the resource, app suspended/closing.
- An observed mismatch between UI visit token, local lease, expected backend service fence and current payment/fulfillment metadata.

**Safe in the background, if isolated:** an old protected payment recovery, bounded backend status reconciliation, or Drive upload/delivery job **may continue** if it has no mutable control of current UI/camera and cannot disclose old media to a new operator/customer. Do not block Settings forever simply because a safely detached cloud upload exists. However, Device Health or Emulate Ticket must not restart, reset, cancel, reprint, disclose or rebind these jobs.

**AR-09 compatibility:** the pre-existing native read-only health/operator entry from `SANDBOX_CHECKOUT` / `RECOVERY` is an **exception path**, not permission to enter the new full Settings menu there. Preserve whatever separate, authenticated, audited operator rescue/release channel AR-09 needs, but route **full Settings** only via Advertising + SAFE_IDLE. Existing backend AR-09 operator PIN remains independent; **the new QR must not silently become a replacement for that PIN or grant AR-09 resolve/release authority**.

### 2.3 Advertisement, camera and audio on opening

- On accepted secret entry, suspend/freeze advertisement visual playback and its independently owned video sound, plus normal idle BGM if applicable; pause face invitation (5-second face presence), palm detector and its callbacks. A face emerging while QR login is active must **not** pop an invitation or consume the operator's touch.
- Use the **existing `AsyncCamera` owner** (`photobooth/kiosk_v2/devices.py`) and read fresh immutable/copied frames. Show a horizontally **mirrored live preview**, as approved for the photo UI, while decoding from original unmirrored frame pixels. Overlay a visible scan box, short instruction, Back/Cancel control, a bounded spinner and accessible retry hints (move phone, reduce glare, adjust screen brightness).
- Scan automatically at a bounded frequency (for example 5–10 decoded frames/s subject to device benchmarking) off the Kivy UI thread; avoid allocating one new QR decoder/worker every frame, stale callbacks, loading the camera twice, or saturating small tablet CPUs.
- Verify operator QR role + version + booth binding + secret/proof, **constant-time** secret verifier where feasible, and local credential/config integrity before admitting. Wrong QR type, expired/unknown version, other-booth operator QR, camera failure and malformed payload return a non-revealing error and do **not** open Settings.
- On success, retire scanner generation and never leave frames/token in UI logs. Open Settings in an authenticated operator-only state, not by setting the old health popup's “open” flag.
- On Cancel / wrong QR / timeout / app minimize / screen close: clean up scanner callbacks and temporary frame references, end the partial operator challenge, restore the advertising/sensor/audio lifecycle safely (subject to current SAFE_IDLE), and never start a photo, a charge, a print or a private claim automatically.
- If an invite/customer flow wins a race before the login transition, reject late operator verification by **page, visit generation and owner fence**, not just latest boolean.

### 2.4 Settings session

- Opening the menu does not unlock photo/recovery data. Limit authenticated operator capabilities to the three approved tabs and their approved safe actions.
- **Inactivity logout:** use **three minutes** as the provisional approved design; track real interactions only, no refresh loop counting as activity. Close/logout and minimize/background must revoke the Settings session immediately; test app restart is logged out.
- Settings Close logs out and returns to the **first Advertising page**, releasing private scanner/Health dialog/media references. Resume ads and normal music only through the existing Audio Manager, avoiding two loops.
- One Settings session, one scanner owner, one Device Health probe at a time. Buttons disabled while underlying operation is active; drop late callbacks based on monotonically advancing UI/session generation.
- Show Booth ID, application version, branch/build identifier (when available), current application mode `LOCAL / MOCK / MIDTRANS SANDBOX` and last health check in an operator-only status footer. Do not show merchant keys, token fingerprints, serial numbers or raw filesystem paths.

### 2.5 Static QR operator credential for **this** development phase

- **One high-entropy random, booth-specific QR secret**, not a predictable `PB001-ADMIN` string, static shared test phrase, six-digit password or code committed to GitHub. Generate through a separate local provisioning action, store only a salted/appropriately hashed verification record and non-secret version/booth binding in a per-booth **local config**; keep the actual QR for the operator securely outside the kiosk. Offline checking is required in development.
- QR has a clearly separated prefix/namespace/role (example design `MEONG-OPERATOR-LOGIN-V1:...`); decoder must not accept Merchant Promo, Meong Fly, Recovery, photo-download, or QRIS payment payload.
- Provision/backup and display/print operator credential through a **controlled administrator setup path**, not a customer page or ordinary Emulate Ticket printing. Avoid putting secret in `AGENTS.md`, test fixture, source, analytics, screenshots, debug console, diagnostics or cloud asset sync.
- Token remains reusable across logins **until rotated**, not a single-use OTP. Design a secure, tested **rotate/revoke** flow for lost/photographed QR that invalidates the prior credential; a credential may be disabled per booth without deleting user payment data. Add limited failed-scan rate/throttle and generic rejection messaging; do not create permanent camera denial from bad ambient QR frames.
- Future operational improvement: an authenticated admin phone/portal issues **dynamic short-lived (30–60 s), one-use** operator QR bound to booth/operator/authorization; optionally kiosk/phone challenge-response, role and audit. **Not a prerequisite now**, not a production-grade security claim for static QR.
- **Camera failure fallback:** a physically/local OS-authenticated maintenance path for actual authorized owner/support, through OS login/admin terminal or managed provisioning, not a public PIN fallback rendered on the customer touchscreen. This is required because Device Health must remain maintainable when the QR camera is broken. It does not bypass financial ledger guarantees or AR-09 exception controls.

---

## 3. Settings tab: Device Health (reuse, do not regress)

Keep all existing read-only Device Health checks, warnings and safe report export. Refer to `photobooth/kiosk_v2/operator_health.py`, `health_service.py`, `health_report.py`, `photobooth/ui_health.py`, `v1_health_controller.py` and [existing operator health evidence](../portrait-v2-operator-health/README.md). Preserve original v1 worker/controller and v2 adapters, do not rebuild an alternate Health service.

- Read-only summaries: camera fresh mailbox frame/readiness, printer route/queue discovery (not proof of paper), available storage, network probe (not proof of Midtrans/Drive), local media, GUI heartbeat and OS candidate inventory as in current source.
- Show **Ready / Warning / Error / Unknown / Checking** grounded in observable facts, plus **last checked timestamp** and refresh; never translate queued/spooled to physically printed or a network ping to connected merchant status.
- Serialize probe activity with the current worker lock; protect against rapid multi-tap/hang (BUG-018), stale results and close/minimize; avoid automatic background poll storms.
- Keep **Copy Diagnostic Report** as proposed optional user-facing convenience, next to existing **SIMPAN LAPORAN LOKAL** / safe export. The copied version must pass the **same allowlist/redaction** as the atomic on-disk report; consider clipboard sensitivity on shared public booth and clear/avoid clipboard when unsafe. No automatic upload. Existing selection/staging actions stay **disabled**, no device hot-swap.
- Do not expose raw photos/camera frames, merchant/order identifiers, QR secrets, API keys, operator PIN, network addresses, serial identities, queue names, full traceback or private data in operator-facing diagnostic export.
- Health during AR-09 Recovery, if retained as an exception, must remain a **separate audited recovery path** and not provide unguarded access to the Settings tabs.

## 4. Settings tab: Audio Settings

### 4.1 Owner-requested controls and accepted additional improvement

Implement at least the user's exact three categories **Music**, **Button SFX**, **Other SFX**; also include the recommended **Master Volume**, **Mute** and **Test Sound**. Suggested slider range: **0–100%**, clamp before touching audio handles. Defaults and step size are configuration/UI choices to validate; illustrative mockups (e.g. 85/65/80/70%) are **not required production defaults**.

| Control | Coverage | Rules |
| --- | --- | --- |
| Master Volume | Overall configured sound level for the app | Gain multiplier over each bus, not an undocumented OS speaker-volume change |
| Music / BGM | Normal GUI landing, tutorial, template, checkout, photo BGM and separate Meong Fly music loop | Keep one existing audio owner, preserve page-specific loop changes; do not restart a track on every slider drag |
| Button SFX | Touch/click/CTA confirmation sounds | Independent from other effects and governed by existing one-cue-per-action guard |
| Other SFX | Camera shutter, countdown, notifications, success/failure, Meong Fly effects | One initial bus; an independent **Game SFX** slider is a later optional extension, not a fourth mandatory category |
| Mute | Effective complete app audio silence with reversible previous sliders | Do not erase underlying volume preferences; restoring mute should not restart ads/game soundtrack incorrectly |
| Test Sound | Bounded preview for a selected bus | Preview sound runs through the normal audio owner and effects limiter, does not simulate a real shutter/charge or create overlapping sounds |

Suggested gain mapping: `effective_bus_gain = clamp(master,0,1) * clamp(bus,0,1)`; honor native per-sound source level and clipping limits. Keep output decoupled from legacy global volume; preserve error behavior when a provider/asset is unavailable. Restore correct BGM when navigating between ads, game and main photo flow.

**Existing source:** `photobooth/kiosk_v2/audio.py` (`PortraitAudio`, `music_gain`, `effects_gain`, `cue`, `set_music_gain`), `game_music.py`, `mixer.py` and the original advertisement player in `app.py`. Existing video ads own their audio separately; do **not** crudely apply a second gain/playback owner or resurrect the Windows intermittent mute/SDL channel issue. Define explicitly whether master controls the ad player's own sound without altering its ownership. Retain the established behavior: still ads use GUI BGM, video ads own their audio, game uses its own distinct loop, GUI shares its own BGM and button cues.

**Persistence:** save operator audio preferences atomically in a **per-booth local config**, not customer session state or source-controlled `.env` secrets. Settings must survive restart and be independent across booths; apply once at startup and on change with debounced writes or deliberate Save/Apply (choose and document). Include schema/version/defaults/clamping/corrupt-file fallback; no cloud dependency. Confirm values for Windows used mini-PC, Ubuntu target and planned tablet Android variant separately. On minimize/close suspend callbacks; when ads resume, use current saved volumes.

**Accessibility/operability:** show numerical % labels, accessible touch targets on both portrait sizes, bounded sliders, mute indication, test sound that cannot cause an endless loop. Avoid a separate full app reboot just to apply simple audio changes.

## 5. Settings tab: Emulate Ticket (exact approved name)

### 5.1 Scope and exact structure

The old names **Ticket Master**, **Print Ticket Master**, **Demo Ticket Generator** are historical aliases only. The visible GUI tab/header must say **Emulate Ticket**. It has two categories:

- **Merchant Promo — DEMO**: static QR stands in for a hypothetical merchant/POS receipt to test QR scanning, amount/eligibility and promotional decision.
- **Meong Fly Entry — DEMO**: static QR opens **one attempt in the currently active customer visit/session**, preserving the original mini-game flow/reward/consume semantics.

Recommended tab structure: a two-category selector, a **Testing Scenario** selector, a legible QR preview plus type/status label, clear "DEMO / NOT PAYMENT" watermark, Print ticket action (thermal), result/error feedback and **Ticket History / Test History** (can be an expandable subsection in the same tab, not a fourth Settings tab). Use the existing POS80/80-mm-class thermal printer through shared configuration/transport, and the existing QR renderer where compatible. A simple print preview must work without physical printer, with clear physical-test gating.

The user initially said "master ticket for simulating merchant validation or chance to play Meong Fly"; this is **not** a universal permanent master credential. Two distinct DEMO payload namespaces, clear type tags, a finite predefined preset library and explicit mode checks prevent privilege and type confusion.

### 5.2 Static development identity and replay rules

**Definitive correction to earlier unique-on-each-print/single-use-token suggestions:** In DEVELOPMENT, each chosen **valid static test preset** yields the **same QR payload on every preview and every subsequent print** (and normally across application restarts), deliberately allowing repetitive scanner tests without minting new QR IDs. The payload's identity should be versioned/booth-aware and controlled; its static contents must not contain real merchant credentials or production payment authorities. Printable ticket serial/tracing metadata may be included only if it does not change the actual static QR payload.

**Separate identity from entitlement:**

- A **Meong Fly static QR may be reused in a new, distinct test visit**, but **only one attempt may be admitted/consumed in the same visit**. Scanning it twice in that visit must reject, even after navigation/restart/recovery of that same visit. Do not "reset the ledger" on each scan or on app relaunch.
- Existing `DemoGameStore` and original game renderer/flow govern actual game attempts. The existing `DEMO-` code path is one-use in its original semantics; provide a distinct, explicitly gated reusable static fixture mode/admission adapter rather than weakening global anti-replay. A successful claim must be **atomically bound** to a stable customer/test-visit ID and persisted so restart does not create a second attempt for that visit. Distinct visit/session B receives its own entitlement only in MOCK/DEMO according to the test contract.
- A merchant promo static QR may be scanned in another test visit, with **once-per-visit promotional application**; no two base-fee waivers from repeated scans in the same checkout. A test promotion is **not payment authority** and must never alter a real Midtrans amount without separately approved server-side quote/redemption authority.
- Repeated Print does not itself consume a ticket; only the scanner's durable, verified admission/claim operation changes the test ledger.
- A stale callback after new visit, failed scan or wrong QR category cannot issue a claim, discount or game start.

### 5.3 Presets (minimum required)

| Category | Preset label | Static QR / test behavior | Expected result |
| --- | --- | --- | --- |
| Merchant Promo | **Eligible Promo — valid purchase scenario** | Valid DEMO merchant identity with example amount above a **configurable illustrative threshold** | Eligible in MOCK/DEMO; one permitted promotional effect for current visit |
| Merchant Promo | **Not Eligible — minimum spend not met** | Valid DEMO QR with amount under threshold | Valid ticket syntax, ineligible promotion; no price reduction |
| Merchant Promo | **Invalid Ticket — validation fails** | Deliberate invalid/wrong-type/unknown-version controlled fixture | Reject with neutral feedback; no discount |
| Meong Fly | **Valid Entry — unlock one attempt** | Valid static DEMO game entry QR | Exactly one game attempt when no prior attempt exists this visit |
| Meong Fly | **Already Used in Current Session — should reject** | **Reuse the same previously accepted valid QR** after consuming it | Reject duplicate by persisted ledger; **do not fabricate a distinct QR containing 'USED'** |
| Meong Fly | **Invalid Entry — validation fails** | Wrong type/tampered/unsupported fixture | Reject; no game entry, no discount |

For Merchant Promo, historical illustrative campaign: **Rp50,000** food purchase may waive **one Rp5,000 base/template fee**, never print fees, with separately verified merchant terms. This is a **test scenario, not an approved production discount threshold/merchant contract**. The Meong Fly mini-game's historical **Rp2,500 win reward** applies only in the existing trusted local MOCK test flow; a loss yields no reward and there is no "MAIN LAGI" for the same visit. Game result continues to **Template**, not back into ticket payment logic. The existing main GUI and original Meong Fly assets/physics should be reused, not rebuilt.

**Promo stacking:** accepted initial recommendation is **do not stack Merchant Promo and Meong Fly discounts** during development, to keep quote tests easy to audit. Establish a deterministic explicit policy: choose one eligible promotion according to an agreed precedence/validation flow, otherwise require operator-selected test scenario; never silently sum discounts or allow negative amounts. This is a provisional business rule to preserve, and changes to production promotion stacking require a separate owner-approved pricing/settlement contract.

### 5.4 QR namespaces and what must never interchange

| QR/printed object | Primary purpose | Who scans/consumes | Authority boundary |
| --- | --- | --- | --- |
| **Operator Login QR** | Static booth-bound Settings access | Operator scanner in Advertising | Secret credential; never a customer ticket |
| **Merchant Promo — DEMO QR** | Simulated receipt/discount eligibility | Merchant receipt scanner (future GUI integration); controlled MOCK tests now | No live merchant or Midtrans authority |
| **Meong Fly Entry — DEMO QR** | Simulated single game entry per visit | Game receipt scanner (future GUI integration); existing manual DEMO path currently | Test-only; not live production entitlement |
| **Recovery Ticket QR** | Original customer's interrupted-payment/photo-session proof | Customer recovery scanner | Unique private high-entropy capability, never static, not a payment result |
| **QRIS Payment QR** | Provider checkout | Customer's bank/e-wallet / Sandbox simulator | Same active provider order; payment verified server-side |
| **QRIS Payment Slip** | Optional paper copy of active payment QR | Customer scans printed paper | Separate planned GUI v2 checkout feature; never confirms payment |
| **Google Drive Photo Download QR** | Link to customer photo folder | Customer phone | Must follow verified folder accessibility/retention; not claim authority |
| **Support/Service Ticket QR** | Possible future exception/compensation tracking | Support workflow after design approval | Future proposal only; not implemented or equal to recovery proof |

All scan entrypoints MUST reject foreign namespaces (even if payload is a valid QR). **Never use one universal “accept any QR and guess its function” decoder**. QR selection controls what is accepted; role separation belongs in backend/business validation too, not only UI labels. All QR shown/printed must remain **unmirrored** and readable; only the live camera **preview** is mirrored.

### 5.5 Print and device behavior

- Emulate Ticket preview may use a software QR renderer and show the selected static payload consistently with the printed pixels. Select type/preset, show status, then press **PRINT DEMO TICKET**; do not auto-print just by opening Settings, selecting preset or scanning.
- Reuse existing native/ESC-POS printer configuration (LAN preferred, Wi-Fi next, USB/Windows queue where supported). Do not reimplement printer transport for a DEMO ticket or mutate customer photo-print settings without permission.
- Respect physical paper width, quiet zone, QR contrast; separate demo ticket graphics from three-photo customer strip and from live QRIS payment slip. Print a visually unmistakable **DEMO / NOT VALID FOR PAYMENT** legend; do not make printed operator credentials or recovery secret from this tab.
- Protect rapid taps, offline printer, disabled printer, uncertain after-send, app crash during spool, old/stale result and cancellation. **A socket/spooler SEND ACK is not proof that paper printed.** Maintain a durable attempt identity/status; do not auto-replay a print whose outcome is uncertain. Provide a deliberate operator inspection/retry decision only after an accurate state check and bounded safe policy.
- **Current Midtrans Sandbox invariant:** dedicated Sandbox v2 launch mode forces photo printer and Drive **OFF**. Do **not** silently bypass that by adding Emulate Ticket printing to the Sandbox process or by enabling live payment-slip printing. Controlled local MOCK/DEMO isolated printer opt-in is a separately scoped, testable path; never attach it to real provider state without separate owner approval.
- Offer honest **PREVIEW ONLY**, **PRINTER NOT CONFIGURED**, **SENT / NOT PHYSICALLY VERIFIED**, **UNCERTAIN — CHECK PAPER** messages, not unconditional “printed successfully.”

### 5.6 History, persistence and cleanup

Recommended history is a **lightweight test-event ledger**, not a collection of raw secrets:

- Store selected QR *type*, *preset ID*, version, test-visit ID (pseudonymous), booth ID, generate/preview time, print-attempt ID/status/timestamps, scan verdict, consumption event and rejection reason code. Avoid customer photos, raw QR operator/recovery tokens, full merchant receipts and API keys.
- Distinguish **print count** from **redeemed count**; a static QR is reprinted many times but its permitted game/promo use is scoped by test session.
- Refresh/print/test actions must not block QRIS recovery and photo workers. Avoid uncontrolled SQLite writes per camera frame; persist only bounded accepted/rejected events and rate-limit noisy invalid scan records.
- Reuse existing SQLite durable ledger/transaction semantics where safe; schema migration needs rollback/readability tests and must not reset consumed one-use entries. Define bounded retention/cleanup of expired DEMO test sessions; **never delete payment/fulfillment ledgers or real photos** as part of test-ticket cleanup.
- If a customer visit is explicitly ended and truly new visit B starts, static QR remains valid for B under MOCK/DEMO test policy; if the visit is only temporarily hidden/restored/recovered, preserve A's existing consumed state.

---

## 6. Operator access, security, billing and privacy invariants

1. **Advertising + SAFE_IDLE is required even after a valid operator QR**; proof alone cannot preempt a customer. Fail closed on inconsistent or unknown state.
2. Operator static QR is a **bearer secret**, vulnerable to photography/replay if leaked. Use high entropy, per-booth binding, local hashed verifier, rotation, non-public handling and basic failed attempts throttle. Future dynamic design remains recorded.
3. Device Health diagnostic export is allowlisted and non-sensitive; no images/log credentials or automatic upload.
4. Settings may not make, replay, refund, cancel, resolve, edit or overwrite a financial order; AR-09 PIN/fences and AR-06 customer capability stay separate.
5. DEMO tickets are accepted only in an explicitly **local MOCK/DEMO** namespace; **production backend rejects** all static DEMO payloads regardless of GUI appearance. Isolated Sandbox can test static fixture decoding but must **not** grant real provider discount or undo printer-off constraints.
6. **One game opportunity per visit** survives UI reconstruction and restart; no direct “PLAY AGAIN”. The original game is reused; win/loss result proceeds to Template.
7. **One promo effect per visit** and initial **no stacking** with Meong Fly reward. Payment amounts from server-authorized backend, not GUI-calculated DEMO payloads for merchant Sandbox/production.
8. Only one camera handle/owner; preview mirroring does not alter QR data. Scan decoding limited frequency, cancellation/timeout and privacy generation fencing.
9. Only one active audio owner for main GUI; video ads maintain their existing sound lifecycle; no competing test-sound playback provider.
10. Physical printing is evidence-bounded, no automatic retry after uncertain send. Printer/Drive/payment Sandbox guards remain intact.
11. Settings must work offline when its local booth credential/config and camera are healthy; real merchant checks may remain unavailable.
12. Password/PIN for the **separate financial AR-09 operator path** must never be placed in QR operator token, kiosk child process env, support ticket, demo ticket or source-controlled records.
13. Never expose operator login or test tickets in shared Drive advertisement/template folders. Per-booth printer/scanner/login config must not overwrite global content.
14. The emergency OS maintenance path must be auditable and inaccessible to casual customers; it does not convey production admin authority or change any payment.
15. Test only on **the correct hardware:** desktop development on Windows, fixed kiosk on used mini-PC/Ubuntu as planned, and mobile fully on tablet/Android in its future separately accepted build. The camera-facing-phone ergonomics and permission lifecycle on tablets need explicit device QA.

## 7. UX and visual copy — proposal refined in implementation

- Secret entry surface: existing Meong header long-hold / F12, not a visible customer Settings button.
- Login: **"OPERATOR LOGIN"**, **"Arahkan QR operator ke kamera"**, clear cancel/back; mask or generic error **"QR tidak dikenali / QR tidak berlaku untuk booth ini"** without revealing credential content; timeout returns to advertising.
- Authenticated header: **"MEONG SETTINGS"**; three tabs only: **"Device Health"**, **"Audio Settings"**, **"Emulate Ticket"**. Include Booth ID, app version and local/sandbox mode in footer.
- Audio labels: **Master Volume**, **Background Music**, **Button SFX**, **Other SFX**, **Mute**, **Test Sound**; show percentages and optional Save/Apply.
- Emulate Ticket sections: **Merchant Promo — DEMO** and **Meong Fly Entry — DEMO**; headings **Testing Scenario**, **Preview QR**, **Print Demo Ticket**, **Test History**. Distinct *Eligible*, *Ineligible*, *Invalid*, *Valid Entry*, *Already Used This Session* states with actual expected verdicts.
- Always visibly state **"DEMO — FOR TESTING ONLY"** on simulated merchant/game tickets and prints; not a payment receipt, customer recovery ticket or real discount.
- Preserve the approved pixel-art/cosmic Meong visual identity without recreating the game. Portrait reference sizes **800 × 1280** and **452 × 900**; support touch sizes, labels, scroll containment, landscape/compact behavior where applicable. No dedicated mandatory new GUI theme.

## 8. Implementation/risk checklist and phased evolution

Risk order: **P0** financial/privacy SAFE_IDLE, operator credential leakage/role confusion, one-visit game/promo ledger, QR namespace and production DEMO rejection, uncertain print/no replay; **P1** camera/sensor lifecycle, audio channel separation/persistence, Device Health no-hang, kiosk resize and worker concurrency; **P2** richer diagnostics, optional Game SFX slider, ticket history export, extra invalid cases, admin provisioning UI, long-term role/dynamic QR.

Proposed implementation sequence **after AR-00–AR-13**:

1. Source audit/decision consistency and isolated contracts/testing fixtures; do not change existing AR code under active development.
2. SAFE_IDLE + secret entry routing to Login (with AR-09 Recovery exception preserved).
3. Per-booth static QR provisioning/hash/rotation, read-only camera live scanner, session logout/timeout/privacy.
4. Three-tab Settings shell and full Device Health reuse, report/copy convenience.
5. Persistent four-control audio mixer + mute/test and full audio lifecycle regression.
6. Static-demo QR fixture definitions, Merchant Promo/Meong Fly scenario engine, durable per-visit ledgers and no-stacking/mock-mode fences.
7. Preview/printing via existing thermal infrastructure + attempt/uncertainty tracking + test history, without bypassing Sandbox.
8. Comprehensive privacy/device/Windows/Ubuntu/tablet acceptance and independent owner go/no-go.

This is expanded into small individually testable **OPS-00–OPS-10** phases in [IMPLEMENTATION-ROADMAP.md](IMPLEMENTATION-ROADMAP.md), with cases in [ACCEPTANCE-MATRIX.md](ACCEPTANCE-MATRIX.md). Separate **operational-phase future migration** (not part of this sprint): dynamic operator QR/roles, genuine merchant receipts with external validation and one-use anti-replay, unique real game tickets/receipt claims, production purchase/promo ledger/settlement, monitored multi-booth provisioning, secure phone admin, real hardware release acceptance.

### Mandatory development process

Before code, inspect branch HEAD, real source, [repository instructions](../../../AGENTS.md), relevant AR checkpoint, current feature status, status/decision/conflict history, and each linked contract. Do NOT assume a mockup equals code. Make focused tests and **small reviewed commits/pushes after each safe meaningful micro-increment**, verify remote HEAD; record actual SHA, test counts, backend/hardware/provider NOT_RUN status and next Codex step to survive a **five-hour ChatGPT/Codex session limit**. Never reset customer journals or spend all progress in an unpushed local branch. Preserve safe rollback.

**Publication of this specification does not change implementation status: every OPS test is NOT_RUN and no operator Settings/QR login/Emulate Ticket runtime is implemented by these documentation commits.**
