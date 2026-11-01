# Post-preview QRIS — documentation consistency reconciliation

**Review date:** 1 November 2026. **Target branch:** `feature/post-preview-qris-checkout`. **Starting audit HEAD:** `b72f89cffa2363e8fcb8557f24649780e19b9793`.  
**Outcome:** Owner-approved product decisions preserved; cross-document contradictions corrected **in Markdown only**. **No Python/source change, code tests, real Midtrans, printer, Drive, vault, cloud deletion or deployment performed.** New-order workflow remains **NOT IMPLEMENTED**, all **84 new PP cases NOT_RUN**, AR-13 CONDITIONAL. Legacy PAID-before-camera rights and parent branch stay unchanged.

**Review method:** Compare original 24 owner decisions/11 Mermaid flows with AR-00–13, UAH-001–050, Midtrans provider research, existing dedicated Sandbox, BUG-026/027/028, UX-07 readiness/paid printer, Drive folder layout, README/AGENTS/development protocol, current branch/HEAD and all changed Markdown references. Match conflicts to new acceptance tests rather than recycling historical CI success.

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
