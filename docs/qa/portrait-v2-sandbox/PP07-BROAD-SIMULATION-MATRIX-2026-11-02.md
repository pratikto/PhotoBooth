# PP-07 broad synthetic simulation coverage matrix — 2 November 2026

## Verified initial 20/20 integration journeys PASS on Windows and Ubuntu

**Tested source:** [`bd70593f20eb62e9da432ba962bd1f59e8265bf5`](https://github.com/pratikto/PhotoBooth/commit/bd70593f20eb62e9da432ba962bd1f59e8265bf5)  
**Matching-source workflow:** [GitHub Actions #41407613830](https://github.com/pratikto/PhotoBooth/actions/runs/41407613830).

| Job | Executed | New J01–J20 | Failures | Errors | Skipped | State |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| Ubuntu backend/private-state | **520** | **20/20 PASS** (test names verified from job logs) | 0 | 0 | 0 | **PASS** |
| Ubuntu native Kivy/Xvfb | **54** | This new module is backend; existing 54 GUI tests | 0 | 0 | 0 | **PASS** |
| Windows backend/private-state | **520** | **20/20 PASS** (individual test names and 520/520 summary verified) | 0 | 0 | 0 | **PASS** |

The previous first run had 18 PASS + 1 FAIL + 1 ERROR among J01–J20; the exact two test specification corrections and their reasons remain documented below. These newer PASS results do not include actual local Kivy 12-template rendering, actual payment webhook provider, POS80 output, cloud upload, real OS process kill, refund or completion of the 112 complete owner acceptance cases.

---

## Purpose and evidence standard

The owner correctly rejected treating 1,042 Windows/Linux/Kivy unittest **executions** as if they proved 112 complete customer journeys. This new work package extends test coverage across the **actual local checkout service, durable SQLite ledger, authenticated local HTTP API, selected printer/Drive adapters, and guarded return-admission coordinator**. It does not invent screenshots, physical paper, cloud confirmations, real merchant charges, or operator approval.

**Authorized development branch:** `feature/post-preview-qris-checkout`. No new branch, production provider, master merge or data wipe. New simulation modules are strictly synthetic, and the real payment/printing/Drive connectors remain disabled by default.

**Authority reviewed:** `AGENTS.md`; `docs/DEVELOPMENT_PROTOCOL.md`; `docs/DECISIONS.md`; `docs/FEATURE_STATUS.md`; `docs/next_step.md`; `docs/DEVELOPMENT_HANDOVER.md`; [complete decision ledger](POST-PREVIEW-QRIS-COMPLETE-DECISION-LEDGER.md); [approved master product flow](POST-PREVIEW-QRIS-OWNER-APPROVED.md); [durable security/financial state contract](POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md); [112-case acceptance matrix](POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md); [26-case owner Windows UAT](PP07-SUPERVISED-WINDOWS-UAT.md); [prior P0 fault injection](PP07-ADVERSARIAL-GUI-FAULTS-2026-11-02.md).

## First execution and corrections — transparent history

[Initial CI 41407278546](https://github.com/pratikto/PhotoBooth/actions/runs/41407278546), source `eb9bbecf`, executed all **J01–J20** on Ubuntu. **18 PASS, 1 FAIL, 1 ERROR** (backend job failed; native GUI baseline 54/54 PASS; Windows run did not reach a final passing result). Neither issue was a proven payment/print vulnerability:

- **J02:** the first test incorrectly counted all JPEGs in the complete root as *shutter activations*. The paid pipeline intentionally **imports and preserves nine original JPG bytes into its own staging root** in addition to the nine original capture files. The corrected test distinguishes **9 camera-original JPEGs + 9 separate paid-import JPEGs** rather than weakening copy-count assertions. It still verifies one charge, exactly three purchased batch sends [2,1,3], and `OWED`.
- **J06:** deliberate corruption of a saved paid JPEG correctly raised the narrow safety exception `CaptureRecoveryRequired('Saved media hash mismatch')`, which the test's original expected exception tuple omitted. The corrected test explicitly requires that exact recovery exception, while ensuring zero paid print output and `OWED` remains.

The **test-only correction** is [`bd70593f`](https://github.com/pratikto/PhotoBooth/commit/bd70593f20eb62e9da432ba962bd1f59e8265bf5); source hardening BUG-034 remains unchanged. [Corrected-source GitHub Actions #41407613830](https://github.com/pratikto/PhotoBooth/actions/runs/41407613830) is **PENDING** until all CI job logs are read. Do not label J01–J20 PASS from the first failed run. Both findings illustrate why a full multi-stage simulation adds value beyond isolated backend tests.

## Why additional work was necessary

The verified prior baseline [CI #41404106134](https://github.com/pratikto/PhotoBooth/actions/runs/41404106134) at `0548bc89` was **494 Windows + 494 Ubuntu + 54 native** (1,042 successful test executions, 0 failures/errors/skips). This baseline included substantial unit testing, but several *composed*, customer-scale failure cases were not executed as a single connected journey.

**New source finding — BUG-034 (source verified, tests pending):** The public paid-delivery UI and `PrivateCheckoutService.paid_print_next` blocked B when A's purchased strip was SENDING/UNCERTAIN. However, a different `OriginalPaidPrintDispatcher` instance could directly try B because the persistent dispatcher only inspected B's individual job state. A wrong higher-level route could therefore bypass the quarantine. [Code fix `92717d25`](https://github.com/pratikto/PhotoBooth/commit/92717d25e08d98abbf1fffcbe317f4a2b3a7a9e8) adds an atomic **purchase-wide SQLite quarantine query inside dispatcher.send_once**, before any B job changes or external printer output. The selected purchase cannot send another batch while any SENDING/UNCERTAIN job remains, even if the caller bypasses UI/service or re-instantiates a new dispatcher. Existing `SUBMITTED` outcomes are distinct: subsequent approved B remains permitted if A's send is fully classified as SUBMITTED. Physical paper remains unverified for SUBMITTED.

## New executable cross-component journey matrix — J01–J20

**Source:** `tests/test_post_preview_journey_matrix.py`. Added in [commit `7983f6b3`](https://github.com/pratikto/PhotoBooth/commit/7983f6b39646e263683c169813906a1c7e64b83f). [CI registration `eb9bbecf`](https://github.com/pratikto/PhotoBooth/commit/eb9bbecf49e0f076fb3f3cefdc34a5f9b1e53085) includes the new module in **both Windows and Ubuntu** jobs. The test module does not use Kivy itself; existing headless native tests remain a distinct GUI evidence track.

| ID | Connected scenario and actual failure injection | Core invariants | PP case mapping (partial automated evidence only) |
| --- | --- | --- | --- |
| J01 | Select **all 12 designs**, capture **36 originals**, quote and begin one synthetic checkout; repeated status polling | One immutable cart, one provider order, no recapture or hidden copy multiplier | PP-003,004,010,020 |
| J02 | Three designs, **2+1+3 copies**, 9 original frames, verified synthetic PAID, Recovery Ticket, three purchased output batches | Exactly [2,1,3] copy sends, one charge, one original ticket, `OWED` and no fabricated paper | PP-002,004,041,048,049 |
| J03 | Attempt paid delivery before ticket offer, visibility and dismissal; then complete original ticket | No premature paid photo printing/Drive claim | PP-041,042,043,080,086 |
| J04 | After PAID and ticket, Drive bind goes offline, then recovers | Same reserved transaction ID, still `OWED`, no new charge or receipt | PP-053,054,057,093 |
| J05 | Drive reports `link_verified=True` with **attacker/untrusted URL** | Deny purchased output despite misleading remote result | PP-053,056,094 |
| J06 | Mutate saved original JPEG after PAID, before composing purchased output | No substituted/corrupt photo can be printed; paid liability survives | PP-016,053,094 |
| J07 | Thermal printer returns explicit negative ACK for A, B remains ready | Quarantine all later purchased batches, no blind replay | PP-050,052,095 |
| J08 | A SUBMITTED, B times out and may have emitted paper | A remains immutable, B UNCERTAIN, no third call, `OWED` | PP-049,052,095,096 |
| J09 | Re-instantiate dispatcher and directly send B after A UNCERTAIN | **BUG-034**: purchase-wide ledger guard, not merely GUI button | PP-050,052,065,095 |
| J10 | Crash-seam leaves A journal SENDING; new dispatcher tries B | No cross-dispatcher B send, preserve original journal | PP-052,065,078,095 |
| J11 | Original printed Recovery Ticket transport times out while screen legitimately visible | One original ticket, no printer replay, paid liability remains | PP-042,044,086,091 |
| J12 | Lost authenticated HTTP response after charge create, then 10 polls | Same original order, one provider create, 6 photos intact | PP-021,022,031,083 |
| J13 | QR1→QR2→QR3 by **verified expiry**; later all three settle | Exactly one paid service/entitlement, two separately audited **excess** attempts, no QR4 | PP-024,025,026,029,030,097 |
| J14 | 25 independently verified PAID status polls after two-design capture | No claim, print, order, photo or paid-entitlement duplication | PP-023,035,049,084 |
| J15 | Drive sharing readiness fails between final photo approval and checkout freeze; recovers | No charge before readiness, no recapture, one eventual checkout | PP-017,019,020,081 |
| J16 | Capture request with wrong immutable worker generation, then valid capture | Reject stale worker camera call, no automatic shutter or provider call | PP-005,008,060,063 |
| J17 | Customer A paid/protected, B admitted and takes a photo, A proof returns WAIT, B retires, A reacquires | A does not preempt B, originals/one PAID entitlement preserved, fenced isolation | PP-036,037,063,064,070 |
| J18 | While B active, scan payment/DEMO/operator/cross-booth/oversized forged proof | Cross-role proof never reveals A or releases B | PP-038,039,046,068 |
| J19 | Stall worker at A paid/protected handoff; attempt B and original A proof; release worker | Both paths fail closed during busy; afterward A may reclaim original rights | PP-037,062,064,071 |
| J20 | 12 successive unpaid protected visits through PREPARE/ACK/isolation and new admission | Unique drafts, exactly one ACK per release, zero merchant charges, no old visitor leak | PP-059,063,064,069,071 |

**Execution status:** The first full run [#41407278546](https://github.com/pratikto/PhotoBooth/actions/runs/41407278546) **FAILED** (18/20 new Ubuntu tests PASS) due the two test assumptions documented above. The corrected source `bd70593f` has **Ubuntu 20/20 J cases PASS, backend 520/520 PASS and native 54/54 PASS** in [CI #41407613830](https://github.com/pratikto/PhotoBooth/actions/runs/41407613830). The distinct Windows job later **completed SUCCESS**: 520/520 PASS, 0 failures/errors/skips. Matching-source native 54/54 also PASS. Both backend jobs include all 20 J cases (not 20 extra scenarios on each OS). Until the actual `J01..J20` test names, PASS/FAIL and jobs are verified from matching-source logs, every new row above is `IMPLEMENTED / NOT YET VERIFIED`, not PASS. If a test fails, preserve the failure and fix actual root cause; never delete a legitimate safety assertion simply to make CI green.

## Second test layer — Native Kivy customer journeys N21–N23

The source now includes `tests/test_post_preview_native_journeys.py`, introduced at [`ff82b4b0`](https://github.com/pratikto/PhotoBooth/commit/ff82b4b0c797257cc7ad1ff3b09759dd47dc5dc9) and explicitly registered by [native CI change `e5ddf7d9`](https://github.com/pratikto/PhotoBooth/commit/e5ddf7d95bf0a07492f46de95f93d23b3d8a7051). Unlike J01–J20, these tests traverse actual Kivy screen widgets and customer action callbacks inside a headless Xvfb display. The source-matching [CI #41408516448](https://github.com/pratikto/PhotoBooth/actions/runs/41408516448) is **PENDING** until native run logs show individual results.

| ID | Native UI scenario | Observable UI and financial assertions | Status |
| --- | --- | --- | --- |
| N21 | Ads/tutorial → choose three designs 2+1+3 → capture 9 images → final preview → original CCP → synthetic PAID → same Recovery Ticket → simulated Drive QR → three purchased print actions | Exactly one provider charge; one ticket receipt; one 2+1+3 paper-intent set; no false paper fulfillment | **ADDED; CI PENDING** |
| N22 | Original paid/ticket journey, Drive deliberately offline on first binding, then route becomes available and customer presses original "retry delivery" action | No second charge/ticket, original reserved paid transaction and `OWED` preserved; one subsequent safe paid-strip submission | **ADDED; CI PENDING** |
| N23 | A has paid, is privacy-locked to protected Ads, B enters and captures; A tries to invoke private recovery claim while B owns camera | Claim modal restricted to protected Ads only, no A proof/media leakage or camera takeover, original A remains `OWED`, one charge | **ADDED; CI PENDING** |

These tests do **not** replace a real touchscreen usability check, human-readable QR scanning, true wall-clock 30-second presentation timing, cloud ACL, or physical printer-paper observation. They add an actual native GUI evidence layer missing from the first integration run.

## Third test layer — actual OS process termination P01–P02 and protected GUI N24

**Current matching-source code:** `aa6ce68c` ([commit](https://github.com/pratikto/PhotoBooth/commit/aa6ce68c778e8c5c13005201597abdc9b318d319)); [CI #41409149264](https://github.com/pratikto/PhotoBooth/actions/runs/41409149264) is **RUNNING** until actual per-job logs prove outcomes.

- **N23 test correction:** The initial GUI test attempted to let B begin while A's original ticket receipt had not yet been genuinely displayed and reliably `SUBMITTED`. The guard correctly refused B, so the test's unconditional tutorial completion raised `NavigationError` (run [#41408717395](https://github.com/pratikto/PhotoBooth/actions/runs/41408717395)). This is an expected protective block, not something to override. At `7944a4fc`, N23 now waits for A's legitimate visible Recovery Ticket and exactly one recorded `SUBMITTED` receipt before proceeding to protected Ads → B capture and checking that A's proof cannot preempt B. **Pending source-aligned CI**.
- **N24 new negative admission:** Simulate A's original receipt as `UNCERTAIN`, protect public Ads, request B's photo journey and assert B is **not admitted**, the original A draft remains, no release ACK/new charge, and original `PAID/OWED` survives. A public Ads screen does not certify financial or printer release. **Pending source-aligned CI**.
- **P01 actual OS process death while original Recovery Ticket receipt printing:** A separate child `tests/post_preview_process_fault_fixture.py` uses `os._exit(73)` *inside* the printer callback, without finally/cleanup after the durable ticket `SENDING` write. An entirely separate Python process reopens SQLite and checks one PAID attempt, ticket `SENDING`, original `OWED`. Test is `tests/test_post_preview_process_crash.py::test_p01_actual_process_exit_during_recovery_receipt_preserves_owed`. No physical printer is connected. **Pending CI on Windows and Ubuntu**.
- **P02 actual OS process death while purchased strip printing:** After original PAID and ticket completion, exit inside strip printer callback, then independent process reopen checks purchased strip `SENDING`, original `OWED`, original receipt `SUBMITTED`, one PAID attempt and original copy count two. The crash is real process termination, not simulated exception; actual printer bytes/cutter state still cannot be known. Test `test_p02_actual_process_exit_during_paid_strip_preserves_sending`. **Pending CI on Windows and Ubuntu**.

**New source and CI registration:** `7944a4fc` (native N23 safety-positive and N24 rejection), `137dddb2` (child process), `9d417fab` (parent OS death/reopen assertions), `aa6ce68c` (register process-crash test module in Windows/Linux CI). If any test fails, fix the actual root cause and rerun matching-source CI; do not weaken the durable journal/visitor-release invariants.

---

## Deliberately separate full acceptance and test debt

The canonical [PP-001..112](POST-PREVIEW-QRIS-ACCEPTANCE-MATRIX.md) are complete-system acceptance scenarios, not a percentage that can be inferred from 20 composed tests or 1,000 repeated runs. This package adds evidence to multiple PP numbers but does **not** turn any complete PP row into a physical/customer-provider PASS.

### Further simulation candidates (independent of owner hardware)

- True OS-level subprocess termination/restart **between** durable SENDING and printer I/O, with SQLite reopening and original worker/lease fencing; J10 currently covers persistent journal model only
- Real watchdog/worker scheduling and A↔B contention with in-flight upload and provider GET, not only synchronous/mock callbacks
- 12-template native Kivy layout, memory growth and 30-second genuinely visible QR on multiple portrait sizes
- Meong Fly DEMO/merchant coupon one-use integrated with a true frozen post-preview cart and discount revalidation; current game tests are separate
- Full operator login, ticket scan roles and service escalation under hardware faults; operator settings remain separately gated
- Explicit property-/mutation-based tests for adverse race orderings, wall clock rollback, repeated webhook retry storms
- Multi-hour synthetic soak tests and storage quota/retention cleanup dry-runs without deleting any real media
- Refund request/reconciliation journal simulation (no merchant refund API calls until verified provider support)

### Cannot be certified without real devices, accounts or owner interaction

Real camera orientation/touch, printer paper/thermal cutter and network delays, actual Google Drive public-share ACL/upload/retention deletion, actual Midtrans Sandbox provider reconciliation, merchant refunds, legal terms, and the owner's 26 physical tests. Production release remains BLOCKED.

## Required next engineering checkpoint

1. Verify actual GitHub Actions job conclusions and `J01..J20` individual test outcomes for source `eb9bbecf`.
2. Fix any source/test defect with micro-push, then rerun exact-source CI on Windows and Linux. Do not claim 20/20 until verified.
3. Add a second native GUI integration increment for the highest-risk missing cross-visit flows and include actual native job evidence.
4. Reconcile `docs/next_step.md`, `docs/FEATURE_STATUS.md`, `docs/DEVELOPMENT_HANDOVER.md`, `docs/bug_tracker.md`, and the full PP acceptance index without deleting historical decisions.
5. Preserve the existing branch, original customer rights, no print replay, bounded QR1/2/3 identities, and every previously approved safety/financial policy.
