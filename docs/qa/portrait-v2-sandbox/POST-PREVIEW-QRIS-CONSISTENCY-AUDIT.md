# Post-preview QRIS — documentation consistency reconciliation

**Review date:** 1 November 2026. **Target branch:** `feature/post-preview-qris-checkout`. **Starting audit HEAD:** `b72f89cffa2363e8fcb8557f24649780e19b9793`.  
**Historical audit outcome (before later refund-first decision):** owner-approved safety/flow contradictions were reconciled **in Markdown only**. No source/code test, merchant action, printer, cloud deletion or deployment was performed. At that earlier checkpoint **84 PP scenarios were documented, all NOT_RUN**, and AR-13 CONDITIONAL. **LATEST owner update:** refund-first/lost-proof policy added **28 additional PP cases (PP-085..112), all NOT_RUN**, and new RF-D01–26 plus full decision ledger. The historical K01–20 audit below is retained without rewriting its dates or counts. Legacy PAID-before-camera rights and parent branch stay unchanged.

**Review method:** Compare original 24 owner decisions/11 Mermaid flows with AR-00–13, UAH-001–050, Midtrans provider research, existing dedicated Sandbox, BUG-026/027/028, UX-07 readiness/paid printer, Drive folder layout, README/AGENTS/development protocol, current branch/HEAD and all changed Markdown references. Match conflicts to new acceptance tests rather than recycling historical CI success.

## Subsequent owner correction — mandatory concurrent screen and paper ticket (new-order only)

On 1 November 2026, after the 20-finding contradiction audit, the owner **changed** the ticket policy for new post-preview orders: **ALWAYS display the original Recovery Ticket QR/full code in a visible 30-second + NEXT screen while concurrently dispatching exactly one paper ticket of that same original credential**, regardless of printer success. Historical printer-failure-only fallback and healthy-printer 'no screen' conclusions apply only to legacy paid-first source/UAH. The 84 acceptance scenarios were updated (especially PP-041/042/051/079/080), remain NOT_RUN, and no source/device changes occurred. Ticket transport SUBMITTED still is not proof paper was received.

## A. Findings addressed by source-of-truth documents

| Finding | Severity | Original contradiction | Documentation correction | Closure status |
| --- | --- | --- | --- | --- |
| K01 | P0 | Master Flow A always sent terminal unpaid to Ads, while Flow D allowed QR2/3 | Flow A separates expired continuing visitor, cancelled/abandoned terminal and safe-release ACK | **DOCUMENTED**, PP-073 NOT_RUN |
| K02 | P0 | Customer cancellation could re-enter QR renewal if still present | Durable USER_CANCEL/abandoned_intent blocks any further QR; verified expiry only | **DOCUMENTED**, PP-074 NOT_RUN |
| K03 | P0 | AGENTS unconditional original AR first vs PP branch-specific roadmap | On PP branch PP-00..07 is intended workstream with AR/UAH safety regression gates; parent branch retains AR sequence | **DOCUMENTED** |
| K04 | P0 | Legacy network-independent/download-pending paper contradicted verified URL before paid strips | Storage explicitly versions legacy offline printing vs new purchased verified-URL gate | **DOCUMENTED**, PP-053/081 NOT_RUN |
| K05 | P0 | Legacy Sandbox Drive OFF cannot satisfy new purchased paid-strip QR contract | Separate **synthetic purchased verified-link** profile required; legacy BUG-027/028 unchanged | **DOCUMENTED**, PP-082 NOT_RUN |
| K06 | P0 | Internal idempotency key mistaken for guaranteed Midtrans Legacy header | Midtrans research preserves header uncertainty; same-order reconciliation, no unsupported retry-POST | **DOCUMENTED**, PP-083 NOT_RUN |
| K07 | P0 | Cancel, minimize, inactivity and departure shared a single event/financial action | Flow E and security matrix give independent intents, privacy and provider authority | **DOCUMENTED**, PP-074..076 NOT_RUN |
| K08 | P0 | Reboot could admit next visitor immediately after provider terminal unpaid | Flow J requires exact private-media worker drain, fence, receipt, backend ACK and verified FREE | **DOCUMENTED**, PP-077 NOT_RUN |
| K09 | P0 | Reboot Drive-upload retry automatically proceeded to Ads despite unknown paper/OWED work | Flow J independently classifies all paid print/upload/occupancy obligations | **DOCUMENTED**, PP-078 NOT_RUN |
| K10 | P1 | Ticket receipt SUBMITTED/UNCERTAIN/presentation states conflated | Separate original receipt transport and actual customer-offer states, no polling/reboot redisplay | **DOCUMENTED**, PP-079 NOT_RUN |
| K11 | P1 | Happy path misleadingly required original customer to rescan CCP | Live original lease skips CCP rescan; retired claimant must present authentic proof | **DOCUMENTED**, PP-080 NOT_RUN |
| K12 | P0 | UAH memory-only ticket prohibition vs owner-approved encrypted escrow | Ordinary plaintext still prohibited, narrowly scoped OS-protected **ciphertext-only** vault exception and original token only | **DOCUMENTED**, PP-043..046 NOT_RUN |
| K13 | P0 | Late-payment CCP claimed operational before vault/fencing integration existed | Move vault interface/secure CCP **before** payment claim integration; PP-03..PP-06 exit criteria distinct | **DOCUMENTED**, PP-033..046 NOT_RUN |
| K14 | P1 | Drive URL required before checkout even though customer folder only binds after PAID | Precharge **health/sharing/READY pool capacity** check without consuming; after PAID exact folder bind and verified URL gate | **DOCUMENTED**, PP-019/081 NOT_RUN |
| K15 | P1 | Legacy 24h ticket, new CCP, original QR attempts, unpaid staging and 15d/30d retention shared ambiguous time anchors | Explicit versioned timestamps/expiry and nonreset rules; numeric CCP TTL/new paid retention anchor still **requires engineering/policy validation** | **SPECIFIED / CALIBRATION OPEN**, PP-084 NOT_RUN |
| K16 | P1 | Root README and development protocol pointed only to parent branch | Versioned implemented-parent vs documentation-only PP branch entry and instructions | **DOCUMENTED** |
| K17 | P1 | Old architecture blanket Sandbox printer OFF conflicted with BUG-027 real scoped trial | Historical source-era snapshot labeled; dedicated paid-first Sandbox receipt/photo print + Drive OFF distinguished | **DOCUMENTED**, PP-082 NOT_RUN |
| K18 | P1 | Existing GUI supports 1..9 copies, backend quotes may accept 10 | Keep discrepancy explicit in Codex source seam; no unilateral code/price change; **needs implementation decision/testing** | **IMPLEMENTATION OPEN**, PP-004/020 NOT_RUN |
| K19 | P2 | Multiple nearly identical owner-approved banners obscured priority | Consolidated first-page scope notes, retained all dated source/CI history | **DOCUMENTED** |
| K20 | P2 | Risk register referenced nonexistent PP-PRIV and PP-OWED test groups | Mapped to existing PP-HAND/CRASH and PP-PRINT/DRIVE; added distinct contradiction cases | **DOCUMENTED** |

**Meaning of DOCUMENTED:** a written contract/diagram conflict has been reconciled. It does **not** mean application behavior or tests have passed. K15 and K18 are not silently declared solved at runtime: they remain explicitly open calibration/implementation gates.

## B. Canonical hierarchy and branch boundaries

1. **New-order product truth:** [owner-approved 24 decisions and 11 revised diagrams](POST-PREVIEW-QRIS-OWNER-APPROVED.md).
2. **Safe implementation truth:** [new state/credential/provider/retention guards](POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md) plus existing AR/UAH nonnegotiable protections.
3. **Executable acceptance truth once developed:** [PP-001..084, all NOT_RUN](POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md), with old AR/UAH CI as historical baseline only.
4. **Work order once separately authorized:** [PP-00..07 handover](POST-PREVIEW-QRIS-CODEX-HANDOVER.md). Parent `feature/portrait-kiosk-v2-next` retains the original AR priority; do not switch branches, weaken old PAID photo recovery, or touch master.

**Important preserved distinctions:** provider expired is not customer cancel; public Advertising is not FREE occupancy; CCP before PAID is not a Recovery Ticket/charge proof; receipt SUBMITTED is not paper physically delivered; compose is not completed paid service; precharge READY capacity is not a paid customer folder/link; provider Legacy API idempotency guarantee is not implied by local keys; encrypted vault is not a plaintext secret or a new ticket issuance; local/photo cloud retention is not equivalent to payment/claim expiry.

## C. Documentation QA record

- 24 unique PP-D01..24 decisions retained; 11 Mermaid diagrams use matching opening/closing fences.
- 84 unique PP-001..084 scenarios retained with no missing number; all **NOT_RUN**.
- 30 Markdown paths changed relative to initial audit head before adding this record (including four core PP documents and branch-specific historical contracts); no source/code file change in that comparison.
- All checked relative Markdown file/directory paths resolve in the repository tree. Existing historical links/CI records were not reinterpreted as new runtime PASS.
- **Not performed:** Mermaid renderer/visual screenshot QA, native GUI/device/protocol tests, billing, Drive live sharing/retention/deletion, vault provisioning, CI execution or master merge.

## D. Follow-on engineering gates — intentionally not auto-approved

- Confirm exact merchant-specific Midtrans Legacy retry, create-uncertain, cancellation/expiry, refund policy and production eligibility; never invent provider behavior.
- Confirm durable CCP delivery UX and proof-of-offer, token lifetime and vault access controls on Windows and intended Ubuntu; Android later by separate authorization.
- Calibrate true inactivity thresholds and check no arbitrary active-session hard cap; decide paid-retention time anchors and CCP/ticket expiry by version while respecting existing local/Drive retention and PAID/OWED.
- Reconcile 1..9 GUI versus backend 1..10 allowed print copies at the frozen server quote boundary.
- Verify physical POS80 paper/ticket/strip outputs and partial/corrupt print evidence, actual Google Drive ownership/sharing and stale callback fencing; no blind automatic replay.
- Only mark PP test PASS with source SHA and real fixture/device evidence, then review AR/UAH regression and AR-13 customer/merchant release separately.

## E. Later comprehensive refund-first + lost-proof reconciliation (new decisions, no source change)

**Owner explicitly approved both**: (a) favor provider-authorized **automatic full refund** when paid service has genuinely and irrecoverably failed, plus refund only exact verified **excess** duplicated settled charge, and (b) **no automatic refund solely because a customer lost genuinely offered CCP/Recovery Ticket**; no tokenless photo unlocking. **These are compatible** because customer negligence and Meong failure are independent evidence dimensions. Customer wants the money not returned on proof loss alone, **not** a legally absolute standard clause forfeiting every possible complaint. Indonesia UU 8/1999 Pasal 18/19 requires review of ToS and proof of consumer fault. This new targeted policy **supersedes unconditional no-auto-refund as a future new-order design only**. Historical paid-first source still has no refund issuance. [Full policy](POST-PREVIEW-QRIS-REFUND-AND-LOST-PROOF-POLICY.md) · [42-area all-decisions ledger](POST-PREVIEW-QRIS-COMPLETE-DECISION-LEDGER.md) · [operator matrix](POST-PREVIEW-QRIS-OPERATOR-AND-REFUND-ESCALATION.md).

| Additional cross-document risk | Contradiction resolved | Exact new-order contract / test anchor |
| --- | --- | --- |
| K21 New owner wants refund-first vs old UAH-D18 blanket no-auto-refund | **Version distinction:** new PP merchant-failure eligible future auto refund; old paid-first UAH remains historical/current code only | RF-D01/26; PP-092/093 |
| K22 Owner says "uang hangus" when CCP/ticket lost vs law/PAID/OWED | No **automatic** refund for genuinely lost proof *alone*, no protected photo disclosure; separate service failure and lawful complaint rights preserved | RF-D05–08/25; PP-085..090/112 |
| K23 Recovery-ticket fallback-only vs latest mandatory screen | First genuine live PAID ticket screen **always** 30 visible seconds + NEXT while **same original ticket prints once concurrently**; printer SUBMITTED never skips UI | RF-D09; PP-041/042/051/079/080 |
| K24 Printer SENDING/UNCERTAIN vs full automatic refund for every failure | Uncertain paper must be physically/evidentially classified; no blind reprint/refund; bounded provider-verified irrecoverable service only | RF-D18/19; PP-095/096/108 |
| K25 Lost proof + separate genuine paid print/Drive failure | Classify merchant failure independently; cannot refuse remedy on proof-loss ground | RF-D06–08; PP-089/093 |
| K26 General Midtrans QRIS refund docs vs GoPay QRIS POS default disabled | Merchant-specific Refund API activation/eligible original transaction still NOT VERIFIED; unprovided API -> REVIEW not fake refund | RF-D14/15; PP-100..102 |
| K27 Refund request accepted vs customer money received | Distinct durable original intent/key, requested, processing, provider-confirmed, customer balance visibility; no second POST on timeout | RF-D16/17; PP-104..106 |
| K28 Two QRIS attempts PAID vs one entitlement | One original paid service; refund only the exact unambiguous excess attempt; never double charge/service | RF-D04; PP-097/098/111 |
| K29 Full service refund vs duplicate-excess refund worker fencing | Full irrecoverable-service refund fences its owed service; **excess-only refund preserves the rightful single paid print/Drive service** | RF-D18; PP-097/107/108 |
| K30 Financial refund vs machine SAFE/FREE | Refund success does not cure printer/camera lease, paper queue, isolation/fence ACK or private-photo hazard | RF-D19; PP-109 |
| K31 Token generated or printer SUBMITTED vs real customer opportunity | Keep proof-offered/QR-visible journal; never-presented proof is Meong failure, not lost-by-customer | RF-D07/21; PP-087/088 |
| K32 Codex post-preview PP-00..07 vs new refund dependency | PP-06R refund stage follows verified PP-05 fulfillment and PP-06 owner/worker release; no live merchant action without separate go-live authorization | PP-085..112, PP-06R roadmap |

**Complete latest record:**
- 24 unchanged PP-D01..24 plus 26 owner refund/lost-proof RF-D01..26 and 42 topic rows in consolidated decision ledger; original AR/UAH/BUG/UX records retained historically.
- **112 PP-001..112 unique proposed new-flow test IDs**; every new PP test **NOT_RUN**. Real Midtrans POS refund activation/actual payout, legal acceptance, Windows/Ubuntu/POS80, live Drive, encrypted vault and privacy/hardware tests **NOT VERIFIED**.
- Existing original 11 master Mermaid charts plus refund/lost-proof, complete-decision and operator-exception supplemental charts. Only docs Markdown is changed; new project refund code and merchant financial actions **NOT IMPLEMENTED**.
- Customer-screen policy still **always original ticket screen plus concurrent original paper receipt**, not an error-only fallback.
- **Do not misread** this audit as runtime confirmation that all tests pass. Outstanding calibrations: account Refund API, old/new TTL and retention anchors, GUI 9 vs backend 10 copies, hardware uncertainty thresholds, merchant/legal ToS wording, abuse thresholds and refund-account settlement.

**Source-of-truth ordering:** [complete decisions](POST-PREVIEW-QRIS-COMPLETE-DECISION-LEDGER.md) -> [master PP](POST-PREVIEW-QRIS-OWNER-APPROVED.md) + [new refund specific](POST-PREVIEW-QRIS-REFUND-AND-LOST-PROOF-POLICY.md) -> [security states](POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md) -> [provider](MIDTRANS-PROVIDER-CONTRACT.md) -> [112 QA](POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md) -> [Codex stage PP-06R](POST-PREVIEW-QRIS-CODEX-HANDOVER.md). New target supersedes old wording **only for new post-preview orders**; never rewrite historical evidence or current legacy PAID -> camera code.
