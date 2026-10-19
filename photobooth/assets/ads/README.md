# Local advertising media

> **Release provenance:** Assets are in the source pre-release [v1.0.0](https://github.com/pratikto/PhotoBooth/releases/tag/v1.0.0), from prior `feature/kivy-gui` work. Keep media/codecs, audio speaker response and printer/QR paper quality distinct from simulated CI; no change to asset bytes in this documentation cleanup.

> **CURRENT (2026-10-19, `master` / immutable `v1.0.0`):** These are local/offline ad assets for **both idle and muted payment placements**. The owner subsequently reported video ads in both placements PASS (BUG-002), but a controlled codec/hardware matrix is not yet recorded. Videos remain local and excluded from Git; the planned per-machine Google Drive ad sync (FEAT-004) is **not implemented**. This file describes bundled media only.

The checkout includes three small still-image posters. The idle placement uses
the first; payment has its own playlist with the other two. Videos remain on
the booth computer and are excluded from Git, including original and converted
copies. They are not required to start the app.

To use a local video, edit `playlist.json`, or copy it outside the checkout and
set `PHOTOBOOTH_AD_CONFIG` to that copy. Change an item's `file` to a local MP4
and optionally set `poster` to a local image. Paths resolve beside the JSON.
The existing `placements` array selects `idle`, `payment`, or both.

Example item (install the referenced files locally):

```json
{
  "id": "venue-video",
  "file": "venue.mp4",
  "poster": "venue-poster.jpg",
  "placements": ["idle"],
  "start": "2026-10-17T00:00:00+07:00",
  "end": "2026-11-01T00:00:00+07:00",
  "hours": ["09:00", "22:00"]
}
```

Images use `seconds` (default 8). Videos rotate at their end; H.264/yuv420p MP4
is a portable choice for the installed ffpyplayer decoder. Missing or broken
files are skipped. The player shows Meong branding if no item can play.
Sample posters are demonstration material; they do not imply sponsorship.
