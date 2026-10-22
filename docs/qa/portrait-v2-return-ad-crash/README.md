# Windows return-to-advertising crash investigation — 2026-10-23

**BUG-012 remains OPEN. The device crash is not proven fixed.**
Branch: `feature/portrait-kiosk-v2-next`; pre-change reference:
`b49ce247d108256a03594e4e9f6440791477fc48`. This is a source/CI reference,
not a known-good Windows hardware rollback for the reported crash.

## Owner result and acceptance

Owner reports **33/35 checked, five cycles**, Windows 11, scaling 100%, laptop
speaker. Tested HEAD and resolution are blank. Layout, pixel branding, moving
strips, response and audio are positively reported. Preserve these observations
and the raw checked count; do not invent failures for otherwise positive checks.

The note **“crash saat kembali ke halaman iklan”** overrides overall navigation
acceptance. In particular, checked F02 describes visit reset but cannot certify a
stable return to advertising. F05/F06 remain unchecked and untested for twenty
cycles. Five reported cycles cannot close them. Exact-HEAD acceptance is also
unverified. [Structured owner report](owner-retest.json).

## What the supplied log establishes

[Console log with workstation paths redacted](owner-console-redacted.txt):

- Python 3.12.10, Kivy 2.3.1, ffpyplayer 4.5.3, Intel Iris Xe.
- Two local advertising videos discovered. The same MP4 produces repeated
  `Image: Error loading` messages.
- Both GUI WAV assets select SDL2 successfully, duration 0.16 s / 40 s.
- No Python traceback, fatal native stack or process exit code is present.
  The final image-loader message alone does not establish why the process exits.

## Reproduced defect and bounded correction

Kivy 2.3.1's Video inherits Image. Its default `texture_update()` attempts to
open the movie source with the still-image loader when no explicit preview is
supplied. The regression **fails before correction**, observing the MP4 passed
to `set_texture_from_resource()` twice:
[red test transcript](image-probe-before.txt).

`GuardedVideo.texture_update()` now loads only an explicit preview; otherwise
it clears the still-image texture and lets the existing video decoder provide
frames. The advertising player's separate poster/fallback remains available
during loading. Valid explicit preview behavior and existing decoder retirement
are preserved. This removes a reproduced spurious loader error; it is **not
proof that the Windows crash had that cause**.

## Persistent diagnostics

The dedicated `python tools/run_portrait_v2.py` launcher installs a local
diagnostic session before importing native Kivy providers. Startup prints the
local source HEAD and a per-run file under `data/diagnostics/portrait-v2-*.log`.
The file remains open through application teardown and records:

- INFO-and-higher logs, page rebuild begin/ready and return-to-advert requests;
- uncaught Python application/worker exception tracebacks;
- fatal native Python stacks when `faulthandler` can capture the exception.

An existing explicit fatal handler (for example `python -X faulthandler`) stays
in control of its destination. An OS-forced termination may provide no Python
stack. Diagnostics cannot recover a native process crash. Logs stay local; no
automatic upload or messaging is added. Failure to create the log directory
does not prevent startup. The ordinary launcher remains the operator entry.

## Verified local evidence

- **79 focused tests PASS**, zero skips: [transcript](focused-tests.txt).
  Includes the red-to-green image-probe regression and seven diagnostics tests
  covering flushed Python tracebacks, native-file lifetime, existing handler
  ownership, worker delegation, bounded local Git lookup, configured launcher,
  and startup when diagnostics cannot be written.
- **314 complete tests run / 312 PASS / 2 optional palm-model skips**, zero
  failures or errors: [transcript](complete-tests.txt). Includes the existing
  shared-advertising native video regression.
- Twelve fresh audio-enabled page captures reviewed at
  [800×1280](screenshots/contact-800x1280.png) and
  [452×900](screenshots/contact-452x900.png). All twelve are pixel-identical to
  the preceding reviewed gallery captures: [comparison](visual-comparison.json).
  Original PNGs and hash manifests are preserved in `screenshots/`.
- Native video/audio **twenty-cycle probes before and after** both complete on
  Linux/offscreen/dummy audio. Mono 22.05 kHz and stereo 48 kHz synthetic MP4
  fixtures alternate across visits; every visit opens real decoded textures,
  retires the decoder, enters tutorial/gallery, changes a template/copy count
  and returns to ads. Cart/tutorial reset and decoder release are checked.
  [Before](native-cycles-before.json), [after](native-cycles-after.json).
- The corrected native [diagnostic transcript](native-cycle-diagnostic.txt)
  records twenty return requests and twenty-one ready advert pages, with no
  MP4 image-loader error. [Probe script](native-cycle-probe.py) preserves the
  local protocol; its `/tmp/v2-return-ad-probe` fixtures were generated by ffmpeg
  and contain synthetic pixels/tones, not the owner's local ad files.

These results **do not reproduce the owner's Windows crash**. They do not close
BUG-012, certify the actual advertisement files, Intel driver behavior, real
speaker output or the owner's twenty-cycle gate. Matching-source CI and capture
evidence are recorded below; no earlier commit's PASS is inherited.
Local captures record the base HEAD plus tracked changes;
[source hashes and test scope](local-source-manifest.json) identify the exact
runtime/renderer/test inputs. No runtime change was made after these checks.

The real dedicated launcher also completes native video/audio startup, displays
the advert page, stops on a scheduled test callback, closes its diagnostic stream
and leaves `Session end` on disk: [integration check](real-launcher-check.txt).
Seven diagnostic tests also pass in a fresh Python process without Kivy installed:
[standard-library-only transcript](stdlib-diagnostics-tests.txt).

## Exact-source checkpoint and CI

Code checkpoint: **`bef4014b762d11f3ea5622afaef35dfbb4fbda4e`**.
Normal push and remote HEAD match were verified. Later evidence-only commits do
not inherit this code checkpoint's CI result.

[CI run 39869369246](https://github.com/pratikto/PhotoBooth/actions/runs/39869369246)
is **SUCCESS, all three jobs**:

- Pure navigation/audio/preview/diagnostics: **56 PASS**,
  [transcript](pure-ci-tests.txt).
- Genuine Windows Python 3.12 native audio and diagnostics: **38 PASS**,
  [transcript](windows-ci-tests.txt). Native dummy output and diagnostic tests do
  not certify Windows GUI, the actual ad files or physical speaker acceptance.
- Desktop widget/audio smoke, native PCM and all four capture commands SUCCESS.

[Verified CI metadata](ci-verification.json). Original artifact `12465338177`
is 3,537,815 bytes; downloaded ZIP SHA-256 matches GitHub:
`7dfcadfcbc0c307382b81b04bfd3c19b6e93da437e4a66ae451a0125b2140002`.
All four manifests show the exact code SHA with `tracked_changes=false`.
All **24 page PNGs and nine motion frames** match their recorded hashes and
were visually reviewed:
[800×1280](ci-original/contact-800x1280.png),
[452×900](ci-original/contact-452x900.png),
[360×640](ci-original/contact-360x640.png),
[800×600](ci-original/contact-800x600.png),
[motion](ci-original/contact-motion.png).

This is a verified non-hardware source checkpoint. **BUG-012 remains OPEN**;
successful CI does not establish why the owner process exited or close its
five-to-twenty-cycle gap. Pre-change `b49ce24` is only a rollback reference,
not a certified stable Windows version for this crash.

## Windows next check

1. Update the existing `feature/portrait-kiosk-v2-next` branch with a normal
   fast-forward pull. Keep any local changes; do not force/reset them.
2. Run `python tools/run_portrait_v2.py`. Record the printed HEAD and diagnostic
   path; use the same local advertising videos that were present during failure.
3. Try one ad → tutorial → gallery → SELESAI / KEMBALI IKLAN cycle. If it exits,
   stop and share that run's diagnostic file plus the terminal's final lines.
   In PowerShell, also run `$LASTEXITCODE` immediately after Python exits and
   include the number; this helps identify native exits without a Python stack.
4. If return works, repeat and check video/image transitions and minimize/restore.
   Only after twenty completed cycles can F05/F06 be considered for a fresh PASS.

The [V4 checklist](../portrait-v2-gallery-focus/windows-checklist.html) remains
available. Clear previous checkmarks for a new tested HEAD; Submit Hasil prepares
a prompt for manual copy/send. Leave any failed or untried item unchecked.

No layout redesign, game/scanner/discount/payment activation, production service
change, new branch or master merge is included. Further changes to the native
decoder/driver/audio pipeline require evidence identifying the failure; current
device acceptance remains BLOCKED pending a diagnostic retest.
