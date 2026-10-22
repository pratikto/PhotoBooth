# Windows MULAI FOTO crash — 2026-10-22

Branch: `feature/portrait-kiosk-v2-next`. Starting reference:
`6dc1f88738fecf0eb9eed4d405f7d95c10ae04db` (contains the reported regression).

## Owner report and diagnosis

The app exits after **MULAI FOTO**. Supplied log records Python **3.12.10 x64**,
Kivy **2.3.1**, kivy_deps.sdl2 **0.8.0**, ffpyplayer **4.5.3**, Intel Iris Xe.
The raw log contains local personal paths and is not republished here.
Relevant sanitized sequence:

```text
Meong v2 WAV provider=SDL2 (idle channel recovery) failed
kiosk_v2/mixer.py: mixer = ctypes.CDLL(None, handle=module)
Python312/Lib/ctypes/__init__.py: if '/' in name or '\\' in name:
TypeError: argument of type 'NoneType' is not iterable
ffpyplayer: Channel layout change is not supported
ffpyplayer: Audio thread error: Not yet implemented in FFmpeg, patches welcome
```

The regression was introduced by the previous idle-channel correction. On
Windows, CPython 3.12 validates the DLL **name even when a valid existing handle
is supplied**. The previous Linux tests accepted `None` and missed this branch.
After the Python exception, automatic SoundLoader fallback constructed a second
FFmpeg WAV player, following advertising video, and the supplied log records its
native audio channel-layout error. There is no Python GUI traceback after that
native error; the owner reports process exit. Do not characterize this as a
missing dependency or ask the operator to rebuild the environment.

## Correction

- Supply `SDL2_mixer.dll` together with the existing 64-bit HMODULE. Keep
  GetModuleHandleW and c_void_p; no new DLL search or audio device is introduced.
- Default Windows WAV fallback remains SDL2. If the channel-recovery wrapper
  fails, try plain SoundSDL2. If neither SDL path loads, return unavailable audio
  and keep the GUI usable instead of automatically opening the failing FFmpeg
  fallback. An explicit KIVY_AUDIO override remains respected.
- Advertising retains its own video decoder/audio. No shared ad-player, layout,
  template, game, payment, scanner or production transaction code changes.

The plain SDL fallback can still exhibit the earlier muted-channel limitation;
the normal corrected wrapper retains idle-channel recovery. Do not count a
fallback-only test as repeated-use speaker acceptance.

## Reproduction and verification

Before the fix, a faithful Windows CPython name-validation regression reproduces
**the exact TypeError**. Two fallback-policy tests also fail; explicit override
and missing-module guards already pass. [Before-fix transcript](before-fix-tests.txt).

After the fix:

- **62 focused tests PASS**, no failures/errors/skips. Includes Windows-only
  branch simulation, 64-bit handle preservation, no fallback DLL search, safe
  fallback/no-SDL policy and explicit override.
- Native default WAV load/play selects SDL without invoking SoundLoader.
- Actual Kivy **MULAI FOTO** and tutorial-continue button callbacks with audio
  enabled complete **five visits** through tutorial/gallery/return without
  closing the GUI or invoking FFmpeg WAV fallback (Linux dummy output).
- Native **20-cycle** post-mix PCM regression still passes, preserving playing ad
  gains and silence after close.
- **297 complete regression tests run: 295 PASS, 2 optional palm-model skips,
  zero failures/errors**. **44 Kivy-independent tests PASS** in a separate run.
- Compile and diff checks PASS. [Focused](focused-tests.txt),
  [complete](full-tests.txt), [Kivy-independent](pure-tests.txt).

Twelve fresh screenshots with **PHOTOBOOTH_AUDIO=1** reviewed at **800×1280** and
**452×900**: advertising, invitation, tutorial, gallery/cart, game preview. Main
CTAs and previews remain visible and the transition to tutorial completes.
[PNGs/manifests](screens/) record base HEAD 6dc1f88 plus tracked corrections;
[exact rendered source hashes](rendered-source-sha256.json) preserve provenance.
These are Linux synthetic captures, not Windows display/speaker acceptance.

A dedicated **windows-latest / Python 3.12** job now installs genuine Windows
Kivy/ffpyplayer providers and runs DLL/default-WAV plus 20-cycle native PCM tests
with SDL dummy output. **Verified exact-SHA CI**:
[run 39742760872](https://github.com/pratikto/PhotoBooth/actions/runs/39742760872)
on `471bbd9064f6fbf15264c15cc5f1fb3ffbd52144` completed **SUCCESS**; all **three
jobs SUCCESS** independently checked. The Windows job completed **29 audio
tests, all PASS**, including real named-DLL/default-WAV loading and twenty
native PCM cycles. Installed Kivy 2.3.1, SDL dependency 0.8.0 and ffpyplayer 4.5.3
match the versions relevant to the owner's log. [Windows transcript extract](windows-ci-tests.txt),
[run metadata](39742760872-run.json), [job/step metadata](39742760872-jobs.json).
This is genuine Windows execution with a dummy output device; physical speaker
and Windows touchscreen/advertising-codec acceptance still need the owner test.

## Checkpoints and acceptance

- Corrected code checkpoint: `471bbd9064f6fbf15264c15cc5f1fb3ffbd52144`, pushed to
  the required branch and remote HEAD verified. All three CI jobs PASS above.
- Final CI-evidence documentation commits change no application source.
- Before this fix: `6dc1f88`, **known to contain this crash**.
- Last owner-tested pre-channel-recovery reference: `9a9e18e`, with the older
  repeated-audio/short-window failures; it is not a complete accepted rollback.
- A rollback must be a reviewed revert on the same branch. No reset, force-push,
  master change, merge or new branch is performed.

Close the GUI, update the existing Windows checkout, then test:

```powershell
git switch feature/portrait-kiosk-v2-next
git pull --ff-only origin feature/portrait-kiosk-v2-next
git rev-parse --short HEAD
python tools/run_portrait_v2.py
```

- [ ] **First gate:** press MULAI FOTO; tutorial opens and the app stays running.
- [ ] Music and one click are audible; continue to gallery, then return to ads.
- [ ] Repeat at least 20 visits, including image/video ads; no exit or disappearing
      sound. Video uses source audio; image uses GUI music.
- [ ] Resize and swipe still work; minimize/restore/close leave no duplicate sound.
- [ ] Payment, scanner, real discounts and production transactions remain inactive.

The [clickable retest form](../portrait-v2-retest-9a9e18e/windows-checklist.html)
still includes Submit Hasil. Record the actual updated HEAD, then paste its
prepared prompt into chat. **Physical owner acceptance remains OPEN.**
