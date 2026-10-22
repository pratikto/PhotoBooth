# Windows retest at 9a9e18e — 2026-10-22

Branch: `feature/portrait-kiosk-v2-next`. Pre-correction rollback checkpoint:
`9a9e18e91fe789cc305826352d282d5be5f2aadf`.

## Owner evidence and open failures

Owner supplied screenshots of the offline checklist: **27/32 checked** on
Windows 11, laptop speaker, tested HEAD `9a9e18e`. A01–A06, B06, C01–C04,
D01–D08 and E01–E06 are visibly checked. F01–F02 were not visible in supplied
screenshots; do not infer them from the total. B01–B05 are **not tested** because
the gallery preview was not visible at the owner's window size. These are not
five independently confirmed swipe failures.

Owner qualifies C/D results: a single flow works, but music **and** clicks become
silent after repeated complete visits. Repeated-use audio acceptance remains
**FAIL / OPEN**, despite the individual single-flow checkmarks. Actual display
resolution/scaling and the number of cycles before failure were not supplied.

## Audio correction

Reproduced the underlying mute condition with the real Kivy 2.3.1 SDL mixer:
channel 0 reused after retirement, `state=play`, WAV gain 0.6, **channel gain 0**.
WAV chunk gain and mixer channel gain are separate. ffpyplayer's Windows mixer
backend changes channel gain; retiring muted video leaves an idle channel that
Kivy SoundSDL2 can reuse without restoring its gain. This is a demonstrated
native failure mechanism, not a claim of reproducing the owner's entire Windows
session on Linux.

The v2 SDL2 wrapper restores gain **only on unused channels before WAV
allocation**, including automatic music loops. Playing video/GUI channels retain
their existing gains. It resolves the mixer already loaded by Kivy, opens no new
audio device, does not change the shared advertising player or v1 audio, and
preserves explicit KIVY_AUDIO overrides. If the native wrapper cannot load,
provider selection logs the failure and uses the existing Kivy fallback.

**54 focused tests PASS** (audio/flow/design/widgets plus native test). The native
regression reproduces the old muted state, then runs **20 cycles** through video
channel reuse, tutorial, gallery, silent game preview, image ad, suspend/resume,
and close. It samples actual **post-mix PCM** through SDL's dummy device, checks
nonzero music/click samples, verifies that a concurrent click does not unmute a
playing ad, and checks silence after close. [Transcript](audio-tests.txt).
Full regression: **289 run, 287 PASS, 2 optional native palm-model skips,
zero failures/errors**. [Transcript](audio-full-tests.txt). Compile and diff checks pass.
No physical speaker or actual Windows decoder was tested here.

## Windows acceptance still required

- [ ] Repeat at least 20 complete visits, including image and video advertising;
      music and clicks must remain audible on every visit.
- [ ] Image ads have GUI music; video ads use source audio only; game preview has
      clicks but no GUI soundtrack.
- [ ] Minimize/restore and close/relaunch repeatedly; no duplicate/orphan audio.
- [ ] After layout correction: resize the live window, check all three previews,
      swipe left/right once per gesture, reject vertical/short gestures.
- [ ] Payment, scanner, real discounts and production transactions stay inactive.

Future checklist preference: add **Submit Hasil** to prepare a report that can
be pasted into chat. Offline HTML cannot silently submit to this conversation.
