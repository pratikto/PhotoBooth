# Centered Meong logo on the v2 Sandbox payment QR

## Owner scope and review — 28 October 2026 (Asia/Jakarta)

The owner supplies a QRIS Sandbox screen and asks for the same centered Meong
logo as the Drive download QR. This authorizes a v2 presentation change, without
changing payment data, merchant credentials, provider requests or payment
authority. Verified base/remote: `4b080ce1997956a0fe57b09e544ff29126d201c0` on
`feature/portrait-kiosk-v2-next`. Reference tips remain `3cc8a8e` (QRIS) and
`38fbaa5` (v1 Kivy); neither branch is switched or merged.

Read the current AGENTS, protocol, documentation index, Sandbox runbook and
technical contracts. The root README, architecture, decisions, roadmap,
feature/bug status, backlog, handover, test ledger, visual/provenance and branch
audit were reviewed in this continuing conversation; later saved-settings and
key-format corrections remain in force. Inspected the existing Drive QR
renderer/logo, original provider-image boundary, v2 worker/view/cache,
HTTP/native fixtures, QR tests and capture helper before editing.

## Bounded plan (recorded before code)

Reuse the existing `qr_code.create_qr_image` renderer and approved full Meong
artwork. Decode the downloaded provider image locally, render the exact decoded
payload with the existing level-H, centered plate, quiet-zone and mask checks,
then verify that the result still decodes identically. Never encode the image
URL as payment data, trim a decoded payload, or modify a downloaded original.
If decoding, asset loading, generation or validation fails, retain the original
image. Non-Sandbox/MOCK images retain their original behavior.

Run this only on the existing single-flight Sandbox worker, cached once per
order/image identity. Use nearest texture filtering like the Drive result QR.
The original image downloader, raw simulator URL, backend/client/journal,
quotes/grants, no-replay and v2 printer/Drive-off isolation stay unchanged.

Before editing, the existing renderer generated and independently checked a
40-character fixture plus 192/312-character numeric-heavy fixtures at full
size and 180px. A 352-character mixed fixture could not pass its checks, which
supports retaining the unmodified provider image as a fallback. These are
synthetic feasibility observations, not real merchant/phone acceptance.

Validate exact pixel-decoded payload equality, centered approved artwork,
failure fallback, no extra downloads on polls and unchanged order identity.
Review actual native captures at 800×1280, 452×900 and the owner's compact shape;
decode the screenshot QR pixels. Run focused checks, one final complete local
regression and matching-source CI. Use only nonpayable fixtures; do not read
private settings, create a merchant payment, print, upload or touch `old`.

## Results

The v2 adapter directly imports the existing renderer; no logo drawing or QR
encoding algorithm is duplicated. An AST comparison excluding docstrings proves
the Drive renderer implementation is unchanged. Its docstrings now describe the
new v2 caller. The full approved artwork and original downloader remain unchanged.

- [Pixel/shared QR checks](qr-logo-pixel-tests.txt): 19 PASS, zero skips, 3.274s.
- [Focused Sandbox/native/QR regression](qr-logo-focused-tests.txt): **175 PASS**,
  zero failures/errors/skips, 11.383s. The native check uses 800×1280, 452×900 and
  640×880, with the same order and only one image load across status checks.
- [Initial 172-case result](qr-logo-initial-tests.txt) and
  [isolated diagnosis](qr-logo-native-diagnostic.txt) retain a one-scale OpenCV
  false negative at 277×277 after compact resize. The exact same painted pixels
  decode identically with the repository's existing strict screenshot reader
  (bounded nearest 1×/2×/3× views). Its blank/occluded negative tests still fail
  as required. That reader is reused only for screenshot/native tests; no runtime
  QR data or payment state was changed to satisfy the test.
- [Source/artwork hashes](qr-logo-tested-source.json) identify the tested files.
  Final full regression, exact-source captures and CI are pending.

Physical phone readability, actual merchant simulator behavior and device
acceptance remain separate. Roll back only scoped source after inspection;
preserve all credentials, orders and photo/Drive state. The original image is
intentionally retained when local branding cannot be verified.
