# PP-07 consolidated software traceability — 4 November 2026

> [5 November partial software evidence: four atomic-proof races, two platform-process cases and five actual-transport/fake-HTTP cases. All full PP acceptance rows remain NOT_RUN.](PP07-CONTINUATION-2026-11-05.md)

**Executed source gate:** 0601354 / CI 41826366906, all 3/3 SUCCESS; Windows
533, Ubuntu 533, native Kivy 61 PASS, zero failures/errors/skips. This verifies
the registered synthetic/component regression, including 14 new test methods;
it does not promote the 112 complete acceptance rows below to PASS.

Branch: `feature/post-preview-qris-checkout`. This index preserves all **112** canonical PP cases and the actual **14** AR stage definitions. It is not a replacement for the canonical acceptance contract or a claim that all acceptance has passed.

Implementation, automated subassertions, complete acceptance and actual device/provider evidence are separate. Priority below is this continuation's engineering risk ranking, not a renaming of approved requirement IDs. All full PP cases remain **NOT_RUN at full acceptance scope**; mapped synthetic execution is partial evidence only. Unmapped rows are **NOT_MAPPED here**, not proof no unit test exists. Refund classification is not a working refund API.

Read the [source/evidence report](PP07-DEVICE-READINESS-2026-11-04.md), [canonical 112 cases](POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md), [existing J/N/P report](PP07-BROAD-SIMULATION-MATRIX-2026-11-02.md) and [owner device guide](POST-PREVIEW-DEVICE-TEST-START-HERE.md).

## Implementation, source, tests, dependencies and risks by group

All listed source paths are under `photobooth/`; test modules under `tests/`. Each PP row inherits its group's implementation/source/test/dependency/next-action fields below. This keeps shared fields consistent without presenting duplicate test counts as distinct cases.

| Group / PP IDs | Priority | Implementation | Source paths | Test modules | Dependencies / remaining risk | Required next action |
| --- | --- | --- | --- | --- | --- | --- |
| CAP / 001–010 | P1 | Guarded private capture/retake/composition source | `post_preview_store.py; post_preview_photos.py; kiosk_v2/post_preview_photos.py` | `test_post_preview_store; test_post_preview_photos; test_post_preview_journey_matrix` | Camera/disk/artwork and durable worker ownership | Run mapped software cases; owner camera/retake/orientation checks remain pending |
| FREEZE / 011–020 | P0 | Frozen quote/media/readiness guards | `post_preview_checkout.py; post_preview_readiness.py; post_preview_authority.py` | `test_post_preview_checkout; test_post_preview_readiness; test_post_preview_authority` | Exact frozen hashes, configured device/payment/Drive observations | Verify unsupported/missing dependencies and actual route/readiness without charging |
| PAY / 021–032 | P0 | Backend attempt/reconciliation source; integrated pilot mock-only | `post_preview_payments.py; post_preview_api.py; post_preview_inbox.py` | `test_post_preview_payments; test_post_preview_api; test_post_preview_payment_crashes` | Authentic independent provider evidence; exact immutable purchase | Keep merchant integration blocked until configured/provider-verified; preserve late/excess settlement |
| PROOF / 033–046 | P0 | Protected original CCP/ticket and in-process claim; platform gates remain | `post_preview_ccp.py; post_preview_ticket.py; credential_vault.py; post_preview_claim.py` | `test_post_preview_ccp; test_post_preview_ticket; test_credential_vault; test_post_preview_claim` | Original proof, fresh settlement, supported key protection and free booth | Verify actual OS vault/restart and physical proof opportunity; never no-proof media access |
| DELIVERY / 047–058 | P0 | Paid folder/media/print journals and synthetic dispatch | `post_preview_paid_drive.py; post_preview_paid_media.py; post_preview_paid_print.py; booth_sync.py` | `test_post_preview_paid_drive; test_post_preview_paid_print; test_post_preview_paid_delivery; test_booth_sync` | Exact paid URL/folder, exclusive lane and classified physical outcome | Owner POS80/public ACL/upload observations; preserve OWED and uncertain-paper hold |
| HANDOFF / 059–072 | P0 | Guarded mock isolation/claim; exact historical ACK readiness | `post_preview_isolation.py; post_preview_pilot_admission.py; post_preview_authority.py` | `test_post_preview_isolation; test_post_preview_pilot_admission; test_post_preview_authority; test_post_preview_native_journeys` | Exact PREPARE/ACK generation, worker fences, no financial/print ambiguity | Run A/B/returning-proof checks; device restart and prolonged soak remain separate |
| BOUNDARY / 073–084 | P0 | Cross-system guards; versioned policy/external calibration still open | `post_preview_payments.py; post_preview_ticket.py; post_preview_paid_delivery.py; booth_sync.py` | `test_post_preview_journey_matrix; test_post_preview_process_crash; test_post_preview_native_journeys` | Original identities, provider semantics, actual visibility, independent retention anchors | Inspect case-specific boundary; do not transfer legacy/synthetic evidence to live integration |
| REFUND / 085–112 | P0 | Evidence classifier only; no live refund transport/activation | `post_preview_refund_assessment.py` | `test_post_preview_refund_assessment` | Independent paid/failure/worker evidence; merchant capability and approved legal policy | Keep actual refund disabled; verify provider/account/OS gates before implementing financial I/O |

## Requirement-by-requirement evidence index

J01–J20 mappings are retained from the earlier executed report. J21, N25/N26, ticket-busy-clock, exact-ACK-authority and Drive-cycle-fence are new 4 November subassertions, with commands/results in the source/evidence report. All mapped results still require their exact source/CI context.

| Requirement | Canonical scenario | Group / priority | Partial automated references | Full verification | Remaining acceptance expectation |
| --- | --- | --- | --- | --- | --- |
| PP-001 | One template | CAP / P1 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | 3 original slots, at most one retake |
| PP-002 | Two templates | CAP / P1 | J02 | NOT_RUN (full scope) | 6 originals, independent retakes |
| PP-003 | Twelve templates | CAP / P1 | J01, N26 | NOT_RUN (full scope) | 36 originals, max 12 retakes |
| PP-004 | Multiple paper copies | CAP / P1 | J01, J02 | NOT_RUN (full scope) | No extra photo sessions |
| PP-005 | Crash during save | CAP / P1 | J16 | NOT_RUN (full scope) | No duplicated or lost committed shot |
| PP-006 | Crash during retake | CAP / P1 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Correct selected slot and quota |
| PP-007 | Deselect/reselect template | CAP / P1 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Consumed retake does not reset |
| PP-008 | Camera disconnect/countdown race | CAP / P1 | J16 | NOT_RUN (full scope) | No automatic shutter |
| PP-009 | Artwork updated mid-draft | CAP / P1 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Pinned version/hash or safe hold |
| PP-010 | Compose before payment | CAP / P1 | J01, N26 | NOT_RUN (full scope) | No print, paid completion or public upload |
| PP-011 | Copy change before QRIS | FREEZE / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Requote, no new captures |
| PP-012 | Add template before QRIS | FREEZE / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | New 3-photo session |
| PP-013 | Remove template before QRIS | FREEZE / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Revised quote, private media remains safe |
| PP-014 | Edit after provider-create intent | FREEZE / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Reject; same frozen cart |
| PP-015 | Preview download QR attempted unpaid | FREEZE / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | No accessible photo |
| PP-016 | Preview manifest corrupted | FREEZE / P0 | J06 | NOT_RUN (full scope) | No charge |
| PP-017 | Camera/disk not ready before capture | FREEZE / P0 | J15 | NOT_RUN (full scope) | No payment |
| PP-018 | Printer known unavailable pre-charge | FREEZE / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | No new charge |
| PP-019 | Drive API/sharing unavailable or READY reserve pool empty before charge | FREEZE / P0 | J15 | NOT_RUN (full scope) | Hold checkout; do not require a bound customer URL pre-PAID |
| PP-020 | Server quote/artifact mismatch | FREEZE / P0 | J01, J15 | NOT_RUN (full scope) | Reject, preserve draft |
| PP-021 | Lost POST response after provider created order | PAY / P0 | J12 | NOT_RUN (full scope) | Same attempt, no duplicate |
| PP-022 | 404 during provider propagation | PAY / P0 | J12 | NOT_RUN (full scope) | UNKNOWN, not unpaid |
| PP-023 | Duplicate/late webhook | PAY / P0 | J14 | NOT_RUN (full scope) | Independently verify fresh provider state |
| PP-024 | QR1 verified expired, active customer | PAY / P0 | J13 | NOT_RUN (full scope) | QR2 same frozen draft, no recapture |
| PP-025 | QR2 verified expired, active customer | PAY / P0 | J13 | NOT_RUN (full scope) | QR3 same frozen draft |
| PP-026 | QR3 expired | PAY / P0 | J13 | NOT_RUN (full scope) | No QR4, guarded close |
| PP-027 | Customer abandons PENDING | PAY / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | No automatic renewal; original cancel/reconcile |
| PP-028 | Cancel races settlement | PAY / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Retain PAID/OWED |
| PP-029 | QR1 PAID while QR2 creating | PAY / P0 | J13 | NOT_RUN (full scope) | One service; conflict ledger |
| PP-030 | QR2 and QR3 both settle | PAY / P0 | J13 | NOT_RUN (full scope) | No double printing; financial review |
| PP-031 | Restart during CREATE_UNKNOWN | PAY / P0 | J12 | NOT_RUN (full scope) | Original identity still authoritative |
| PP-032 | QR expires after customer departure | PAY / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | No automatic absent-customer renewal |
| PP-033 | Pre-PAID checkout-claim proof offered | PROOF / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Private, distinct, strong token/verifier |
| PP-034 | Claim proof used before PAID | PROOF / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Cannot show unpaid photos |
| PP-035 | Late PAID after customer goes | PROOF / P0 | J14 | NOT_RUN (full scope) | PAID_UNCLAIMED; no public print |
| PP-036 | Returning original proof with PAID/free booth | PROOF / P0 | J17 | NOT_RUN (full scope) | One original entitlement restored |
| PP-037 | Returning proof while visitor B active | PROOF / P0 | J17, J19 | NOT_RUN (full scope) | WAIT/DEFER, B not preempted |
| PP-038 | Wrong booth, forged, expired claim | PROOF / P0 | J18 | NOT_RUN (full scope) | Deny private access |
| PP-039 | Replay/brute force attempts | PROOF / P0 | J18 | NOT_RUN (full scope) | Rate-limited, scoped, audited |
| PP-040 | Customer paid but claim proof never offered | PROOF / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Owed/remedy; no customer blame |
| PP-041 | Fresh PAID, original customer owns booth, printer healthy and acknowledges SUBMITTED | PROOF / P0 | J02, J03 | NOT_RUN (full scope) | **Mandatory on-screen original QR + full code with 30s visible timer/NEXT** starts while **one same-token ticket receipt job is enqueued concurrently**, without waiting for ACK; successful printing MUST NOT skip or dismiss screen |
| PP-042 | Ticket printer unavailable, failed, timeout, delayed SUBMITTED or UNCERTAIN | PROOF / P0 | J03, J11, ticket-busy-clock | NOT_RUN (full scope) | **Same mandatory 30s ticket screen shown regardless of print outcome**; no reissue/auto-reprint, no timer reset on late printer callback, correct private cleanup on NEXT/zero |
| PP-043 | Crash after PAID before any genuine first ticket screen became visible / printer SENDING | PROOF / P0 | J03 | NOT_RUN (full scope) | Vault and owed policy; no public ticket on boot, no duplicate send; first lawful screen requires original customer proof and free booth |
| PP-044 | Crash after ticket SENDING | PROOF / P0 | J11 | NOT_RUN (full scope) | Never auto-reprint |
| PP-045 | Vault key/ciphertext missing | PROOF / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Fail closed, OWED retained |
| PP-046 | Operator/DEMO/QRIS/download QR as customer proof | PROOF / P0 | J18 | NOT_RUN (full scope) | Reject cross-type use |
| PP-047 | Compose auto-print callback while unpaid | DELIVERY / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Block paid photo print |
| PP-048 | 3 designs with 2+1+3 copies | DELIVERY / P0 | J02, J21 | NOT_RUN (full scope) | Six paid copies; only 9 captures |
| PP-049 | SUBMITTED but no paper physically emerged | DELIVERY / P0 | J02, J08, J14 | NOT_RUN (full scope) | Not recorded as physical delivery |
| PP-050 | Partial RAW bytes sent then timeout | DELIVERY / P0 | J07, J09 | NOT_RUN (full scope) | UNCERTAIN, no replay |
| PP-051 | Ticket screen shown while thermal printer lane holds original receipt job; NEXT pressed before printer returns | DELIVERY / P0 | ticket-busy-clock | NOT_RUN (full scope) | Screen timer operates independently; serialized exclusive original receipt / photo-strip jobs, no lost job, overlapping raw sends or reprint |
| PP-052 | Design A printed, B uncertain | DELIVERY / P0 | J07, J08, J09, J10 | NOT_RUN (full scope) | No A replay or blind B replay |
| PP-053 | Paid, Drive URL unverified | DELIVERY / P0 | J04, J05, J06, J21 | NOT_RUN (full scope) | Hold strip, retain OWED |
| PP-054 | Verified Drive URL, upload pending | DELIVERY / P0 | J04 | NOT_RUN (full scope) | Real QR, honest upload status |
| PP-055 | Anonymous draft and 25 READY folders | DELIVERY / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | No free folder claim/public upload |
| PP-056 | Cross-booth/foreign folder | DELIVERY / P0 | J05, J21 | NOT_RUN (full scope) | Binding rejected |
| PP-057 | Crash during upload | DELIVERY / P0 | Drive-cycle-fence, J04 | NOT_RUN (full scope) | Same checksum retry, no reprint |
| PP-058 | Last compose marks payment completed | DELIVERY / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Must remain pending paid obligations |
| PP-059 | Unpaid draft abandoned, no QR attempt | HANDOFF / P0 | J20, exact-ACK-authority/N25 | NOT_RUN (full scope) | Privacy fence, safe release |
| PP-060 | Customer actively capturing with slow worker | HANDOFF / P0 | J16 | NOT_RUN (full scope) | No hard inactivity cutoff |
| PP-061 | Inactive gallery/review/final preview | HANDOFF / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Warning, safe suspend |
| PP-062 | PENDING original checkout and new visitor | HANDOFF / P0 | Drive-cycle-fence, J19 | NOT_RUN (full scope) | No unsafe new payment |
| PP-063 | Stale A callback during B session | HANDOFF / P0 | Drive-cycle-fence, J16, J17, J20, J21, exact-ACK-authority/N25 | NOT_RUN (full scope) | Fenced; B unaffected |
| PP-064 | Crash during release/ACK lost | HANDOFF / P0 | Drive-cycle-fence, J17, J19, J20, J21, exact-ACK-authority/N25 | NOT_RUN (full scope) | Retry exact operation, no broad reset |
| PP-065 | Reboot with printer SENDING | HANDOFF / P0 | J09, J10 | NOT_RUN (full scope) | UNCERTAIN, no replay |
| PP-066 | Legacy PAID-first unfinished photo | HANDOFF / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Original capture recovery unchanged |
| PP-067 | Meong Fly consumed then unpaid abandon | HANDOFF / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | No new game attempt |
| PP-068 | Untrusted game DEMO discount | HANDOFF / P0 | J18 | NOT_RUN (full scope) | No real discount without verified backend |
| PP-069 | Repeated unpaid visits filling disk | HANDOFF / P0 | J20, J21, exact-ACK-authority/N25 | NOT_RUN (full scope) | Safe resource control, no active hard cutoff |
| PP-070 | Valid proof when booth finally free | HANDOFF / P0 | J17 | NOT_RUN (full scope) | Fresh verification, original claim |
| PP-071 | New visitor arrives during old worker uncertainty | HANDOFF / P0 | Drive-cycle-fence, J19, J20, exact-ACK-authority/N25 | NOT_RUN (full scope) | Neutral HOLD |
| PP-072 | Expired credential and paid liability | HANDOFF / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | No illicit reveal, no erased OWED |
| PP-073 | QR1 verified expired unpaid while same customer requests continuation | BOUNDARY / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | QR2 via its own guarded provider create; master flow does **not** force Advertising |
| PP-074 | USER_CANCEL with verified cancelled/unpaid while customer remains in front of camera | BOUNDARY / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Persist cancel intent and close safely; **never** QR2/QR3 |
| PP-075 | App minimized while live QRIS PENDING, no cancel action | BOUNDARY / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Privacy fence only; do not invent financial cancellation or renewed order |
| PP-076 | Inactivity warning during valid camera countdown or ongoing write/compose | BOUNDARY / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Active work not abandoned; retained original capture/retake quota |
| PP-077 | Restart after terminal unpaid but stale camera/file worker active | BOUNDARY / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | No new visitor before exact quiescence, fence and durable release ACK |
| PP-078 | Restart during paid authorized upload while a photo print is UNCERTAIN | BOUNDARY / P0 | Drive-cycle-fence, J10 | NOT_RUN (full scope) | Resume only idempotent upload; retain paid/print obligations; no blind print or unsafe release |
| PP-079 | Receipt SUBMITTED early while first mandatory 30s screen active, then polling/restart/returning claimant | BOUNDARY / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | First screen remains visible independent of SUBMITTED; when dismissed, never automatically re-display or reset countdown on provider/paper callback, polling, reboot or returning claim; preserve exact original presentation journal |
| PP-080 | Live paid owner has intact original booth lease, no CCP scan | BOUNDARY / P0 | J03 | NOT_RUN (full scope) | Open **mandatory** original Recovery Ticket screen and dispatch **same ticket receipt** concurrently once; no extra claim/CCP step |
| PP-081 | Precharge sees healthy Drive and available unclaimed READY pool, but atomic customer folder binding/URL verification fails after PAID | BOUNDARY / P0 | J15 | NOT_RUN (full scope) | No paid strip or invented QR; PAID/OWED retained; no unpaid READY consumption |
| PP-082 | Legacy Sandbox Drive OFF vs new purchased synthetic verified-link profile | BOUNDARY / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Existing BUG-027/028 profile unchanged; isolated fake link never represented as real cloud evidence |
| PP-083 | Attempt-create timed out; provider Legacy /v2/charge idempotency-header behavior unknown | BOUNDARY / P0 | J12 | NOT_RUN (full scope) | No unverified provider header or repeated POST; same original identity/status reconciliation |
| PP-084 | Draft/QR1/QR2/PAID/ticket timestamps across restart and expiry | BOUNDARY / P0 | J14 | NOT_RUN (full scope) | Different versioned TTL and 15-day/30-day anchors; no silent extension, deletion or mixing legacy 24h Sandbox claim rule |
| PP-085 | CCP genuinely visible/offered at first QRIS, later lost, original PAID service fully delivered | REFUND / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | `NO_AUTO_REFUND_PROOF_LOST`; cannot self-restore old photos without valid capability; no blanket legal waiver |
| PP-086 | Mandatory 30-visible-second ticket with full QR/code + same concurrent paper ticket, customer discards both, no independent service failure | REFUND / P0 | J03, J11 | NOT_RUN (full scope) | No automatic refund solely from customer-lost proof; no operator tokenless media unlock |
| PP-087 | First CCP never offered due prepay UI crash; original charge later independently PAID | REFUND / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Not labeled customer negligence; PAID/OWED and secure claim/remedy, no fake proof-presented evidence |
| PP-088 | After PAID printer SUBMITTED but mandatory Recovery Ticket screen never rendered/never visibly displayed | REFUND / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Printer ACK is not genuine screen offer; preserve claim/remedy, no customer-forfeiture |
| PP-089 | Customer lost genuinely offered ticket AND paid photo strips genuinely failed permanently | REFUND / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Do not refuse compensation on proof-loss ground; independently evaluate merchant service failure and refund |
| PP-090 | Customer disappears after PAID; valid CCP exists; claim window/onscreen screen timer expires | REFUND / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | No automatic refund merely on absence/expiry; retain paid/owed, lawful remedy and original claim rules |
| PP-091 | Recovery-ticket receipt printer broken but same original 30s screen displayed, purchased photo strips can still be safely fulfilled | REFUND / P0 | J11 | NOT_RUN (full scope) | Do not auto-refund solely because paper ticket failed; still permit genuine service |
| PP-092 | PAID original order, printer failed irrecoverably after bounded retry, worker safely fenced, provider refund enabled | REFUND / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Refund-first full original amount candidate exactly once, not operator money-back prerequisite |
| PP-093 | PAID, paid customer Drive URL cannot be bound/verified after bounded recovery and refund channel enabled | REFUND / P0 | J04 | NOT_RUN (full scope) | PAID/OWED -> eligible full refund after safe cleanup; never issue false QR or duplicate print |
| PP-094 | Corrupt/missing paid manifest makes purchased service impossible; no safe restoration | REFUND / P0 | J05, J06 | NOT_RUN (full scope) | Independently verified unrecoverable merchant fault -> refund eligibility, preserve private photo evidence |
| PP-095 | One photo strip SENDING/UNCERTAIN and paper may have emerged | REFUND / P0 | J07, J08, J09, J10 | NOT_RUN (full scope) | No blind retry or blind auto-refund; physical outcome/worker fence classified, conditional review |
| PP-096 | Three templates, some purchased strips already delivered, other outputs permanently fail | REFUND / P0 | J08 | NOT_RUN (full scope) | Full-goodwill-refund preference only when deterministically safe, valid merchant policy and bounded abuse controls; preserve partial paper truth |
| PP-097 | QR1 and QR2 both freshly verified PAID on same frozen logical purchase, same merchant and exact amount | REFUND / P0 | J13 | NOT_RUN (full scope) | One service entitlement; refund the unambiguously excess settled attempt only, one original refund key |
| PP-098 | Two QR attempts PAID but merchant/order/amount differ or conflict | REFUND / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | No automatic refund or duplicate service; secure financial review |
| PP-099 | Midtrans create/status PENDING, 404, UNKNOWN, CANCELLED unpaid, or EXPIRED unpaid | REFUND / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | **No refund request**, original cancel/status reconciliation only |
| PP-100 | Merchant GoPay QRIS POS Refund API not activated or disabled | REFUND / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | No pretend auto-refund; `REFUND_REVIEW_REQUIRED` with redacted truthful support remedy |
| PP-101 | QRIS refund window elapsed or issuer/acquirer/merchant balance makes provider refund ineligible | REFUND / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | No refund API retry loop or false success; lawful approved support/manual remedy |
| PP-102 | Provider account refund activation, documented API endpoint, status and refund_key semantics unknown | REFUND / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Production/refund API feature gate remains disabled; synthetic mocks do not authorize live money |
| PP-103 | Forged CCP, vault compromise, mismatched provider settlement or suspected refund fraud | REFUND / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Security/finance HOLD, no private photo release, no automatic money return |
| PP-104 | Permanent service fault triggers refund; app crashes before external refund POST | REFUND / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Durable unique original refund intent/key survives; continue/reconcile same original one only |
| PP-105 | Provider refund POST response lost/timeout or webhook repeats | REFUND / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Reconcile SAME refund intent/key, do not issue second unique refund or double payout |
| PP-106 | Provider accepts refund request but money remains in process | REFUND / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Only `REQUESTED`/`PROCESSING`, not `REFUND_CONFIRMED` nor claim funds in customer's balance |
| PP-107 | Provider independently confirms original refund, then stale print callback arrives | REFUND / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | No old photo-strip reprint, no fresh Drive release or duplicated grant; ledger remains auditable |
| PP-108 | Refund intent races in-flight printer receipt or Drive upload worker | REFUND / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Fence/quarantine exact original work and physical paper possibilities; no blind refund/admission while unsafe |
| PP-109 | Verified refund completed but old camera/print lease/backend ACK still uncertain | REFUND / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Booth remains `ADS_PROTECTED` / `ISOLATION_HOLD`; technician if needed, never free from financial status alone |
| PP-110 | Customer checks refund status and receipt reference | REFUND / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Distinct state texts, authenticated/redacted reference, no fake contact/ETA, no media or credential leakage |
| PP-111 | Multiple real paid attempts, original order IDs, partial/different refund provider references | REFUND / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Refund exactly the intended original settled provider charge; no cross-merchant or wrong-attempt payout |
| PP-112 | Policy customer copy says "uang hangus, tidak pernah bisa refund" despite system failure or statutory rights | REFUND / P0 | NOT_MAPPED in this partial journey crosswalk; inspect group tests | NOT_RUN (full scope) | Reject blanket waiver; narrow proof-lost NO_AUTO_REFUND policy only; legal/provider/merchant gate required |

## Retained AR-00–AR-13 definitions and branch boundary

Definitions below are copied from the [actual AR roadmap](AUTONOMOUS-RECOVERY-ROADMAP.md), not invented from the identifiers. Original paid-first evidence stays versioned. PP is the active implementation stream here, while all AR/UAH safety remains binding. Current AR-13 does not receive a production signoff from synthetic pilot tests.

| ID | Actual roadmap definition | Current continuation treatment / verification | Dependency / next action |
| --- | --- | --- | --- |
| AR-00 | contract and fixture freeze | Retain original implementation/evidence; run applicable legacy regression; no blanket recertification | Follow original stage contract and source-specific evidence; preserve PP/legacy version and external device/provider gates |
| AR-01 | uncertain charge creation / provider idempotency | Retain original implementation/evidence; run applicable legacy regression; no blanket recertification | Follow original stage contract and source-specific evidence; preserve PP/legacy version and external device/provider gates |
| AR-02 | provider evidence and automatic reconciliation | Retain original implementation/evidence; run applicable legacy regression; no blanket recertification | Follow original stage contract and source-specific evidence; preserve PP/legacy version and external device/provider gates |
| AR-03 | distinct ledgers and durable atomic admission | Retain original implementation/evidence; run applicable legacy regression; no blanket recertification | Follow original stage contract and source-specific evidence; preserve PP/legacy version and external device/provider gates |
| AR-04 | photo write-ahead capture | Retain original implementation/evidence; run applicable legacy regression; no blanket recertification | Follow original stage contract and source-specific evidence; preserve PP/legacy version and external device/provider gates |
| AR-05 | reconstruct original customer photo workflow | Retain original implementation/evidence; run applicable legacy regression; no blanket recertification | Follow original stage contract and source-specific evidence; preserve PP/legacy version and external device/provider gates |
| AR-06 | secure customer self-claim | Retain original implementation/evidence; run applicable legacy regression; no blanket recertification | Follow original stage contract and source-specific evidence; preserve PP/legacy version and external device/provider gates |
| AR-07 | native unattended UX | Retain original implementation/evidence; run applicable legacy regression; no blanket recertification | Follow original stage contract and source-specific evidence; preserve PP/legacy version and external device/provider gates |
| AR-08 | readiness and paid remedy | Retain original implementation/evidence; run applicable legacy regression; no blanket recertification | Follow original stage contract and source-specific evidence; preserve PP/legacy version and external device/provider gates |
| AR-09 | operator path and safe customer release | Retain original implementation/evidence; run applicable legacy regression; no blanket recertification | Follow original stage contract and source-specific evidence; preserve PP/legacy version and external device/provider gates |
| AR-10 | watchdog & recovery supervisor | Retain original implementation/evidence; run applicable legacy regression; no blanket recertification | Follow original stage contract and source-specific evidence; preserve PP/legacy version and external device/provider gates |
| AR-11 | webhook/backend separation | Retain original implementation/evidence; run applicable legacy regression; no blanket recertification | Follow original stage contract and source-specific evidence; preserve PP/legacy version and external device/provider gates |
| AR-12 | comprehensive validation | Retain original implementation/evidence; run applicable legacy regression; no blanket recertification | Follow original stage contract and source-specific evidence; preserve PP/legacy version and external device/provider gates |
| AR-13 | release controls | External release controls remain CONDITIONAL / NOT_APPROVED | Follow original stage contract and source-specific evidence; preserve PP/legacy version and external device/provider gates |

## Defects and operational handoff

BUG-036: visible ticket timer versus busy receipt; BUG-037: safe historical ACK versus next checkout; BUG-038: idle Drive daemon versus active request; BUG-039: unique default synthetic folder. See [bug register](../../bug_tracker.md) and the [4 November report](PP07-DEVICE-READINESS-2026-11-04.md) for reproduction, exact tests, pending/verified CI and rollback boundaries.

Owner physical PILOT-01–24 remain NOT_RUN; actual merchant payment/refund PILOT-25/26 remain BLOCKED. Source and a passing static preflight never replace those observations. Real multi-hour soak, platform escrow/reinstall, actual worker/peripheral restart, public Drive retention/deletion and merchant/legal approval remain explicit dependencies.
