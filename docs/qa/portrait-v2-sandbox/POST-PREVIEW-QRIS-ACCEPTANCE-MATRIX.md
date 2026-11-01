# Post-preview QRIS — acceptance and adversarial QA matrix

**1 November 2026 | OWNER-APPROVED DESIGN | all 84 scenarios NOT_RUN.** This is a test specification, not an executed test report. Refer to [canonical decisions and 11 diagrams](POST-PREVIEW-QRIS-OWNER-APPROVED.md) and [security contract](POST-PREVIEW-QRIS-SECURITY-STATE-CONTRACT.md). Existing AR-00–13 and UAH evidence is historical, not new-flow acceptance.

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
| PP-019 | Drive URL not verified pre-charge | Hold new checkout |
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
| PP-041 | Recovery Ticket after PAID | One original receipt submission |
| PP-042 | Ticket printer unavailable/uncertain | Same token 30s + NEXT if original live owner |
| PP-043 | Crash after PAID before ticket | Vault/recovery policy; no public ticket on boot |
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
| PP-051 | Ticket and strips share printer | Exclusive, separate jobs |
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
| PP-079 | Ticket receipt already SUBMITTED; polling/restart/returning claimant | Do not automatically re-display or reset original fallback; preserve presentation journal |
| PP-080 | Live paid owner has intact original booth lease, no CCP scan | Go directly to original Recovery Ticket; no extra mandatory claim step |
| PP-081 | Precharge sees unclaimed valid READY folder, but exact folder binding fails after PAID | No paid strip or invented QR; PAID/OWED retained; no unpaid READY consumption |
| PP-082 | Legacy Sandbox Drive OFF vs new purchased synthetic verified-link profile | Existing BUG-027/028 profile unchanged; isolated fake link never represented as real cloud evidence |
| PP-083 | Attempt-create timed out; provider Legacy /v2/charge idempotency-header behavior unknown | No unverified provider header or repeated POST; same original identity/status reconciliation |
| PP-084 | Draft/QR1/QR2/PAID/ticket timestamps across restart and expiry | Different versioned TTL and 15-day/30-day anchors; no silent extension, deletion or mixing legacy 24h Sandbox claim rule |

**Mapping check:** K01 privacy/ownership -> PP-HAND and PP-CRASH; K11 OWED/COMPOSED -> PP-PRINT and PP-DRIVE. `PP-PRIV` and `PP-OWED` are not standalone acceptance groups. All PP-001..084 remain NOT_RUN until newly implemented, executed and individually evidenced.

**External gates, all NOT_RUN:** physical POS80 receipt, partial paper, QR scanning and Windows/Ubuntu camera; genuine configured Midtrans Sandbox status and webhook; Google Drive sharing/retention/deletion; vault/OS key compromise, restart and reinstall; CCP/QRIS/ticket UX at 800x1280 and 452x900; merchant/support policy and AR-13 release; Android only if separately approved.

**Integrity:** all new tests must begin as expected-fail / NOT_RUN, with fixture isolation and no real charge/refund/cloud deletion, then exact SHA/command/platform outcome. No historic AR/UAH CI PASS becomes POSTPAY PASS.