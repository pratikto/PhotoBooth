# Unpaid preview and synthetic payment clarity

9 November 2026 · branch `feature/post-preview-qris-checkout` · base
`af510d0b8fee88413a626b0d9b6377fd7ca8bc44` (remote verified before work).
Fresh checkout; no pre-existing project process, user edits or operational data.
Excluded `old` was not inspected or modified.

## Delivered bounded increment

The unpaid per-design and final preview inherited `STRIP KAMU SUDAH SIAP` from
shared paid/local result presentation. A small brand hook now supplies
`PREVIEW FOTO` / `BELUM DIBAYAR • BELUM DICETAK` only for the private flow.
Existing capture/review controls, design previews, totals and checkout remain.
Legacy photo-page brand values remain the original defaults.

The MOCK-only checkout service deliberately supplies a white payment fixture
image. Its native page now displays a readable simulation card instead of that
blank image: no scan/transfer, actual QRIS not connected, and the existing
SIMULASI PAID control continues the owner trial. A fixture without that control
shows a status-check explanation instead. This changes presentation only; no
mock click can become merchant settlement authority. HTTP uncertainty retains
the original protected hold message and cannot create a replacement charge.

## Actual verification

- Before: one new native method, two portrait subtests FAIL on inherited heading;
  3.501s, no errors/skips. This did not yet reach the placeholder assertion.
- After UI change: expected hold assertion initially FAIL because a provider
  outage preserves last observed PENDING in the backend. Corrected the fault
  fixture to interrupt the actual HTTP boundary (the intended service hold);
  first fixture patch targeted nonexistent `get`, then corrected to `request`.
  No payment guard or expected charge-count assertion was weakened.
- Corrected focused native method: PASS at 452×900 and 800×1280, 4.357s,
  zero failures/errors/skips. It drives six original captures, Rp25,000 preview,
  real local HTTP/journal checkout and HTTP-loss hold, retaining one charge and
  no unpaid fulfillment.
- Four-module native affected regression: 35 PASS in 146.884s, zero failures,
  errors or skips; process exit 0. Original paid automatic output, ticket,
  timeout, Ads/proof handoff, both portrait layouts and actual launcher exercised.
- Four clean native screenshots reviewed, one fresh offscreen process per size:
  [unpaid 452×900](preview-payment-clarity-2026-11-09/unpaid-452x900.png),
  [payment 452×900](preview-payment-clarity-2026-11-09/payment-452x900.png),
  [unpaid 800×1280](preview-payment-clarity-2026-11-09/unpaid-800x1280.png),
  [payment 800×1280](preview-payment-clarity-2026-11-09/payment-800x1280.png).
  Synthetic black photo pixels; no CCP/ticket screenshots or real customer media.
  Both capture drivers exited zero. These are native Kivy views, not browser mocks.

Linux / Python 3.12 / Kivy 2.3.2 / cryptography 49.0.0; offscreen SDL,
software GL, dummy audio, synthetic camera/provider/printer/Drive only. Initial
native startup was blocked by read-only default Kivy home; fixed runtime setup
with a workspace KIVY_HOME. Actual Windows/Ubuntu devices, merchant Sandbox,
refund, paper, cloud and full stage acceptance remain NOT_RUN or BLOCKED.

## Reconciled finite continuation

| Status | Concrete scope |
| --- | --- |
| SUDAH SELESAI | Published automatic strips after ticket/verified URL at 0fe3734; result timeout at fc8853b; this bounded preview/simulation presentation correction |
| BELUM TERHUBUNG | Actual post-preview Midtrans host/profile; complete platform-protected worker/vault restart; real refund/customer-status mounting |
| BELUM DIVERIFIKASI | Comprehensive native A→B→A, all PP/UAH full acceptance, measured complete two-hour simulation/four-hour device campaign |
| BLOCKED EKSTERNAL | No configured merchant/Drive secrets or outbound identities on this executor, no owned POS80/camera deployment device, merchant refund eligibility and legal/production signoff |

Preserve the owner's 11 reported checks; request only changed or missing device
observations. No new feature scope, production activation, real refund or cloud
deployment/deletion is included. Next: native complete A→B→A using existing
admission/claim/worker fixtures, then guarded post-preview merchant integration.

Reviewed authority: AGENTS and development protocol; current index/handover,
feature/bug/backlog and implementation checkpoints; architecture; STAR roadmap;
PP decision ledger, owner flow, security/state, refund/lost-proof and escalation;
canonical acceptance matrix; full test plan, quick start, Windows UAT; original
automatic-print report/verification. Historical banners retain original scope.
Source seam reviewed: photo_views, private preview/checkout app/service,
CheckoutFixture, actual owner launcher/runtime tests and native journeys.

Rollback: scoped inverse of the presentation hook/card and associated test.
Preserve all media, leases, PAID/OWED, print/provider/Drive/credential journals.
