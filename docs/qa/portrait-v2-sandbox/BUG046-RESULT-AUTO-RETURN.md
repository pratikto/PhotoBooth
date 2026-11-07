# BUG-046 — automatic return from paid results after 30 seconds

8 November 2026 · Existing branch `feature/post-preview-qris-checkout`.
Base source: `5307e582485bca03c4e7acbb449c049151893695`.

## Owner report and approved correction

The owner ran the real-camera, synthetic-payment, no-printer/no-Drive laptop
trial and reported 11 checklist steps PASS and PILOT-03 NOT_RUN. Reported PASS:
PRE-01, PILOT-04/05/06/07, PRICE-01, PILOT-08/09/10/13/15. The exact laptop
commit and device metadata were not supplied. These are owner-reported scoped
observations, not an independently observed complete PP/PILOT acceptance run.
The QR demo label passed; the accompanying note says the results page cannot
return to the main page. Preserve both facts rather than changing PILOT-15 to FAIL.

The owner explicitly corrected the proposed manual finish action: **return to
the main Advertising page automatically after 30 seconds; no additional button**.
This applies to the post-payment `paid_delivery` result screen. It is a second,
separate display window after the Recovery Ticket's existing 30 visible seconds
or NEXT. It does not shorten the ticket opportunity or time out unpaid previews,
active capture, checkout or a different customer's session.

## Cause and implementation

The paid-result renderer had print/status controls but neither a return deadline
nor a `paid_delivery` inactivity rule. It could stay on private results indefinitely.
The current supervised pilot already has privacy retirement and protected Ads
admission; this change reuses those original paths rather than resetting a visit.

- Set one monotonic deadline when the paid-result page is first constructed.
  Show the remaining seconds in the existing status-label area.
- Keep the same deadline across status polling, button activity, redraw/resize
  and printer replies. This is a fixed result display window, not inactivity.
- At zero, hide private pixels immediately and return the supervised pilot to
  protected Ads, even when the original serialized worker is still busy.
- Persist the distinct `RESULT_TIMEOUT` lifecycle event using the existing local
  worker and authenticated lifecycle endpoint. It fences the old lease but does
  not request cancellation, create a refund, mark delivery complete or free the
  booth. Original PAID/OWED, media, proof, print and Drive journals remain intact.
- Give privacy retirement priority over late paid-delivery replies. A late
  printer/status result must not rebuild the old results page over protected Ads.
- Clear the UI deadline on exit; a new visitor still needs the original
  PREPARE/ACK gate. Busy or uncertain output continues to deny new admission.
  Incomplete development fixtures without that coordinator retain their protected
  hold; the actual supervised owner launcher installs the Ads coordinator.

No schema migration, original-order reset, new return button, receipt/strip
replay, merchant activation or change to legacy paid-before-photo behavior.

## Executed evidence

Before the fix, the new native journey reproduced the defect at both 452×900
and 800×1280: after advancing past 30 seconds the page was still `result`
instead of `advert` (one method, two failing subtests). The first console run
was hidden by Kivy logging; rerun with MIXED logging retained the actual assertions.

Focused final run: **3 methods PASS, zero failures/errors/skips, 11.917 seconds**.
Two native methods execute real Kivy widgets, original HTTP/service/photo/ticket/
paid-output code with synthetic devices. They check the 29.999/30-second boundary,
unchanged deadline on refresh/redraw, protected Ads, original PAID/OWED, no new
charge/cancel/receipt/strip, safe B admission and no old timer affecting B.
A blocked original print proves immediate privacy/Ads while busy, late-reply
suppression, persistent UNCERTAIN and denied B admission without replay.
The authenticated API method verifies RESULT_TIMEOUT retains the original paid
entitlement and does not cancel or release occupancy.

The initial slow-print test used `print_bitmap` against an adapter exposing
`print_image`; its barrier did not run (one test FAIL). Corrected the test to use
the actual original printer API; no product guard was weakened.

Final registered backend/native regression and matching-source CI: PENDING.
The boundary checks use a controlled monotonic clock; they are not a measured
30-second physical laptop result. No real paper, Drive, merchant or refund I/O.

## Owner retest after the published fix

1. Close the existing trial, preserve its folders and update the existing branch
   using the [quick start](PP07-PHYSICAL-QUICK-START.md).
2. Start a fresh trial with `Start-PostPreviewDeviceTest.ps1` and repeat the
   already working photo → synthetic payment → original Recovery Ticket route.
3. On the final results/QR demo page, observe the separate 30-second countdown.
   Do not close the app and do not press a manual finish button.
4. Confirm it returns automatically to Ads at zero and old photos/QR disappear.
   A status refresh must not restart the 30-second window.
5. Record this result separately as BUG-046 RETEST PASS/FAIL and capture the
   source SHA. Existing hardware/provider and full acceptance gates remain open.

## Reviewed sources and rollback

Reviewed root instructions/README, documentation index, current handover,
development protocol, architecture, owner decisions/status/bug/next-step entries;
post-preview product/security lifecycle and ticket/paid-output contracts;
physical quick start/UAT; the original preview/checkout UI, lifecycle API/store,
isolation/admission, worker and native journey fixtures. Latest owner correction
supersedes the absent result-return policy while preserving the ticket contract.

Rollback is a scoped inverse source commit on this branch. Never delete trial
roots or rewrite payment, photo, ticket or output journals to roll back the UI.
