# Copy the active Sandbox QRIS link

28 October 2026 (Asia/Jakarta). Owner requests a GUI button to obtain the QRIS
link for pasting into the Midtrans web simulator, on the existing
`feature/portrait-kiosk-v2-next` branch. The owner explicitly confirms this
feature is **Sandbox only**; ordinary/MOCK/production modes have no copy action.
Base remote/local source was refreshed to
`959242ddc47a3aacac7e759afec2076f288a3dc9`; functional source is
`39e8c32967451423f3c2749570c04a97badd1248`. No new branch.

## Use on Windows

```powershell
git switch feature/portrait-kiosk-v2-next
git pull --ff-only origin feature/portrait-kiosk-v2-next
python tools/run_portrait_v2_sandbox.py
```

Use the existing Windows Kivy environment and local Sandbox credentials/settings.
Choose templates/copies, enter Sandbox and confirm the test order. On
**MENUNGGU SIMULATOR**, press **SALIN LINK QRIS**. The GUI reports
“Link QRIS tersalin. Paste di simulator Midtrans.” Paste into the QRIS URL field
at the [official simulator](https://simulator.sandbox.midtrans.com/v2/qris/index)
and submit the simulated payment there. Existing automatic status polling or
**CEK STATUS** waits for the backend's verified payment state.

The button copies the exact current provider image-action URL, including its
original API version/image reference. It does not copy the QR payload, guess a
new URL, open a browser or submit a simulator transaction. Failed clipboard
access reports a retry/terminal fallback. The terminal still provides the
verified image URL and official simulator link.

The action is offered only for a verified PENDING Sandbox order in WAITING.
Missing/untrusted URLs, uncertain verification, cancellation and paid/finished
states cannot copy. Existing page revision, suspend, close and worker-busy guards
also apply. Missing image pixels do not prevent copying an otherwise valid URL.
Payment authority, quotes, order creation, journal and single-use photo admission
remain in the original backend/session. Dedicated trial printer/Drive stay off.

## Reuse and validation

Reuse the current native `_action` widget/lifecycle and Sandbox view; validate
through the existing `sandbox_qr_url` from QRIS reference `3cc8a8e` (read-only
remote check confirms that reference unchanged). Use Kivy's desktop Clipboard API.
Only the v2 adapter/views and their existing test modules change; the shared
backend/client/session, QR renderer and launcher are unchanged.

Focused command: `python tools/run_kiosk_unittests.py test_kiosk_v2_sandbox test_kiosk_v2_sandbox_widgets`.
**21 PASS, zero errors/failures/skips.** New checks cover exact active URL,
malformed/foreign URLs, phase/mode/verification guards, old button retirement,
clipboard failure/retry, missing QR pixels and unchanged order/one charge.
Linux Python 3.12.14, existing `.venv`, Kivy SDL offscreen/software OpenGL,
dummy audio; fixture API runs in process. This executor requires its supported
network-enabled command context for the fixture's asyncio socket/event loop;
the restricted attempt was interrupted, not counted as PASS. No merchant call
or real payment was made.

The full discovery run completed **937 run / 864 PASS / 73 SKIP / zero
failures/errors**, 209.360s. The 71 disabled legacy GUI cases were then run
separately with `PHOTOBOOTH_TEST_GUI=1`: **69 PASS / 2 SKIP / zero failures/errors**,
145.583s. Across both runs, **933 of 937 unique cases PASS; four remain SKIP**
(three optional native palm-assets checks and one legacy native-video opt-in).
[Full discovery output](copy-link/full-tests.txt) ·
[GUI complement](copy-link/gui-complement-tests.txt) ·
[Focused output](copy-link/focused-tests.txt).

Six exact-source native WAITING/success/clipboard-error screenshots at
800×1280 and 452×900 were reviewed. Both WAITING QR screenshots decode to the
nonpayable fixture. [Hashes/source/screenshots](copy-link/tested-source.json).
Feedback captures mock the clipboard API, not Windows clipboard-to-browser.
[Matching functional-source CI](https://github.com/pratikto/PhotoBooth/actions/runs/40641479742)
has navigation and Windows jobs SUCCESS; the desktop job is still running.
No final CI success is claimed yet.

Windows clipboard-to-browser and actual merchant simulator acceptance remain NOT_RUN here. Local fixture success does not establish provider settlement.

## Rollback

Inspect and revert functional commit `39e8c32` only if needed. Preserve all
merchant settings, orders, service grants, journals, photos and print/Drive state.
Do not create a replacement order or erase a journal to test clipboard behavior.
