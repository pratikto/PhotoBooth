# On-screen Recovery Ticket fallback when the receipt printer is unavailable

**Status: OWNER-APPROVED UX REQUIREMENT / DOCUMENTATION ONLY / NOT IMPLEMENTED / NOT TESTED.**
Recorded from the owner's follow-up to the payment flowchart on 1 November 2026.
Target: existing `feature/portrait-kiosk-v2-next` dedicated Midtrans QRIS Sandbox
profile. This is a future extension of [BUG-027](BUG027-PAID-TO-PHOTO.md) and
[BUG-028](BUG028-PAID-STARTING.md), **not** evidence that the current UI has
already changed. The validated happy path remains PAID -> attempt one recovery
receipt print -> directly prepare the original camera session. Drive and
production remain OFF; AR-00 through AR-13 remain the top development priority.

## 1. Owner decision

If the **Recovery Ticket receipt printer does not respond** after a freshly
verified PAID transaction, show the **original Recovery Ticket on the kiosk
screen for 30 seconds**, with a **visible 30-second countdown** and an
immediately available **NEXT / LANJUT** button.

- Show the existing, original customer recovery QR **and the complete
  corresponding ticket code** in a legible, selectable/readable display. Do not
  substitute the short order reference, merchant payment QR, download QR,
  operator login QR, or any new/reissued token. The secret/code is for the
  current paid customer's recovery only.
- Display suggested customer guidance: "Printer tiket tidak merespons. Simpan
  tiket pemulihan ini dengan memfoto layar atau memindai QR. Jika sesi terputus,
  gunakan tiket ini untuk melanjutkan tanpa membayar lagi."
- Show the countdown clearly, for example **"Lanjut otomatis dalam 30 detik"**
  updating 30, 29, ..., 0. The **LANJUT / NEXT** button is visible and enabled
  throughout the display, so the customer can continue **before** 30 seconds.
- At zero, **automatically dismiss the ticket screen** and continue the same
  original paid session. If **LANJUT / NEXT** is tapped, perform the same guarded
  transition immediately; do not require an extra acknowledgment. Both exits
  must operate at most once (timer/tap race is idempotent).
- The 30 seconds is the **ticket display duration**, not a Midtrans payment QR
  expiration, payment polling delay, receipt printer wait timeout, or photo
  countdown. Begin it only after the failed/uncertain printer outcome qualifies
  for fallback and the authorized ticket view has actually appeared. A page
  rebuild/status poll must not restart or extend the original countdown.
- If the printer **acknowledges the one permitted submission**, retain the
  current happy path: no mandatory on-screen ticket page and no extra Next
  button before entering the camera.

## 2. Exact entry and exit guards

1. Enter fallback only after fresh authoritative settlement of the **same
   original PAID order**, its valid grant and current live customer ownership.
   The original raw credential must still be available securely in the current
   process. The existing printer submission can be absent/unavailable, throw an
   error, time out without acknowledgment, or end in `UNCERTAIN`; this qualifies
   for a screen fallback, **not** a second submission.
2. Preserve the original order ID, checkout key, grant, allocation operation,
   capture/fulfillment rights, receipt job, and print uncertainty state. Never
   create another payment, issue a fresh ticket, reprint the receipt, retry an
   uncertain transport job, or infer physical paper delivery from `SUBMITTED`.
3. The display runs as a bounded **current-visit privacy-sensitive overlay**
   rather than a general-purpose ticket viewer. Once NEXT is tapped or zero
   reached, wipe the displayed ticket QR/plaintext from live widgets and
   transient UI caches. Never show it to the next customer.
4. Enter camera only after the existing original allocation / local readiness /
   backend `STARTED` acknowledgment safety gates pass. If preparation remains
   pending when NEXT is tapped or countdown expires, hide the ticket and show
   the existing neutral **preparing photo permission** state until that exact
   transaction is safely ready. Do not leave a blocked camera or bypass guards.
   Permanent camera/storage failure retains PAID/OWED rights and uses existing
   recovery/remedy, not another payment.
5. A minimize, session privacy lock, expired ownership generation, app close or
   process restart immediately hides sensitive pixels and retires stale timer
   and NEXT callbacks. Never reopen an original private/restarted session or
   redisplay the ticket automatically without the existing valid ownership/proof
   rules. If the raw original ticket has been lost after a restart, do **not**
   mint a substitute or expose private media: retain the paid obligation and
   use the existing customer-proof/operator exception route.
6. The original ticket remains valid under the existing Sandbox **24 hours
   from order creation** policy; the 30-second view does not extend or reset
   this validity. A short numeric order label is never sufficient to redeem
   private media.

## 3. Revised PAID-to-camera flow

```mermaid
flowchart TD
  A["Midtrans PAID freshly verified"] --> B["Reserve one grant and one original recovery receipt job"]
  B --> C{"Receipt printer acknowledgment?"}
  C -->|"SUBMITTED"| G["Original photo allocation and STARTED confirmation"]
  C -->|"Unavailable / no response / timeout / UNCERTAIN"| D["Keep print UNCERTAIN; no reprint"]
  D --> E["Display same Recovery QR + full code, 30s countdown and NEXT"]
  E --> F{"NEXT tapped or 30s elapsed?"}
  F -->|"Yes, exactly once"| G
  G --> H{"Original session ready and STARTED acknowledged?"}
  H -->|"Yes"| I["Open camera; deliberate SIAP and countdown"]
  H -->|"Not yet"| J["Neutral preparing-photo state; retry original safe operation"]
  J --> H
```

The QR is the **customer Recovery Ticket**, not the Midtrans QRIS payment QR.
The ordinary successful receipt submission should still transition directly to
camera as before. Auto-navigation after fallback does **not** trigger a shutter.

## 4. UI / privacy requirements

- Use the existing native portrait UI/theme and recovery QR encoder; adapt to
  800x1280 and 452x900. Keep code text fully readable or scrollable without
  clipping. The NEXT button and remaining seconds must remain obvious on both.
- The customer should have a practical chance to photograph/scan the ticket on
  their own phone before NEXT or countdown expiry. Make no claim that scanning
  alone stores a reusable link: the code is a private recovery capability.
- Do not automatically copy the secret to the operating-system clipboard.
  Never save raw token, QR bitmap, screen capture or rendered ticket payload to
  files, GitHub, logs, SQLite, crash dumps, UI diagnostic previews, screenshots
  or telemetry. QA screenshots must use **synthetic nonredeemable** tokens only.
- Keep QR identities separate (payment / recovery / operator / DEMO / download)
  and preserve full-ticket claim validation, hash-at-rest, proof expiry, rate
  limiting, pause/minimize privacy and one-owner camera controls.
- If printer acknowledgement is given but paper is physically missing, the
  current transport acknowledgment alone cannot prove paper delivery; physical
  printer/paper tests remain a separate acceptance item. Do not silently claim
  that every missing-paper event is detectable in software.

## 5. Required implementation tests (NOT RUN)

1. Printer unavailable before send, printer transport exception, delayed/no
   acknowledgment and after-send uncertainty: exactly one original paid order,
   one receipt intent, **no second print**, and on-screen fallback entered.
2. No fallback after a successfully acknowledged receipt; PAID-to-camera remains
   direct with no mandatory NEXT or additional consent.
3. QR decodes to the exact **original synthetic** Recovery Ticket; the matching
   complete code is readable; 30->0 countdown is visible at both portrait sizes.
4. NEXT at 29 seconds (and near zero) advances once; untouched timer expires at
   zero and advances once; no capture happens without deliberate SIAP/countdown.
5. Repeated polls, widget rebuild, delayed callbacks and animation do not reset
   or extend the original 30-second window.
6. NEXT/timeout while STARTING or allocation acknowledgment is delayed keeps
   exactly the original operation and neutral readiness hold, then admits the
   original camera once safe. No second allocation or fee.
7. Minimize, lock, session-owner change, restart and late timer/print callbacks
   cannot expose the ticket or previous customer photos; old private/restarted
   sessions still require existing customer proof.
8. No fallback/token exposure for PENDING/EXPIRED/UNKNOWN, refund, mismatched,
   previously held or unproved reopened orders. Saved unpaid QR1/QR2/QR3 behavior
   stays unchanged.
9. Raw secret never reaches files, persistent journals, logs or exported QA
   evidence; one-time print semantics and PAID/OWED preservation remain intact.
10. Owner Windows + real configured 80 mm printer + Sandbox simulator trial must
    separately confirm the visible 30-second fallback, phone readability,
    NEXT behavior and successful camera admission. These are **NOT RUN**.

## 6. Handoff and scope

- **Requested now:** document the new requirement, its updated flow, and tests.
  **No application, tests, GUI, printer service, launcher or cloud deployment
  changes are authorized by this documentation-only request.**
- **Implementation later:** reuse current BUG-027 receipt worker and original
  in-memory customer ticket, native Kivy widget/QR rendering and BUG-028
  same-operation admission. First add failing focused tests, then a narrowly
  scoped runtime change, test native portrait views, one applicable full
  regression and matching Windows/Linux CI, and capture owner laptop/manual
  acceptance separately.
- Do not create a branch, merge to master, alter production payments, change
  Midtrans amount/renewal, weaken privacy/recovery, enable Drive or redo earlier
  verified AR/BUG work. Keep this item queued alongside active BUG-028 and
  existing AR-00–13 release gates; historical test results do not certify it.
