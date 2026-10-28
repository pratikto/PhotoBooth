# BUG-021 — pending QR image identity during status polling

## Scope and review — 28 October 2026 (Asia/Jakarta)

Owner reports that the image disappears while the GUI stays on QRIS Sandbox;
elapsed time and displayed status are unknown. Base/local and remote HEAD are
`a6d7da7469dcc4c73ff49ae024f48362c4908f2d`, on the authorized
`feature/portrait-kiosk-v2-next` branch. Read-only reference refresh confirms
QRIS `3cc8a8e` and v1 Kivy `38fbaa5`; neither is switched or merged.

Reviewed AGENTS, documentation index/protocol, handover, Sandbox runbook,
technical design, bug register and preceding key/settings/logo evidence. Root
README, architecture, decisions, feature status, roadmap/specification, backlog,
test ledger and branch audit were reviewed comprehensively in this continuing
conversation. Inspected the shared backend/evidence/store, durable client/session,
v2 worker/image cache, polling/timeout rules and HTTP/native fixtures.

An offline reproduction proves that a verified action URL is overwritten with
a derived v2 URL when a later PENDING status omits actions. A v4 action fixture
therefore changes image identity despite retaining the same unpaid order and
one charge. A failed reload then leaves no image. This proves a source defect;
it does not establish the exact cause on the owner's laptop. Expiry, settlement
and unavailable verification are separate legitimate reasons to withhold a QR.

Midtrans's [QRIS reference](https://docs.midtrans.com/reference/qris) documents
image URLs in actions, including a v4 image action with its own image reference.
Do not guess another API version/reference or treat a QR-image token as the
provider transaction ID.

## Bounded plan — recorded before code

Reuse the existing backend and allowlist: when independently verified PENDING
evidence omits the QR action, retain and revalidate the existing stored image URL.
An explicit replacement action still undergoes the original method/URL checks;
an invalid action must not be hidden by the cache. Derive the existing legacy v2
endpoint only if no image URL has ever been saved, preserving lost-create-response
recovery. No schema, pricing, merchant, expiry, state, permit or journal change.

Add regressions for repeated missing actions, durable restart, explicit valid
replacement, untrusted actions/cache and the existing missing-response fallback.
Exercise automatic native polling through the actual HTTP/client/SQLite path,
requiring stable visible pixels, one image load/charge and unchanged identities;
provider expiry must still remove the QR. Capture and review the native WAITING
screen at the two required sizes. Run focused checks, one final full regression
and matching-source CI; record exact source/results and device/provider limits.

No merchant requests, credentials, customer files, archive traversal, payment
replay, print, Drive operation or Google deployment. Roll back scoped source
only after inspection, preserving all settings/orders/journals. Already overwritten
URLs cannot be reconstructed from this change: do not delete a journal or create
a replacement order to disguise that state. Actual on-device retest is pending.

## Initial verification

- [Before correction](qr-polling-before-tests.txt): seven targeted cases, five
  failures, zero errors/skips. The actual native automatic poll loses the image
  while retaining WAITING/PENDING; backend restart/replacement also lose the URL.
  Existing invalid-action and terminal-state guards already pass.
- [After correction](qr-polling-focused-tests.txt): **182 PASS**, zero
  failures/errors/skips, 14.158s. Six new durable-backend cases and one native
  automatic-poll case pass alongside the existing Sandbox/QR group. Five forced
  automatic polling deadlines retain one image load/charge and the same
  order/key/pixels; authoritative expiry still removes the image. These are
  deterministic polling checks, not a real-time soak or merchant test.

Final full regression, exact-source native captures and matching-source CI are
pending at this checkpoint; results will be appended after execution.
