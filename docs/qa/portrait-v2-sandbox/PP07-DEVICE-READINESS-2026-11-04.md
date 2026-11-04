# PP-07 software continuation and device readiness — 4 November 2026

## Scope, authority and source

Authorized branch: `feature/post-preview-qris-checkout`. Starting remote HEAD:
`4b1c12ac173fa4cb64d7940a1679ff280b26f055`. The owner's 4 November execution
prompt authorizes implementation through device-test preparation. Existing
PP-D/RF-D/AR/UAH safety, legacy prepaid routes and external release gates remain.

Reviewed authorities include root `AGENTS.md`, development protocol/handover,
architecture, decisions/status, PP complete decision ledger, owner-approved
flow, state/security contract, refund/lost-proof and escalation policies,
acceptance matrix, consistency audit, implementation checkpoint, prior broad
simulation report and Windows pilot/26-case worksheet. Older design-only
restrictions describe their original epoch, not the current implementation task.

The attached Git checkout is clean but on stale `work` at `0fbf158`; it was not
modified or switched. A separate non-Git execution snapshot was built from
the exact authorized remote commit through the GitHub connector. Existing local
Git blobs were reused only when their content SHA matched the remote tree;
fetched source transport newlines were normalized against the Git blob SHA.
This snapshot is not a new branch and does not alter the owner's checkout.

## Increment 1 — BUG-036: ticket timeout independent of receipt worker

**Requirements:** PP-042 and PP-051; PP-D06; state/security invariant 10.

**Reproduction:** `PrivateCheckoutFixtureApp._poll_photos` returned as soon as
`PhotoJobs.busy` was true, before updating the Recovery Ticket countdown or
checking its automatic deadline. A slow receipt sender therefore froze the
display at 30 seconds and could leave the private QR visible beyond its window.
The existing manual-NEXT regression did not cover automatic expiry.

**Change:** process visible-ticket UI countdown and expiry before the worker-busy
return. Automatic expiry immediately retires the QR/code, just like NEXT.
Durable dismissal remains queued until the original receipt sender completes;
there is no second receipt, lost SENDING journal, forced release or overlapping
photo job. Closed/suspended UI still returns without rendering private content.

**New native regression:**
`test_ticket_countdown_and_auto_wipe_continue_during_blocked_receipt` holds the
actual synthetic receipt callback behind a threading event, advances only the
ticket's injected monotonic clock and tests both 800×1280 and 452×900. It checks
the 10-second label, automatic QR/full-code wipe, still-SENDING receipt, one
charge, and eventual single SUBMITTED receipt/DISMISSED screen with OWED intact.
No screenshots of live private test credentials are saved.

**Executed evidence:**

| Check | Result | Boundary |
| --- | --- | --- |
| New regression before fix | FAIL at both portrait sizes | Countdown stayed at 30 instead of 10 while receipt blocked |
| New regression after fix | PASS at both portrait sizes | Actual Kivy widgets; synthetic camera/provider/printer |
| Existing NEXT-during-blocked-receipt regression | PASS | Single original receipt and no code retention |
| Four visible-ticket-clock unit cases | 4 PASS | Actual visibility start, expiry/NEXT once, no timer reset |
| Focused total | 6 PASS; zero failures/errors/skips | Linux Python 3.12, SDL2 offscreen/software GL |
| Apps Script syntax and Node regression | PASS | Existing offline VM suite; no account/deployment/deletion |
| Matching-source CI for this increment | NOT_RUN at local checkpoint | Must inspect the resulting pushed source workflow separately |
| Physical/device/provider acceptance | HARDWARE_PENDING / BLOCKED | No real paper, merchant, upload, refund or customer media |

Focused runner arguments:

```text
python tools/run_kiosk_unittests.py
  test_post_preview_checkout_widgets.PrivateCheckoutWidgetTests.test_ticket_countdown_and_auto_wipe_continue_during_blocked_receipt
  test_post_preview_checkout_widgets.PrivateCheckoutWidgetTests.test_next_wipes_qr_while_original_receipt_sender_is_blocked
  test_post_preview_ticket_window
```

Local environment note: the existing Kivy virtual environment was retained.
An external scratch `sitecustomize` supplied the already installed cryptography
50.0.0 for offline execution; repository requirements still specify >=46,<50.
FastAPI 0.128.2/Pydantic 2.13.5 match the repository. Local results therefore
supplement, but do not replace, CI using the declared dependency bounds.
Restricted socket access initially stalled the in-process HTTP test client;
that run was stopped and repeated with local socket support. Neither that
infrastructure stall nor an initially omitted snapshot asset is a product bug.

## Current readiness and next action

The prior 522/522/58 CI at `238012f7` remains historical source-specific evidence.
Current full backend and affected native checks must finish and new CI must be
inspected before claiming this new source has the same broad verification.

Next: complete baseline/affected integration verification; inspect remaining
restart, proof/isolation, native-template and bounded repeated-session gaps;
continue safe micro-increments. Reconcile stale current-looking status banners
and owner launch instructions as the device package is finalized.

Full PP-001–112 and the 26 owner physical cases are not promoted to PASS by these
subassertions. Synthetic pilot, actual merchant Sandbox, physical acceptance and
production release remain independent readiness states. Actual Midtrans,
POS80 paper, Drive public ACL/upload/retention, supported OS vault protection and
real refunds retain their external gates. No production activation is authorized.
