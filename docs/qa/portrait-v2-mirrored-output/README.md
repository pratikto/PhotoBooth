# GUI v2 — mirrored photo output

Owner request, **26 October 2026 (Asia/Jakarta)**: printed photo output should
also be horizontally mirrored. Required branch `feature/portrait-kiosk-v2-next`.
Base/rollback checkpoint **568a2585379e17ff2671fb8ef1eb928170eae324**, remote
confirmed before editing. Existing shared catalog renderer is byte-identical to
refreshed v1 master **27f3801** and GUI **38fbaa5**; extend/reuse that renderer.

Mirror only photo pixels within their existing apertures, after EXIF/crop and
before the original clipping masks. Keep template/text/logo/QR, 640×1920 size,
203.2 dpi, copy batching and uncertainty/restart guards. Preserve full-resolution
raw JPEGs and detector inputs. New output only; never rewrite old saved strips,
requeue uploads or replay prints on restart. V1 callers retain their default
unmirrored composition.

Owner explicitly selected **"Strip hasil, cetakan, dan strip digital sama-sama
mirror"**. GUI v2 therefore composes one mirrored-photo PNG for onscreen result,
print transport and uploaded strip; review thumbnails mirror too. Raw JPEGs in
the download folder remain unmodified originals. No second print derivative or
driver mirror is applied, preventing an accidental double flip.

`compose_result(..., mirror_photos=True)` reuses the original renderer; v2 opts
in, while default v1/CLI callers remain normal. Mirroring precedes the original
mask, protecting asymmetric heart cutouts and decorative art within apertures.
The printer receives that same saved result path with the selected copy count.

## Planned validation and rollback

Use asymmetric photos to check all twelve real designs, unchanged template/QR
regions, original-file hashes and default v1 behavior. Exercise actual v2
composition/print path and retake, no-duplicate/restart guards. Run one final full
regression, review real native screenshots at 800×1280/452×900 and record the
tested source/hashes, counts, physical-paper limits and published checkpoints.

Rollback uses a scoped inverse commit on the same branch after review. Preserve
originals, saved outputs, manifests/counters, game/payment/print journals, queue
and original retention deadlines. Physical paper orientation requires a Windows
printer test; synthetic success is not paper acceptance.

## Windows retest

Use the [five-item Submit/import form](windows-checklist.html); it starts
unchecked with separate browser storage and adds no twenty-cycle requirement.

```powershell
git pull --ff-only origin feature/portrait-kiosk-v2-next
python tools/run_portrait_v2.py --print
Start-Process ".\docs\qa\portrait-v2-mirrored-output\windows-checklist.html"
```

Drive is optional for the paper-orientation test; add `--drive` only when its
existing setup is ready. Leave unavailable paper/phone checks blank. The older
eleven-item print/Drive form also has its obsolete unmirrored-photo wording
updated; its browser storage is versioned so old checks cannot automatically
pass the changed orientation. Prior stored answers/reports are not deleted.

## Local automated evidence

[Renderer/template checks](renderer-tests.txt): **19 PASS**, including the new
asymmetric all-twelve-design test. Photo pixels reverse left/right; QR pixels,
text/artwork and protected mask cutouts stay identical, raw-file hashes unchanged.
[Focused native/service checks](focused-tests.txt): **42 PASS / zero skips**,
21.260s, including approval → same saved print path/copy count, raw preservation,
retake, Drive and uncertainty/no-replay behavior.

[Final full regression](full-tests.txt): **808 PASS / zero failures/errors/skips**,
224.094s, Linux/Python 3.12.14/Kivy 2.3.1/software GL/dummy PCM and prepared offline
models. Includes the added restart assertion that a saved strip is not rewritten.
All [240 code/workflow/form hashes](tested-source-sha256.json) match the final
tested tree. Physical paper/audibility/cloud acceptance is NOT_RUN.

[Browser checks](browser-tests.txt) pass: five fresh unchecked items, metadata
import without passes, partial Submit 1/5 preserving unchecked paper, persistence/
download, 360/452/800px without horizontal overflow, and zero page errors. The
updated delivery form leaves old stored P03 answers intact but does not carry
them into the changed orientation. [Initial helper failure](browser-first-run.txt)
records a wrong P02 selector; correcting the test to actual P03 required no form
HTML/runtime/Python change and does not replace a failed app result with PASS.
