# P3 preview redraw and first-use response — 2026-10-23

Branch: `feature/portrait-kiosk-v2-next`. Owner reports that the v2 camera
preview is very laggy while v1 is smooth, followed by a fuller Windows retest
and clarification that random page buttons are slow on first use and usually
smooth on subsequent uses. These are corrections within the approved P3 scope.

## Owner report audit

[Original report](owner-retest-2026-10-23.txt) is preserved byte-for-byte.
The directory's attributes preserve its Windows CRLF and empty-field spacing.
[Structured audit](owner-analysis.json): **36/40 raw checked**, twenty reported
cycles, Windows 11, 100% scaling, built-in laptop camera. HEAD, resolution,
camera index and speaker fields are missing. No exact-source acceptance is inferred.

| Item in original 40-item form | Interpretation |
| --- | --- |
| B03 checked | Preview explicitly reported very laggy in notes: **FAIL/OPEN**, raw checkbox preserved. |
| A02/B05 checked | Embedded camera cannot be unplugged; physical detach/reconnect remains untested. Minimize is a separate reported check. |
| D02 checked | Owner says CETAK UJI is inactive. Default-disabled behavior may be checked, but physical batch output is **not tested**. |
| B02, D03–D05 empty | Failed OR not tested; never automatically PASS. |
| A01 checked | Startup reported working; metadata portion incomplete. |
| A03/A04 and I01–I06 checked | Face and palm now owner-reported working at unknown HEAD; not acceptance of a later revision. |

The `Kapan lag terasa: tidak terasa` field also conflicts with preview/button
notes. Do not present this as all responsiveness gates passed. Existing Drive
checkmarks are owner-reported at unknown HEAD; they do not certify cloud deletion.

## Stage 1 — redraw correction

Source checkpoint **`0d08f07acc471c7776e5bc494c53c00f3d48f717`**.
v1's `MeongUI.update_live_frame` explicitly calls `preview.canvas.ask_update()`.
v2 reused a texture and uploaded new pixels without invalidating the canvas.
Assigning the same texture object does not emit an Image property change;
Kivy's idle loop only draws when `window.canvas.needs_redraw` is true. This
explains a reproduced source defect: new pixels can remain invisible until
another UI change. It does not establish every cause of the owner's device lag.

The fix requests redraw once per new prepared preview. Conversion remains in
the bounded worker; original camera resolution, raw pixels, mirroring policy,
countdown, sensor guards and v1 code remain unchanged.

The same real-widget regression was run with the baseline `507035b` method
and the fixed method. [Baseline FAIL](redraw-baseline-fail.txt),
[fixed PASS](redraw-fixed-pass.txt). Six alternating red/green/blue frames
must cause actual window flips; `glReadPixels` checks displayed pixels before
buffer swap. Labels stay unchanged, no touch/countdown is injected, and the
same GPU texture is reused. Polling the same packet does not force a redraw.
This tests presentation, rather than counting submitted/converted frames.

[Complete stage-1 regression](stage1-full-tests.txt): **350 PASS, zero skips**.
[Three-job source CI](https://github.com/pratikto/PhotoBooth/actions/runs/39931838768).

## Stage 2 — first-use preparation

Source checkpoint **`ef0fcb0e15f3c83178044631e84530b5b629a821`**.
The existing preview worker prepared CPU images, but GPU textures could still
be created on the first gallery action. Count/shutter/success audio handles
were also loaded on first use. The idle scheduler now uploads one ready strip
or loads one silent effect per turn. It never waits for an unfinished decoder,
does not play warmup audio, and pauses work outside idle/while minimized.
Close cancels its callback. First gallery actions reuse warmed textures.

The existing fallback remains available if the user opens the gallery before
warmup completes. This is not proof that all missed/slow taps are fixed;
native decoder retirement, sound playback and actual Windows input still need
device timings. Existing `Slow action` and `Performance` lines are in the log.

[36 focused tests PASS](first-use-focused-tests.txt).
[Final complete regression](final-full-tests.txt): **353 PASS, zero failures,
errors or skips**, including native public-model fixtures and dummy audio/video.
No actual customer camera, speaker, printer or Drive account was exercised.
Exact-source CI and runtime hashes are recorded in [verification](verification.json).

## Visual evidence

Twenty-four real Kivy captures at clean tracked source `ef0fcb0`, using synthetic
camera pixels/sensor hints and isolated local photo stores. All source reports,
PNG sizes and SHA-256 values were checked. Reviewed contact sheets:
[800×1280](contact-800x1280.png), [452×900](contact-452x900.png).
Originals/reports are under [screenshots](screenshots).
These demonstrate containment and controls, not live camera FPS.

## Windows run and focused retest

Close v2, then in the existing Windows PowerShell/virtual environment:

```powershell
git switch feature/portrait-kiosk-v2-next
git pull --ff-only origin feature/portrait-kiosk-v2-next
git rev-parse --short HEAD
Start-Process .\docs\qa\portrait-v2-preview-redraw\windows-checklist.html
.\.venv-kivy\Scripts\python.exe tools/run_portrait_v2.py
```

[Focused 16-item form with Submit](windows-checklist.html) has separate browser
storage and imports no old checkmarks. Enter the actual HEAD and device fields.
Most important: remain at the ready camera for **30 seconds without touching
anything or starting a countdown**, and check continuous movement. Then test
the first tap on each page, countdown, retake, palm, resize, minimize and twenty
complete cycles. Submit prepares text for manual paste into chat. Browser
checks include Submit, storage, unchecked print gates, download and 360px layout:
[results](form-browser-test.json). It supplements the full P3 checklist; it
does not silently close original open items.

For the built-in camera, B02's unavailable-camera guard can be checked in a
separate run with `$env:PHOTOBOOTH_CAMERA = "0"`, restoring it to `"1"` before
the next launch. This is a disabled-camera test, not a physical unplug test.

### Optional physical printer test

Being connected to Windows does not enable printing. Close v2 fully, then,
only when deliberately testing the operator's configured printer:

```powershell
$env:PHOTOBOOTH_V2_PRINT = "1"
.\.venv-kivy\Scripts\python.exe tools/run_portrait_v2.py
```

Choose copies, finish three photos/review, compose the strip, then press
**CETAK UJI** on the result page. The flag does not print automatically or
rewrite printer settings. Verify actual N sheets; SUBMITTED alone is not paper
confirmation. Do not automatically resend an uncertain batch. Leave original
D03–D05 empty until deliberately tested. For local-only runs restore
`$env:PHOTOBOOTH_V2_PRINT = "0"` before launch. No default or production
payment/scanner/discount/game/Drive activation is made by this correction.

If lag persists, send the newest log after `explorer .\data\diagnostics`,
with the page/button and whether this was its first use. BUG-013 stays OPEN for
Windows confirmation; BUG-014 is owner-reported working at unknown HEAD.

## Rollback checkpoints

- `507035b451ff9db84972b52b19a0f20d1271c542`: before both corrections; contains the reproduced redraw defect.
- `0d08f07acc471c7776e5bc494c53c00f3d48f717`: redraw fix without additional idle preparation.
- `ef0fcb0e15f3c83178044631e84530b5b629a821`: both corrections, 353-test source checkpoint.

No reset, force push, new branch, merge, master/v1 modification, model change,
remote deletion or hardware transaction was performed. Any rollback preserves
local photos/diagnostics and uses an ordinary reviewed revert on the same branch.
