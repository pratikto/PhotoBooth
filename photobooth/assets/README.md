# MEONG PHOTOBOOTH brand assets

> **Release provenance:** Assets are in the source pre-release [v1.0.0](https://github.com/pratikto/PhotoBooth/releases/tag/v1.0.0), from prior `feature/kivy-gui` work. Keep media/codecs, audio speaker response and printer/QR paper quality distinct from simulated CI; no change to asset bytes in this documentation cleanup.

> **CURRENT (2026-10-19, `master` / immutable `v1.0.0`):** This is the active Meong logo asset for Kivy headers and new customer **folder-access** QRs. The approved source PNG and branding hash below are unchanged; the DEMO payment QR remains unbranded/non-payable. Logo artwork test history is archived in [QA](../../docs/qa/branded-qr.md).

`meong_photobooth_vivid.png` is the user's final uploaded
**Bright pixel camera-cat with colorful trail(3).png**, preserved byte-for-byte.
It contains the camera-cat, bright pink/lilac/yellow/cyan/peach/mint trail, and
the complete **MEONG PHOTOBOOTH** wordmark. SHA-256:
`dc1866b6e9cac905a08fec4019f971bb6daa6d243c51e13b23d082027646f61b`.

`photobooth/branding.py` selects this asset by default for every GUI header and
new transaction-folder QR. It trims surrounding white space only for display;
it preserves the uploaded PNG. Header display crops keep the full width of the
wordmark, and pixel artwork uses nearest texture filtering. An optional
`PHOTOBOOTH_LOGO_PATH` overrides the default with another local file.

`meong_photobooth.png` is the earlier grayscale-trail artwork retained as a
fallback. Payment-demo QRs remain plain. The folder QR includes the full logo
on its centered plate, with independently checked decoding and a four-module
white scan margin. `monochrome=True` dithers only the inserted artwork for
thermal compositions; the QR data matrix is never blurred or dithered.

See [audio/README.md](audio/README.md) for the shipped music and sound cues.
