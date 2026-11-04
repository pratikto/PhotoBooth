# Post-preview continuation — 5 November 2026

Authorized branch: `feature/post-preview-qris-checkout`. Starting remote source:
`5fc73bc025327a5ecf55a6673722cdb089e1eaeb`. Dates use Asia/Jakarta.

## Increment 1 — BUG-040 atomic returning-proof validity

**IMPLEMENTED / AUTOMATED_VERIFIED locally; matching-source CI pending.**
The synthetic candidate remains `READY_FOR_SUPERVISED_SYNTHETIC_DEVICE_TEST`;
this change does not enable actual merchant payments or persistent pilot restore.

`OriginalMockClaim.claim` verified the original CCP/Recovery Ticket before two
independent provider checks, then reacquired occupancy using that old verdict.
Four deterministic connected tests reproduce a proof expiring or being revoked
during the final settlement GET, with provider responses still within their
lease. All four originally FAIL: the old visit incorrectly becomes ACTIVE.

`OriginalCCPService` now shares its existing hash, role, booth, merchant, expiry,
revocation and rate-limit checks through a transaction-owned verifier. Claim
rechecks that exact original proof **after the last provider call, within the
same SQLite write transaction as occupancy acquisition**. No proof plaintext is
persisted, decrypted or redisplayed. Existing public verifier failure accounting
still commits before rejection. Invalidated proof cannot change the closed
original generation, create a reacquisition event, print, or mint another charge;
the original entitlement and PAID/OWED remain.

```mermaid
flowchart TD
    P[Original customer proof] --> V{Original proof valid?}
    V -->|No| DENY[Generic denial; preserve PAID/OWED]
    V -->|Yes| GET[Independent original settlement reconciliation]
    GET --> T[Begin original SQLite write transaction]
    T --> CURRENT{Same proof still valid now?}
    CURRENT -->|No| DENY
    CURRENT -->|Yes| FREE{Original exact ACK and booth free?}
    FREE -->|Busy| WAIT[WAIT; never preempt B]
    FREE -->|Unsafe| HOLD[HOLD; preserve original identity]
    FREE -->|Yes| CLAIM[Reacquire original generation atomically]
```

### Executed evidence

Source: starting SHA plus the code/tests in the commit containing this record.
Linux Python 3.12.14; cryptography 49.0.0 (within declared bounds), FastAPI
0.128.2, Pydantic 2.13.5, httpx 0.28.1. Synthetic photos/provider/vault/printer.

| Check | Outcome |
| --- | --- |
| Four new final-GET expiry/revocation cases before fix | 4 FAIL, 0 errors/skips |
| Initial fix placed before the last GET | 81 run, 77 PASS, 4 FAIL; corrected before delivery |
| Final claim/CCP/ticket/isolation/admission regression | 81 PASS, 0 failures/errors/skips, 13.437s |
| Exact-source Windows/Ubuntu/native CI | PENDING after functional push; never inferred from prior CI |
| Physical paper/camera/Drive/merchant acceptance | NOT_RUN / HARDWARE_PENDING / PROVIDER_BLOCKED |

```text
python tools/run_kiosk_unittests.py test_post_preview_claim test_post_preview_ccp test_post_preview_ticket test_post_preview_isolation test_post_preview_pilot_admission
```

The focused total includes existing imported fixture test classes; it is not 81
new scenarios. The four new methods map partial executable evidence to
PP-036/038/039/070/072/084/103. All 112 full acceptance rows remain NOT_RUN.

### Source delivery and workspace preservation

The attached checkout is the unrelated, clean local branch `work` at
`0fbf15829d1537a7f18990b492b1e5934f21c0f8`. It is not switched or staged.
Following the previously documented delivery method, development uses an exact
snapshot of the fetched authorized remote SHA, an external temporary Git index,
one explicit parent, and a normal fast-forward push to the existing authorized
ref. No branch creation, history rewrite, master merge or old-archive access.
Network-enabled managed execution restores Git transport; no proxy bypass.

### Independent readiness gates and external blockers

| Gate | Status / remaining evidence |
| --- | --- |
| A synthetic supervised device candidate | Preserve previous verified candidate; new local regression PASS, new CI pending |
| B actual post-preview merchant Sandbox | PROVIDER_BLOCKED: no merchant secret binding/runtime variable or verified public webhook supplied; integrated launcher remains synthetic-only |
| C protected cross-process pilot restore | NOT_IMPLEMENTED; Linux runtime has no configured session bus, Secret Service binding or visible TPM device; Windows DPAPI full original-worker restore/device acceptance pending |
| D comprehensive software acceptance | Partial AUTOMATED_VERIFIED; 112 full acceptance rows NOT_RUN |
| E owner physical acceptance | HARDWARE_PENDING; existing 26-case worksheet unchanged |
| F production | NOT_APPROVED; actual refunds NOT_ENABLED |

Environment observations establish only this runtime's available facilities,
not whether an owner's Windows/Ubuntu machine has a working protected vault.
No plaintext/key-file fallback, OS credential provisioning, payment/refund,
public upload, paper write or occupied-root reuse is introduced.

**Next engineering action:** add actual independent-process OS-protector
round-trip and corrupt/wrong-scope failure evidence to the existing credential
suite; on unsupported Linux prove fail-closed without creating a replacement
key. Then run the registered full source-matched backend/native regression and
inspect the pushed Windows/Ubuntu/native CI. This does not itself complete
original proof-gated worker restore or authorize reopening old pilot roots.

Reviewed authority: AGENTS, development protocol/architecture/handover/status/
bug register; device start/readiness/traceability/evidence; implementation
checkpoint; complete decision ledger; security state and refund/lost-proof
contracts; canonical 112 cases; supervised 26-case worksheet; original AR/UAH
and Midtrans provider contracts. Historical design-only restrictions and pending
CI notes retain their dated scope; the 4 November verified source is preserved.
