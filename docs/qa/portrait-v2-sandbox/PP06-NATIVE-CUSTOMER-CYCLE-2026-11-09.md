# Native A → B → A original-customer cycle

9 November 2026 · `feature/post-preview-qris-checkout` · base
`0e70b4b02112f6ef03d71422df126076a6ea2c6b` (pushed and remote verified).

## Connected behavior actually exercised

N28 drives the existing native Kivy shell, real local authenticated HTTP backend,
photo worker, durable journals, original proof services, printer dispatcher and
paid Drive fixture at both 452×900 and 800×1280. No new service or UI is introduced.

A selects two designs / 2+1 copies, takes six photos and saves the original CCP.
A's independent simulated settlement opens the mandatory original ticket;
NEXT leads to verified synthetic folder binding and automatic 2+1 dispatch.
A's result deadline returns to protected Ads. B's Photo action requires A's
ACKED isolation and a fresh tutorial/cart, then B takes one photo. A's valid
original proof returns WAIT while B owns the camera; the native claim popup
cannot open over B. B explicitly cancels through the native control. On Ads,
A opens the actual recovery popup, enters the original CCP, presses VALIDASI
TIKET, and reacquires the original lease only after B's exact ACK.

The test verifies the input field is wiped, the popup closes, the original
entitlement/group/folder and six photo hashes are identical, the dismissed
ticket is not redisplayed, and existing submitted strips are not resent after
original delivery preparation. One original charge, one receipt and 2+1 sends;
PAID/OWED retained and physical_paper_verified remains false. Returning to Ads
is not a claim that paper or digital delivery has completed.

## Results and evidence limits

- New N28 method: PASS at both portrait sizes, 10.457s, zero failures/errors/skips.
- Existing admission/isolation/claim affected scope: 56 PASS in 19.478s, zero
  failures/errors/skips, exit 0. Count includes imported original fixture tests.
- Complete registered native regression: 74 PASS in 168.605s, zero failures,
  errors or skips; process exit 0. Registered backend regression: 598 PASS in 180.435s, zero failures,
  errors or skips; process exit 0. Initial command-selection wrapper exited
  before running tests because an unnamed workflow step had no name key;
  corrected selection to use get(name), then executed the original command.
- Existing late-print response / timeout / uncertain-receipt regressions are
  included in that final native group; no uncertain journal is reset.
- Linux Python 3.12, Kivy 2.3.2, cryptography 49.0.0; offscreen SDL/software GL,
  dummy audio, synthetic camera/provider/paper/Drive. Actual POS80, Windows
  device interaction, phone/cloud ACL, merchant settlement and full acceptance
  are NOT_RUN. No raw CCP/ticket/private image artifacts are published.

This closes a connected native regression gap beyond the earlier separate
A→B and A→A tests. It is partial software evidence for PP-036/037/063/070 and
PILOT-18–21, not full stage-2 physical/operational acceptance. Earlier eleven
owner-reported checks are preserved.

[Machine-readable results and source hashes](native-customer-cycle-2026-11-09/verification.json).

## Next implementation boundary

The post-preview owner launcher remains explicitly MOCK-only, backed by
CheckoutFixture. PrivateCheckoutService, OriginalMockClaim,
OriginalMockIsolation and OriginalPilotAdmission reject real provider profiles.
Actual post-preview Midtrans work must integrate a separately guarded profile,
reuse PostPreviewPayments / MidtransSandboxClient / PostPreviewClient / API,
keep credentials exclusively in a backend process, and wire protected escrow,
trusted exact-worker readiness, paid ticket/delivery and original release before
enabling payable UI. Removing a mock-only guard alone is not integration.

The existing real Sandbox transport has offline JSON/HTTP contract tests at
`tests/test_post_preview_payments.py::MidtransPostPreviewContractTests`; these
are not merchant tests. No second transport or legacy paid-first launch is a
substitute for this still-unmounted path.

Safe metadata inspection found no ignored local_settings.py and no existing
Midtrans merchant/key, Apps Script URL/token or printer route environment
configuration. This executor has no configured secret binding or outbound
identity. Actual merchant tests need the owner's Sandbox credential pair in
secure settings; actual paper/cloud/device tests require the original scoped
opt-ins and owned equipment. Never ask for keys in chat.

Further code remains: guarded post-preview provider mounting, supported full
Windows/Ubuntu recovery/vault integration, real refund/status integration and
operational release packaging. Full two-hour simulation and four-hour device
qualification are not complete. None is represented as PASS by N28.

Rollback is test-only scoped removal; preserve all operational data and journals.
