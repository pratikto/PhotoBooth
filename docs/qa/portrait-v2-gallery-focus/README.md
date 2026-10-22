# Owner retest and gallery polish — 2026-10-22

Branch: `feature/portrait-kiosk-v2-next`. Starting code/document checkpoint:
`29a34198a4893df6fc399ac64767a04b7401935e`.

## Owner result and limits

Owner reports **41/41 boxes checked**, Windows 11 / laptop speaker / **10 completed
cycles**. Crash gates P01–P03, touch swipes, clicks, image/video music ownership,
minimize/close and reset are positively reported. Follow-up confirms arbitrary
window resizing works; the requested change concerns gallery proportions.

**Do not close the 20-cycle gate:** G03/G06 explicitly require twenty cycles,
while supplied metadata records ten. Tested HEAD, resolution and display scaling
are blank; the follow-up did not supply them. Preserve the raw checked count,
but do not call this final exact-SHA or twenty-cycle acceptance. [Audit](owner-retest.json).

Three open requests: slight lag after taps, actual strip motion during sliding,
and a gallery layout that gives most space to the strip images.

## Response correction

Local Linux/offscreen profile at the starting source measured first gallery
entry **167.398 ms**; uncached template changes **36–62 ms**, dominated by Pillow
artwork decode/resizing. These are callback timings, not Windows input-to-display
or speaker latency and not a guarantee about video decoder shutdown.

- Prepare silent button/music handles during idle. Valid button feedback starts
  before routing; short button feedback survives page handoff, while camera-only
  effects still stop on silent pages and all sounds stop on suspend/close.
- One worker prepares detached RGB previews of the twelve approved masters,
  prioritizing the first gallery's three strips. Only the main thread creates
  GPU textures. Reading the warmup cache never waits; early uncached access keeps
  the existing synchronous fallback. Queued warmup is cancelled on close.
- Copy changes update only the quote/count; they no longer touch image rendering.

**68 focused tests PASS**, including silent/idempotent audio preparation,
feedback-before-callback, no copy-triggered image work, worker priority/failure,
nonblocking cache access, queued-work cancellation and native twenty-cycle PCM.
[Transcript](response-tests.txt).

[Before timings](latency-before.json), [immediate after timings](latency-after-immediate.json)
and [after two seconds idle](latency-after-idle.json). The latter explicitly
waits for background preparation and records ready-preview count; first use
before warmup completes can still decode synchronously. No synthetic timing is
presented as a measurement on the owner's Windows machine.

## Checkpoint / next stage

Pre-change rollback reference: `29a3419`. This documentation records the incoming
owner result separately from the subsequent source. Gallery layout/slide polish
is the next change in the same authorized scope. No game/payment/scanner/backend
integration or master change is made. Windows acceptance for these new changes
requires a fresh retest and actual HEAD.
