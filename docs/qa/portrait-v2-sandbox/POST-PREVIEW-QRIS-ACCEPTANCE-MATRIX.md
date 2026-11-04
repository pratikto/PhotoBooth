# Post-preview QRIS — acceptance and adversarial QA matrix

> **5 November final software simulation:** [executed full campaign and all 112 case classifications](PP07-END-TO-END-SIMULATION-2026-11-05.md), acbac15 / CI 41906929920: 1,744 all-opt-in local PASS; 546 Windows, 546 Ubuntu, 62 native PASS; no failures/errors/skips. Full provider/device/refund/legal acceptance remains separate; no owner UAT row is promoted.

> **2 November expanded cross-system simulation evidence:** [Broad J01–J20, native N21–N24 and actual process-death P01–P02 traceability](PP07-BROAD-SIMULATION-MATRIX-2026-11-02.md). At matching-source [CI #41407613830](https://github.com/pratikto/PhotoBooth/actions/runs/41407613830), J01–J20 each PASS on Windows and Ubuntu, with 520/520 per OS and existing Kivy 54/54. Latest native 4 new cases N21–N24 PASS in [CI #41409614158](https://github.com/pratikto/PhotoBooth/actions/runs/41409614158), 58/58 total; P01–P02 exact hard-exit + independent SQLite reopen awaiting [CI #41409982930](https://github.com/pratikto/PhotoBooth/actions/runs/41409982930), source `238012f7`. **These are regression subassertions, NOT full PP-001–112 acceptance**. No physical paper, actual merchant settlement/refund, cloud ACL/retention deletion or 26 physical owner UAT has been verified; keep all complete acceptance rows NOT_RUN at those scopes.

## 2 November 2026 — 20 integrated journey simulations instead of unit-test-count proxy

**Source and scope:** [J01–J20 comprehensive simulation design, code, exact failure-injection and acceptance mapping](PP07-BROAD-SIMULATION-MATRIX-2026-11-02.md). Source `tests/test_post_preview_journey_matrix.py` drives real local SQLite, authenticated test HTTP API, the original camera capture/compose services, multi-template quote, original ticket, paid Drive transaction/purchased strip staging, printer dispatcher and guarded A/B admission. CI entry registered on both Windows and Ubuntu; no merchant account/device network calls. These do **not** replace full 112 owner acceptance cases or the 26 actual Windows UAT observations.

**New security finding BUG-034:** A separate paid strip dispatcher could previously directly send design B when design A was `SENDING/UNCERTAIN`, bypassing the kiosk-level hold. Fixed `92717d25` with an atomic original-purchase-wide journal gate inside the dispatcher. J09/J10 verify a new direct dispatcher with a different PREPARED design and no printer I/O on unsafe original state.

**Observed tests:** First source `eb9bbecf` [CI #41407278546](https://github.com/pratikto/PhotoBooth/actions/runs/41407278546) ran J01–J20 with 18 PASS, 1 FAIL and 1 ERROR due two test setup/expectation issues (counting paid imported media as new camera captures, and not catching the precise original `CaptureRecoveryRequired`). Corrected in *test-only* `bd70593f`, retaining strict camera/import separation and hash-tamper rejection. New matching-source [CI #41407613830](https://github.com/pratikto/PhotoBooth/actions/runs/41407613830) has **20/20 J cases PASS on Ubuntu**, **520/520 backend** and **54/54 existing native Kivy PASS**; **Windows matching-source result remains pending** in this checkpoint. Never extend the Ubuntu result into a Windows PASS without logs.

**Next:** finish Windows evidence; add native 3-design 2+1+3 customer journey and Drive loss/recovery across GUI; pursue process-death/reopening print journal, A/B upload/worker races, game/discount integration, longer-term soak. Real merchant Midtrans, POS80 output, Drive public sharing/retention, refund I/O and production remain separate gates.

> **2 November further synthetic PP-029/030/065 subassertions:** The [PP-07 adversarial GUI record](PP07-ADVERSARIAL-GUI-FAULTS-2026-11-02.md) now covers a late PAID QR1 while QR2 is PENDING, followed by a separately observed excess QR2 settlement. Exactly one original entitlement and `OWED` must persist. A separate persisted SENDING printer crash-boundary model denies replay under a fresh dispatcher. These tests were **added**, but latest source `0548bc89` matching [CI #41404106134](https://github.com/pratikto/PhotoBooth/actions/runs/41404106134) is **VERIFIED 3/3 SUCCESS** with 494 Windows + 494 Ubuntu + 54 native (1,042 executions, zero failures/errors/skips); the earlier failed run remains documented as an incorrect test assertion about a deliberately omitted private QR. **Do not mark PP-029/030/065 complete** or extend automated PASS beyond source `c86a8e64` until exact-source execution finishes. All 112 full acceptance cases remain NOT_RUN at their comprehensive scope.

> **2 November P0 GUI adversarial subassertions:** [PP-07 fault-injection evidence](PP07-ADVERSARIAL-GUI-FAULTS-2026-11-02.md) maps new native tests to PP-024/025/026 (three original QRIS attempts and no QR4), PP-050/052/065/095 (uncertain first print blocks the next distinct design), with earlier original paid/no-replay obligations preserved. At source `c86a8e64`, native Kivy **53/53 PASS**, Ubuntu **493/493 PASS** and Windows **493/493 PASS**; matching-source [CI 41402925221](https://github.com/pratikto/PhotoBooth/actions/runs/41402925221) is **3/3 SUCCESS**. The later source `0548bc89` is separately verified with 494 Windows + 494 Ubuntu + 54 native PASS [CI 41404106134](https://github.com/pratikto/PhotoBooth/actions/runs/41404106134). These are **isolated automated subassertions**; **all 112 full acceptance scenarios remain NOT_RUN** at their required comprehensive scope. No real merchant payment, paper, Drive, refund or physical owner UAT was performed.

> **2 November 2026 evidence boundary:** The source-pinned [PP-07 automated simulation report](PP07-AUTOMATED-SIMULATION-2026-11-02.md) has real GitHub Actions executions of isolated backend tests and native Kivy synthetic checkout (including a one-order/two-template, 2+1 paper-copy fixture). These are **component/native subassertions**, not automatically individual PASS outcomes for PP-001..112. The canonical **112 full acceptance cases remain NOT_RUN** until separately executed and evidenced at the required device/provider/customer scope. The 26-case owner [Windows worksheet](PP07-SUPERVISED-WINDOWS-UAT.md) has separate NOT_RUN/BLOCKED status; no actual merchant charge/refund/paper/cloud success is established by mock tests. Latest-source CI [41393795509](https://github.com/pratikto/PhotoBooth/actions/runs/41393795509) is now independently verified **3/3 SUCCESS** (493 Windows + 493 Ubuntu + 51 native); this remains only synthetic/component evidence, not full 112-case acceptance.

**1 November 2026 | OWNER-APPROVED DESIGN | all 112 scenarios NOT_RUN.** This is a test specification, not an executed test report. Refer to [canonical decisions and 11 diagrams](POST-PREVIEW-QRIS-OWNER-APPROVED.md) and [security contract](POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md). Existing AR-00–13 and UAH evidence is historical, not new-flow acceptance.

## PP-CAP — capture/retake (10)
| ID | Scenario | Required outcome |
| --- | --- | --- |
| PP-001 | One template | 3 original slots, at most one retake |
| PP-002 | Two templates | 6 originals, independent retakes |
| PP-003 | Twelve templates | 36 originals, max 12 retakes |
| PP-004 | Multiple paper copies | No extra photo sessions |
| PP-005 | Crash during save | No duplicated or lost committed shot |
| PP-006 | Crash during retake | Correct selected slot and quota |
| PP-007 | Deselect/reselect template | Consumed retake does not reset |
| PP-008 | Camera disconnect/countdown race | No automatic shutter |
| PP-009 | Artwork updated mid-draft | Pinned version/hash or safe hold |
| PP-010 | Compose before payment | No print, paid completion or public upload |

## PP-FRZ/READY — preview, edit, frozen order (10)
| ID | Scenario | Required outcome |
| --- | --- | --- |
| PP-011 | Copy change before QRIS | Requote, no new captures |
| PP-012 | Add template before QRIS | New 3-photo session |
| PP-013 | Remove template before QRIS | Revised quote, private media remains safe |
| PP-014 | Edit after provider-create intent | Reject; same frozen cart |
| PP-015 | Preview download QR attempted unpaid | No accessible photo |
| PP-016 | Preview manifest corrupted | No charge |
| PP-017 | Camera/disk not ready before capture | No payment |
| PP-018 | Printer known unavailable pre-charge | No new charge |
| PP-019 | Drive API/sharing unavailable or READY reserve pool empty before charge | Hold checkout; do not require a bound customer URL pre-PAID |
| PP-020 | Server quote/artifact mismatch | Reject, preserve draft |

## PP-PAY/QR — provider reconciliation (12)
| ID | Scenario | Required outcome |
| --- | --- | --- |
| PP-021 | Lost POST response after provider created order | Same attempt, no duplicate |
| PP-022 | 404 during provider propagation | UNKNOWN, not unpaid |
| PP-023 | Duplicate/late webhook | Independently verify fresh provider state |
| PP-024 | QR1 verified expired, active customer | QR2 same frozen draft, no recapture |
| PP-025 | QR2 verified expired, active customer | QR3 same frozen draft |
| PP-026 | QR3 expired | No QR4, guarded close |
| PP-027 | Customer abandons PENDING | No automatic renewal; original cancel/reconcile |
| PP-028 | Cancel races settlement | Retain PAID/OWED |
| PP-029 | QR1 PAID while QR2 creating | One service; conflict ledger |
| PP-030 | QR2 and QR3 both settle | No double printing; financial review |
| PP-031 | Restart during CREATE_UNKNOWN | Original identity still authoritative |
| PP-032 | QR expires after customer departure | No automatic absent-customer renewal |

## PP-CLAIM/SEC — claims and original ticket (14)
| ID | Scenario | Required outcome |
| --- | --- | --- |
| PP-033 | Pre-PAID checkout-claim proof offered | Private, distinct, strong token/verifier |
| PP-034 | Claim proof used before PAID | Cannot show unpaid photos |
| PP-035 | Late PAID after customer goes | PAID_UNCLAIMED; no public print |
| PP-036 | Returning original proof with PAID/free booth | One original entitlement restored |
| PP-037 | Returning proof while visitor B active | WAIT/DEFER, B not preempted |
| PP-038 | Wrong booth, forged, expired claim | Deny private access |
| PP-039 | Replay/brute force attempts | Rate-limited, scoped, audited |
| PP-040 | Customer paid but claim proof never offered | Owed/remedy; no customer blame |
| PP-041 | Fresh PAID, original customer owns booth, printer healthy and acknowledges SUBMITTED | **Mandatory on-screen original QR + full code with 30s visible timer/NEXT** starts while **one same-token ticket receipt job is enqueued concurrently**, without waiting for ACK; successful printing MUST NOT skip or dismiss screen |
| PP-042 | Ticket printer unavailable, failed, timeout, delayed SUBMITTED or UNCERTAIN | **Same mandatory 30s ticket screen shown regardless of print outcome**; no reissue/auto-reprint, no timer reset on late printer callback, correct private cleanup on NEXT/zero |
| PP-043 | Crash after PAID before any genuine first ticket screen became visible / printer SENDING | Vault and owed policy; no public ticket on boot, no duplicate send; first lawful screen requires original customer proof and free booth |
| PP-044 | Crash after ticket SENDING | Never auto-reprint |
| PP-045 | Vault key/ciphertext missing | Fail closed, OWED retained |
| PP-046 | Operator/DEMO/QRIS/download QR as customer proof | Reject cross-type use |

## PP-PRINT/DRIVE — paid fulfillment (12)
| ID | Scenario | Required outcome |
| --- | --- | --- |
| PP-047 | Compose auto-print callback while unpaid | Block paid photo print |
| PP-048 | 3 designs with 2+1+3 copies | Six paid copies; only 9 captures |
| PP-049 | SUBMITTED but no paper physically emerged | Not recorded as physical delivery |
| PP-050 | Partial RAW bytes sent then timeout | UNCERTAIN, no replay |
| PP-051 | Ticket screen shown while thermal printer lane holds original receipt job; NEXT pressed before printer returns | Screen timer operates independently; serialized exclusive original receipt / photo-strip jobs, no lost job, overlapping raw sends or reprint |
| PP-052 | Design A printed, B uncertain | No A replay or blind B replay |
| PP-053 | Paid, Drive URL unverified | Hold strip, retain OWED |
| PP-054 | Verified Drive URL, upload pending | Real QR, honest upload status |
| PP-055 | Anonymous draft and 25 READY folders | No free folder claim/public upload |
| PP-056 | Cross-booth/foreign folder | Binding rejected |
| PP-057 | Crash during upload | Same checksum retry, no reprint |
| PP-058 | Last compose marks payment completed | Must remain pending paid obligations |

## PP-HAND/CRASH/GAME/LEGACY — unattended operation (14)
| ID | Scenario | Required outcome |
| --- | --- | --- |
| PP-059 | Unpaid draft abandoned, no QR attempt | Privacy fence, safe release |
| PP-060 | Customer actively capturing with slow worker | No hard inactivity cutoff |
| PP-061 | Inactive gallery/review/final preview | Warning, safe suspend |
| PP-062 | PENDING original checkout and new visitor | No unsafe new payment |
| PP-063 | Stale A callback during B session | Fenced; B unaffected |
| PP-064 | Crash during release/ACK lost | Retry exact operation, no broad reset |
| PP-065 | Reboot with printer SENDING | UNCERTAIN, no replay |
| PP-066 | Legacy PAID-first unfinished photo | Original capture recovery unchanged |
| PP-067 | Meong Fly consumed then unpaid abandon | No new game attempt |
| PP-068 | Untrusted game DEMO discount | No real discount without verified backend |
| PP-069 | Repeated unpaid visits filling disk | Safe resource control, no active hard cutoff |
| PP-070 | Valid proof when booth finally free | Fresh verification, original claim |
| PP-071 | New visitor arrives during old worker uncertainty | Neutral HOLD |
| PP-072 | Expired credential and paid liability | No illicit reveal, no erased OWED |

## PP-CONFLICT — cross-document contradiction regression (12, all NOT_RUN)

These tests are additional to PP-001..072. They specifically prevent the previously discovered policy/diagram contradictions from turning into unsafe runtime behavior.

| ID | Conflicting edge / failure injection | Required outcome |
| --- | --- | --- |
| PP-073 | QR1 verified expired unpaid while same customer requests continuation | QR2 via its own guarded provider create; master flow does **not** force Advertising |
| PP-074 | USER_CANCEL with verified cancelled/unpaid while customer remains in front of camera | Persist cancel intent and close safely; **never** QR2/QR3 |
| PP-075 | App minimized while live QRIS PENDING, no cancel action | Privacy fence only; do not invent financial cancellation or renewed order |
| PP-076 | Inactivity warning during valid camera countdown or ongoing write/compose | Active work not abandoned; retained original capture/retake quota |
| PP-077 | Restart after terminal unpaid but stale camera/file worker active | No new visitor before exact quiescence, fence and durable release ACK |
| PP-078 | Restart during paid authorized upload while a photo print is UNCERTAIN | Resume only idempotent upload; retain paid/print obligations; no blind print or unsafe release |
| PP-079 | Receipt SUBMITTED early while first mandatory 30s screen active, then polling/restart/returning claimant | First screen remains visible independent of SUBMITTED; when dismissed, never automatically re-display or reset countdown on provider/paper callback, polling, reboot or returning claim; preserve exact original presentation journal |
| PP-080 | Live paid owner has intact original booth lease, no CCP scan | Open **mandatory** original Recovery Ticket screen and dispatch **same ticket receipt** concurrently once; no extra claim/CCP step |
| PP-081 | Precharge sees healthy Drive and available unclaimed READY pool, but atomic customer folder binding/URL verification fails after PAID | No paid strip or invented QR; PAID/OWED retained; no unpaid READY consumption |
| PP-082 | Legacy Sandbox Drive OFF vs new purchased synthetic verified-link profile | Existing BUG-027/028 profile unchanged; isolated fake link never represented as real cloud evidence |
| PP-083 | Attempt-create timed out; provider Legacy /v2/charge idempotency-header behavior unknown | No unverified provider header or repeated POST; same original identity/status reconciliation |
| PP-084 | Draft/QR1/QR2/PAID/ticket timestamps across restart and expiry | Different versioned TTL and 15-day/30-day anchors; no silent extension, deletion or mixing legacy 24h Sandbox claim rule |

**Mapping check:** K01 privacy/ownership -> PP-HAND and PP-CRASH; K11 OWED/COMPOSED -> PP-PRINT and PP-DRIVE. `PP-PRIV` and `PP-OWED` are not standalone acceptance groups. All PP-001..112 remain NOT_RUN until newly implemented, executed and individually evidenced.

### Mandatory ticket-screen parallelism — subassertions of PP-041/042/043/051/079/080, all NOT_RUN

- **Screen always on healthy printer:** first fresh PAID opens original Recovery Ticket screen **even when printer acknowledges SUBMITTED immediately**. Assert the same original secret encoded in onscreen QR/full code and in receipt bytes; record both effects from one event.
- **True concurrency:** a deliberately slow/nonresponsive printer does **not** delay first visible QR or block the independent 30s countdown; the first single printer dispatch begins during screen visibility, not after NEXT/zero.
- **Timer starts on actual visibility:** QR/code must be fully legible at portrait kiosk sizes before countdown; screen closes once on NEXT or zero, with no reset from provider polling, printer ACK, stale callback or screen rebuild.
- **No repeat effects:** zero/early NEXT while receipt SENDING does not issue a new print or drop original in-flight journal; no RAW overlap with purchased strips. Never mint second Recovery Ticket.
- **No cross-customer disclosure:** PAID_UNCLAIMED and returning customer without verified original proof/lease must not trigger either the screen or receipt; boot does not show ticket; escrow does not authorize unsolicited screen.
- **Known printer unavailable:** mandatory screen still offered to the rightful customer, job outcome honestly NOT_SENT/FAILED without an automatic second send. Physical paper presence remains distinct from transport SUBMITTED.

**Historical UAH/BUG-027 test descriptions that require *no mandatory overlay on successful receipt* are legacy-version expectations and MUST NOT be used as acceptance assertions for the new post-preview route.** They remain unchanged as historical evidence until a separately authorized migration/change.

## PP-REFUND/PROOF — new owner refund-first and lost-proof regressions (28 scenarios, all NOT_RUN)

| ID | Simulated scenario / conflicting owner rule | Required outcome |
| --- | --- | --- |
| PP-085 | CCP genuinely visible/offered at first QRIS, later lost, original PAID service fully delivered | `NO_AUTO_REFUND_PROOF_LOST`; cannot self-restore old photos without valid capability; no blanket legal waiver |
| PP-086 | Mandatory 30-visible-second ticket with full QR/code + same concurrent paper ticket, customer discards both, no independent service failure | No automatic refund solely from customer-lost proof; no operator tokenless media unlock |
| PP-087 | First CCP never offered due prepay UI crash; original charge later independently PAID | Not labeled customer negligence; PAID/OWED and secure claim/remedy, no fake proof-presented evidence |
| PP-088 | After PAID printer SUBMITTED but mandatory Recovery Ticket screen never rendered/never visibly displayed | Printer ACK is not genuine screen offer; preserve claim/remedy, no customer-forfeiture |
| PP-089 | Customer lost genuinely offered ticket AND paid photo strips genuinely failed permanently | Do not refuse compensation on proof-loss ground; independently evaluate merchant service failure and refund |
| PP-090 | Customer disappears after PAID; valid CCP exists; claim window/onscreen screen timer expires | No automatic refund merely on absence/expiry; retain paid/owed, lawful remedy and original claim rules |
| PP-091 | Recovery-ticket receipt printer broken but same original 30s screen displayed, purchased photo strips can still be safely fulfilled | Do not auto-refund solely because paper ticket failed; still permit genuine service |
| PP-092 | PAID original order, printer failed irrecoverably after bounded retry, worker safely fenced, provider refund enabled | Refund-first full original amount candidate exactly once, not operator money-back prerequisite |
| PP-093 | PAID, paid customer Drive URL cannot be bound/verified after bounded recovery and refund channel enabled | PAID/OWED -> eligible full refund after safe cleanup; never issue false QR or duplicate print |
| PP-094 | Corrupt/missing paid manifest makes purchased service impossible; no safe restoration | Independently verified unrecoverable merchant fault -> refund eligibility, preserve private photo evidence |
| PP-095 | One photo strip SENDING/UNCERTAIN and paper may have emerged | No blind retry or blind auto-refund; physical outcome/worker fence classified, conditional review |
| PP-096 | Three templates, some purchased strips already delivered, other outputs permanently fail | Full-goodwill-refund preference only when deterministically safe, valid merchant policy and bounded abuse controls; preserve partial paper truth |
| PP-097 | QR1 and QR2 both freshly verified PAID on same frozen logical purchase, same merchant and exact amount | One service entitlement; refund the unambiguously excess settled attempt only, one original refund key |
| PP-098 | Two QR attempts PAID but merchant/order/amount differ or conflict | No automatic refund or duplicate service; secure financial review |
| PP-099 | Midtrans create/status PENDING, 404, UNKNOWN, CANCELLED unpaid, or EXPIRED unpaid | **No refund request**, original cancel/status reconciliation only |
| PP-100 | Merchant GoPay QRIS POS Refund API not activated or disabled | No pretend auto-refund; `REFUND_REVIEW_REQUIRED` with redacted truthful support remedy |
| PP-101 | QRIS refund window elapsed or issuer/acquirer/merchant balance makes provider refund ineligible | No refund API retry loop or false success; lawful approved support/manual remedy |
| PP-102 | Provider account refund activation, documented API endpoint, status and refund_key semantics unknown | Production/refund API feature gate remains disabled; synthetic mocks do not authorize live money |
| PP-103 | Forged CCP, vault compromise, mismatched provider settlement or suspected refund fraud | Security/finance HOLD, no private photo release, no automatic money return |
| PP-104 | Permanent service fault triggers refund; app crashes before external refund POST | Durable unique original refund intent/key survives; continue/reconcile same original one only |
| PP-105 | Provider refund POST response lost/timeout or webhook repeats | Reconcile SAME refund intent/key, do not issue second unique refund or double payout |
| PP-106 | Provider accepts refund request but money remains in process | Only `REQUESTED`/`PROCESSING`, not `REFUND_CONFIRMED` nor claim funds in customer's balance |
| PP-107 | Provider independently confirms original refund, then stale print callback arrives | No old photo-strip reprint, no fresh Drive release or duplicated grant; ledger remains auditable |
| PP-108 | Refund intent races in-flight printer receipt or Drive upload worker | Fence/quarantine exact original work and physical paper possibilities; no blind refund/admission while unsafe |
| PP-109 | Verified refund completed but old camera/print lease/backend ACK still uncertain | Booth remains `ADS_PROTECTED` / `ISOLATION_HOLD`; technician if needed, never free from financial status alone |
| PP-110 | Customer checks refund status and receipt reference | Distinct state texts, authenticated/redacted reference, no fake contact/ETA, no media or credential leakage |
| PP-111 | Multiple real paid attempts, original order IDs, partial/different refund provider references | Refund exactly the intended original settled provider charge; no cross-merchant or wrong-attempt payout |
| PP-112 | Policy customer copy says "uang hangus, tidak pernah bisa refund" despite system failure or statutory rights | Reject blanket waiver; narrow proof-lost NO_AUTO_REFUND policy only; legal/provider/merchant gate required |

### Acceptance rules for the new refund-specific matrix

- 28 new tests are **additional** to PP-001..084; total is **112 unique proposed cases**, all NOT_RUN. Keep original 84 test descriptions and their historical scope intact.
- No Midtrans actual payout is permitted in documentation or synthetic tests. Mock provider refund `REQUESTED`/`PROCESSING`/`CONFIRMED`/`UNKNOWN`/`REJECTED` and refund-key uncertainty; merchant-activated Sandbox/integration evidence is a separate approval gate.
- Synthetic fixtures must not contain redeemable CCP/tickets, real user photos, merchant credentials or real payment bank data.
- Screen receipt mandatory + concurrent one paper ticket remains PP-041/042/051/079/080 and **is not conditioned** on refund functionality.
- `NO_AUTO_REFUND_PROOF_LOST` cannot be emitted unless genuine offer and no independently proven merchant failure are established. If the original photo purchase remains OWED due merchant defect, do not claim all obligations void.
- Merchant/provider settlement, fulfillment, print worker fencing, refund authorization/eligibility and consumer-law policy are independent axes. Evidence incomplete -> REVIEW, not fake provider-confirmed success.
- **No blanket legal forfeiture**: owner preference addresses automation for customer-lost proof alone, not enforceability of categorical no-refund standard terms.

**External gates, all NOT_RUN:** physical POS80 receipt, partial paper, QR scanning and Windows/Ubuntu camera; genuine configured Midtrans Sandbox status and webhook; Google Drive sharing/retention/deletion; vault/OS key compromise, restart and reinstall; CCP/QRIS/ticket UX at 800x1280 and 452x900; merchant/support policy and AR-13 release; Android only if separately approved.

**Integrity:** all 112 proposed new tests must begin as expected-fail / NOT_RUN, with fixture isolation and no real charge/refund/cloud deletion, then exact SHA/command/platform outcome. No historic AR/UAH CI PASS becomes POSTPAY PASS.