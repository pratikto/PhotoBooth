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

## Final source and evidence

Functional source **`4237d3f0e435245f0bce4b3ee5b158105f6af9ad`** is pushed and
remote-verified on the authorized branch. [Source hashes and environment](qr-polling-tested-source.json)
identify the two runtime changes, tests and unchanged related services.

- [Full local regression](qr-polling-full-tests.txt): **933 run / 930 PASS /
  3 optional native palm-assets SKIP / zero failures/errors**, 289.540s. The
  skipped cases are native camera-recovery palm inference, v2 palm countdown
  and standalone palm inference; none is a QR/payment test.
- Matching-source [CI 40614355442](https://github.com/pratikto/PhotoBooth/actions/runs/40614355442):
  **all three jobs SUCCESS**. Sandbox group: 182 PASS/zero skips, including all
  seven new regression cases. Windows: 55 portable and 103 dummy-audio checks
  PASS. The pure job skips one Kivy-dependent integration (covered locally);
  native GUI skips its optional palm-assets case. [Exact summaries](qr-polling-ci-result.json).
- Ten exact-source native PNGs pass phase, dimensions and SHA256 checks at
  800×1280 and 452×900. Both WAITING images were visually reviewed: QR/centered
  logo, amount, status and actions fit without observed clipping. Actual
  screenshot QR pixels independently decode the exact nonpayable fixture.
  [Pixel/hash results](qr-polling/qr-pixel-validation.json),
  [800px view](qr-polling/02-waiting-offline-fixture-800x12800001.png),
  [compact view](qr-polling/02-waiting-offline-fixture-452x9000001.png).
  The initial metadata checker incorrectly expected no checkout phase during
  photo consent; consent correctly retains RESERVED. Only that checker
  expectation was corrected; no app change or repeat full suite was needed.

These fixtures verify the reproduced source defect, not the unidentified cause
on the owner's device. Actual merchant/simulator, Windows/Ubuntu hardware,
phone readability and real-time idle soak remain separate acceptance. No live
order or credential was used and no journal was reset.

## Windows update and owner retest

Close the Sandbox GUI/launcher so its loopback backend also loads the update.
Keep the existing Kivy environment, saved settings and all pending-order data:

```powershell
git pull --ff-only origin feature/portrait-kiosk-v2-next
python tools/run_portrait_v2_sandbox.py
```

Let the current verified PENDING screen poll without tapping. Its existing QR
should remain visible; provider-confirmed payment or expiry still removes it.
If it disappears, record the on-screen status and tested HEAD; no key, payment
journal or photo is needed. The previous report does not identify whether expiry,
network verification, image loading or this source defect occurred on the device.

Resume the existing pending order rather than resetting its journal. This fix
cannot recover an original action URL already overwritten before updating;
do not infer a replacement image reference or force another charge. The shared
backend correction also applies to clients using it; v1 GUI/launcher, Drive,
Apps Script, payment admission and original image/branding renderers are unchanged.
No Google deployment or real payment is part of this update.
