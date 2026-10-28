# Autonomous recovery — mandatory fault-injection, QA and acceptance matrix

**Status: PLANNED TEST CONTRACT; all newly specified tests NOT_RUN** · 28 October 2026  
**Baseline:** `2e5efe5d281a93fe8d22e53309a50147764d2939`  
**Links:** [Master](AUTONOMOUS-RECOVERY-MASTER-PLAN.md) · [Roadmap](AUTONOMOUS-RECOVERY-ROADMAP.md) · [Provider research](MIDTRANS-PROVIDER-CONTRACT.md) · [Operations](AUTONOMOUS-RECOVERY-OPERATIONS.md)

All test fixtures must be deterministic, offline, isolated, without paid provider calls/real print/Drive deletion. Additional owner-controlled on-device/provider tests are specified separately. The current code has earlier unit tests and CI evidence, but none are credited as PASS for the new matrix without rerunning/explicitly mapping exact functional SHA. Preserve historical failures and skips.

## A. Invariants asserted on every relevant transition

`I01` Exactly one internal order and immutable provider order ID for same checkout key.  
`I02` No second charge attempt/new order ID because of timeout/404/late status; never infer failed from timeout alone.  
`I03` Provider evidence matches merchant/booth/order/amount/currency/type/reference and fraud policy; no local payment authority.  
`I04` Exactly one service entitlement/grant and one bound local photo transaction per verified paid order.  
`I05` Any verified paid but undelivered service remains an auditable liability even if UI releases.  
`I06` No overwriting old/orphan original or retake; at most three originals and one retake per selected design.  
`I07` No duplicate composition, printing, upload, backend completion or physical capture from retries/crashes.  
`I08` Only authenticated original customer claim reveals previous photos or resumes camera.  
`I09` All external I/O off Kivy main thread; bounded retries/backpressure; stale callbacks and duplicate taps harmless.  
`I10` No rewinding/deleting/reassigning existing customer IDs, data or claims; original retention deadlines preserved.  
`I11` Sandbox never leaks provider key into GUI or produces real printer/Drive jobs; production disabled.  
`I12` No accidental cross-booth/customer/provider entitlement ownership or path/link traversal.

## B. Payment provider and backend (synthetic)

| ID | Fault injection or input | Required proof | Roadmap |
| --- | --- | --- | --- |
| PAY-01 | Kill process after persisting CREATE_PREPARED, before sending POST | One frozen order/key, safe resume and no duplicate charge | AR-01 |
| PAY-02 | Provider accepted POST but response is dropped | Same provider order reconciled; no new ID or charge | AR-01 |
| PAY-03 | Provider never saw POST; GET status not found | Hold CREATE_UNCERTAIN; no invented fail/replacement; documented safe next action | AR-01 |
| PAY-04 | Provider status returns stale/lagging 404 after POST | Bounded retry, no same-order POST unless verified semantics | AR-01 |
| PAY-05 | Two threads retry CREATE concurrently | Unique checkout/order, one logical provider creation, conflict safe | AR-01 |
| PAY-06 | Crash between provider evidence and DB commit | On reboot fresh revalidation, no duplicate entitlement | AR-02 |
| PAY-07 | API timeout while pending | Preserve QR/order; exponential+jitter retry (no hot loop) | AR-02 |
| PAY-08 | Network returns after several failures | Trigger one immediate safe reconciliation; no retry storm | AR-02 |
| PAY-09 | Settlement arrives during cancellation | Same original order becomes paid or formally held, no replacement charge | AR-02 |
| PAY-10 | Duplicate/out-of-order signed webhook | One update, monotonic evidence, no double grant | AR-02/AR-11 |
| PAY-11 | Tampered signed notification, amount/order/merchant mismatch | Reject/quarantine; never grant | AR-02 |
| PAY-12 | Cache says PAID, fresh provider says refund/partial_refund | Revoke new admission, preserve old fulfillment audit | AR-02 |
| PAY-13 | Cache says PAID, provider unreachable | Do not grant new sensitive recovery action; retain liability | AR-02 |
| PAY-14 | Missing optional fraud_status vs present deny/challenge | Contract-compliant decisions; unknown never bypasses validation | AR-00/AR-02 |
| PAY-15 | Provider terminal cancel/expire/fail confirmed | Existing visit closed safely; new checkout allowed only after release | AR-02 |
| PAY-16 | Late settlement for closed/suspended order | Original order/claim retained; never grants next visitor | AR-03 |
| PAY-17 | Two booths / wrong bearer / merchant IDs | No cross-tenant read, cancel, claim or resolve | AR-03 |
| PAY-18 | Lost claim/STARTED/COMPLETED response, retry same action | Same ID, idempotent server ACK; no new session | AR-03 |
| PAY-19 | Mismatched or reused action ID/body | Conflict and no mutation | AR-03 |
| PAY-20 | In-app clock changes or expired GUI timer | Provider evidence still authoritative; retention/expiry not silently extended | AR-02 |
| PAY-21 | Provider endpoint redirects/large body/auth failure | Reject, redact and hold; no secrets sent to redirect | AR-02 |
| PAY-22 | Sandbox-specific provider repeat-charge behavior unknown | Test remains BLOCKED on official contract, no speculative production call | AR-01 |

## C. Durable payment-to-photo binding and local files

| ID | Crash/fault point | Expected outcome | Stage |
| --- | --- | --- | --- |
| CAP-01 | Crash just before allocation intent | No second allocation if unknown; safe original reserve flow | AR-03/04 |
| CAP-02 | Crash after allocation intent, before folder creation | Same operation/ID can be recovered or held, never new unbound ID | AR-03/04 |
| CAP-03 | Crash after local folder creation, before manifest first write | Orphan recognized, original ID preserved, no "latest folder" inference | AR-04 |
| CAP-04 | Crash after initial manifest, before backend STARTED | Reconcile exact order/grant/transaction; no second transaction | AR-03/04 |
| CAP-05 | Crash after STARTED API accepted, before response persisted | Replay same acknowledgment, not service reallocate | AR-03 |
| CAP-06 | Crash after capture intent, before camera frame | Same slot/intent resumes safely; no phantom photo | AR-04 |
| CAP-07 | Crash after temp JPEG, before fsync/rename | Recover temp safely or quarantine; no acknowledged photo | AR-04 |
| CAP-08 | Crash after durable rename, before manifest photo entry | Detect orphan and validate file; no overwrite | AR-04 |
| CAP-09 | Crash after manifest entry, before GUI updates | Manifest is authoritative; exact saved frame restored | AR-04/05 |
| CAP-10 | Resume with photo 1/2/3 present | Correct count, no fourth default shot and no old file replacement | AR-05 |
| CAP-11 | Crash after retake select, before retake frame | Correct selected index and retake allowance; never double consume | AR-05 |
| CAP-12 | Crash after retake frame, before retake manifest/quota commit | Resolve exact retake intent/file or hold; no duplicate retake | AR-04/05 |
| CAP-13 | Crash after retake commit | Used quota remains consumed, original retained and final chosen path matches | AR-05 |
| CAP-14 | Crash during composition temporary output | Validate or recompute only if explicitly safe and no downstream effect; no duplicate output identity | AR-05 |
| CAP-15 | Crash after output committed, before next design | Restore completed design/copies; resume only unfinished design | AR-05 |
| CAP-16 | Crash between final local composition and service COMPLETE API | Reconcile same backend ACK; never repeat capture/print | AR-05 |
| CAP-17 | Another template version/price deployed while order held | Frozen quote/template/copy hashes match historical transaction | AR-03/05 |
| CAP-18 | Missing/corrupt media/manifest, path symlink/junction or wrong booth | Hold reason and preserve evidence; no unsafe restore | AR-04/05 |
| CAP-19 | Duplicate rapid touch, stale Kivy callback or minimized worker response | One valid active operation, no old session reentry | AR-07 |
| CAP-20 | Disk full/permission error on intent, image or manifest | No false commit; paid-unfulfilled remedy retained | AR-04/08 |
| CAP-21 | Local photo deadline passed during suspended visit | No resurrection/expiry extension; original claim and remedy remain | AR-08 |

## D. Kiosk, privacy, customer claim and operational effects

| ID | Scenario | Required assertion | Stage |
| --- | --- | --- | --- |
| UX-01 | App reopens with old PAID order | No old photo on startup; neutral claim screen only | AR-06/07 |
| UX-02 | New passerby taps "Continue" with no token | Denied; cannot expose thumbnails or consume original permit | AR-06 |
| UX-03 | Guessed/expired/replayed/wrong-booth token | Rate-limited denial and no photo data disclosure | AR-06 |
| UX-04 | Original valid claim token after restart | Restore exact order/manifest; user chooses fresh countdown | AR-06/07 |
| UX-05 | User abandons ambiguous payment | Rights retained; new visitor admitted only after safe durable separation | AR-09 |
| UX-06 | PAID with missing camera after settlement | No silent cancellation; customer claim/compensation recorded | AR-08 |
| UX-07 | Camera, disk, template or printer preflight failure | Block charge before QR creation, with clear user message | AR-08 |
| UX-08 | Offline Drive with approved verified reserves | Correct existing offline-safe behavior, no new hard block | AR-08 |
| UX-09 | Printer job SENDING/UNCERTAIN after restart | No automatic second spool/print; operator remedy | AR-09 |
| UX-10 | Drive upload/retry during resume | Existing queue retained; no duplicate customer folder/QR; retention policy unchanged | AR-09 |
| UX-11 | App frozen while upload/QR/checkout worker running | No UI thread blocking; watchdog cannot replay external effects | AR-10 |
| UX-12 | Kill/restart repeatedly, including competing startup processes | Single live lease/fencing and bounded supervisor restart | AR-10 |
| UX-13 | Operator wrong PIN/replay/cross-order resolution | Rate-limited, fully audited denial; same action ID idempotent | AR-09 |
| UX-14 | Operator closes PAID Sandbox test | Ledger remains PAID + UNFULFILLED where appropriate, never fake refund/completion | AR-09 |
| UX-15 | 800×1280 and 452×900 recovery views | Screenshot/readability/copy link/touch safe; no clipping | AR-07 |
| UX-16 | Exit/restart with no active obligation | Ordinary v2/MOCK paths unchanged and stable | AR-12 |
| UX-17 | Server secret/PIN/token in exception/report/process args | No secret exposure; redaction assertions | AR-09/11 |
| UX-18 | Archive folder "old" or linked storage | Excluded from scan, sync, retention and recovery | All |

## E. Webhook backend (only if separately authorized)

`WEB-01` Public HTTPS valid TLS, host/port/redirect/header compatibility.  
`WEB-02` Correct signature verification, exact status/order amount and anti-replay/dedup.  
`WEB-03` Durable inbox acceptance before 2xx, bounded handler latency, background reconciliation.  
`WEB-04` Duplicate/out-of-order notification and provider outage during callback.  
`WEB-05` Crash after inbox insert/before acknowledgment, replay without double grant.  
`WEB-06` Endpoint downtime, retries, poison event quarantine, monitoring/metrics.  
`WEB-07` Legacy-to-BI-SNAP differences explicitly gated; never confuse `X-EXTERNAL-ID`, invoice idempotency header and provider order ID.  
`WEB-08` Public API limits, admin identity/auth, no local debug or public private records.  
All WEB items are **NOT_RUN** until infrastructure approval.

## F. Test harness specification

- Use `tempfile.TemporaryDirectory`, fake clock, fault injection at **every** durable write boundary and external request boundary; run isolated process crash/restart cases, not just raised exceptions in memory.
- For DB reliability test SQLite WAL, abrupt exit, connection close/reopen, two concurrent workers, unique indexes, transaction rollback, blocked writer and persistence at new process PID.
- For media use tiny synthetic distinguishable JPEG/PNG assets; verify actual file hashes, content versions, paths, original/retake selection and output IDs. Never place customer photo samples/merchant keys in CI artifacts.
- For GUI use injected Kivy worker outcomes, main-thread update checks, lost callbacks, minimize/restore, 800×1280 + 452×900 native renders. Validate both portrait dimensions, no interaction overlap.
- Mock provider states: pending, settlement, expire, cancel, deny, failure, refund, partial_refund, missing, stale 404, malformed JSON, wrong merchant/order/currency/amount/type/fraud, slow response, timeout and duplicate callback.
- Test each transition at ***before effect / after effect before commit / after commit before reply / after reply*** whenever applicable.
- Record expected/actual backend and local order state, fulfillment state, files present, job counts, customer-visible screen and operator log per test.
- First write tests to reproduce the loophole; implement minimal source fixes; verify no regression in original P3/MOCK/Sandbox and v1.

## G. Evidence and acceptance sheet

| Gate | Evidence required | Current |
| --- | --- | --- |
| Source unit/integration | Exact SHA, OS, command, full count PASS/FAIL/SKIP, fixtures and no secret leakage | NOT_RUN |
| Crash/restart fault-injection | Every PAY/CAP/UX applicable ID mapped to test output | NOT_RUN |
| Complete GUI regression | One final applicable full suite after last functional change; no borrowed old pass | NOT_RUN |
| GUI screenshot/pixels | Tested exact source 800×1280 and 452×900, readability and QR identity | NOT_RUN |
| Windows booth | Real camera/storage, app close/reopen/power interruption, native touch/keyboard | NOT_RUN |
| Ubuntu mini PC | Actual graphical session service, permissions, startup, real camera/print hardware | NOT_RUN |
| Android/tablet | Separate build/lifecycle/provider and storage behavior; if targeted, actual device evidence | NOT_RUN |
| Merchant Sandbox | Owner controlled simulator, actual status/poll/cancel/late settlement; no bank/wallet | NOT_RUN |
| Production QRIS | Account/BI-SNAP decision, webhook, merchant terms, refund/compensation, security | NOT AUTHORIZED |
| Paper/Drive/retention | Real paper/phone/cloud access and authorized deletion test when separately in scope | NOT_RUN |

**Blocker policy:** Any unresolved P0 no-double-charge, no-double-fulfillment, photo overwrite, privacy leak, financial liability loss, or unproven provider creation outcome blocks unattended release. A test running successfully is not a real-device/merchant certification. Do not mark new tests PASS without execution.

## H. Owner handoff

For each stage add a row to implementation evidence documenting `AR-XX`, source SHA, test IDs, counts, CI run, device/provider acceptance and known risks. Historical [P5 acceptance](../portrait-v2-pending-acceptance/README.md) is retained; these new cases supplement it and do not require retesting unrelated already-stable photo/game cycles without a code-affecting regression.
