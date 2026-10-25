# GUI v2 automatic print and background Drive delivery

Owner continuation, **25 October 2026**: prioritize **printing and Google Drive
only**, postponing proposed watchdog work. The owner selected automatic printing
after approving three photos, as v1, with Drive uploading in the background.
Required branch `feature/portrait-kiosk-v2-next`; baseline/rollback **edeec47**.

## Reuse and boundaries

Remote references were refreshed read-only: master 27f3801, v1 GUI 38fbaa5,
thermal a38d4a6, newer lab e89e6ee. [Provenance](reused-source.json) verifies nine
actual printer/settings/Drive/pool/sync/retention/transaction/workflow/QR files
already match v1 master byte-for-byte. Reuse them, existing PhotoJobs and the
durable v2 print reservation/retention guard; do not instantiate v1 GUI or port
the newer lab. Existing v1 print controller automatically starts one batch after
composition; the v2 host will follow that choreography through its current worker.

Stage 1 adds explicit launcher opt-ins and worker-only setup/verified download
QR metadata. Stage 2 wires automatic print, background queue startup, readable
readiness/progress, large verified on-screen QR and native regression/screens.
One final full regression follows the final functional change, with relevant
checks/commit/push/remote verification at each stage.

No payment/provider/scanner/discount, watchdog, merge/default change, actual
cloud upload/deletion/deployment or physical printer action occurs in cloud QA.
Use synthetic photo/provider/printer fixtures. Dedicated merchant trial keeps
printer/Drive off. Cloud environment has no saved printer config/Drive credentials;
actual paper, phone download, configuration and cloud retention require the laptop.
BUG-009 remains OPEN; do not remove the retention acknowledgement upload guard.

Existing failed/uncertain print jobs must never replay after restart. Preserve
originals, retakes, assigned folder IDs/QR, file-revision checks, offline queue,
local retention and all journals. A spool submission is not physical paper;
UPLOAD_COMPLETE is verified files, not proof of phone permissions or deletion.

## Stage 1 validation

**29 PASS / zero failures/errors/skips**, 5.343s: options, original photo/print/
Drive worker, setup/QR, launcher diagnostics and saved printer settings.
[Raw output](stage1-tests.txt). No physical/provider readiness is inferred.


## Native delivery integration

The owner selected automatic printing. Existing v1 controller choreography is
approval → composition → one background print batch, with Drive kicked separately.
Its root.after/legacy PhotoBoothUI controller cannot own the active native v2
window. Reuse the already-present PhotoJobs/PhotoTest durable print routine,
existing v2 result page and original v1 QR encoder instead of opening a second
GUI or recreating printer/cloud transports.

`python tools/run_portrait_v2.py --print --drive` opts into both. It reads the
same `data/printer_settings.json`, ignored `photobooth/local_settings.py` or
existing Drive OAuth environment as v1; do not paste credentials into chat/Git.
`--print` follows the owner's auto-print choice; `--manual-print` is an explicit
operator fallback. Default launch without opt-ins remains local/no printing.
Dedicated merchant Sandbox rejects these opt-ins and still forces both off.

After PAKAI FOTO INI, the existing worker persists SENDING, sends exactly N
identical copies in one batch, then records SUBMITTED/UNCERTAIN. It never equates
spooling to paper. Repeated input/resize/minimize/Drive status updates cannot
reprint; uncertain sends require the existing operator acknowledgement. Restart
converts interrupted sends to UNCERTAIN and does not replay them.

With --drive, the existing queue resumes at startup without a new photo visit;
preparation/client/pool work is off the GUI. No late preparation result rebuilds
advertising. Consent shows actual verified folder readiness and remains disabled
until a cached/online verified folder is available. Cached slots preserve the v1
offline contract; no slot means wait, not a fake URL or silent local fallback.
Result status distinguishes pending/retry/verified/retention hold. Upload keeps
running after returning to advertising, using original file identities/revisions.

A large on-screen QR appears only after the original queue reports all files
verified. The existing v1 encoder runs/caches on PhotoJobs; UI polls update the
existing QR/label without reconstructing the page or sending another print.
Raw originals/retake/final strip, assigned URL and separate V2 namespace remain.
No cloud cleanup/deployment or BUG-009 closure is inferred from retention ACK.

Early GUI checks: **92 PASS / zero failures/errors/skips**, 70.894s, including
native photo/game-adjacent input, operator, MOCK and Sandbox regressions
([raw](native-regression-tests.txt)). An additional background-resume case then
joined the delivery service module, **5 PASS**, 0.554s ([raw](resume-service-tests.txt)).
The actual inherited sync loop delivered an old fixture queue without a new visit,
new counter or print. Final full regression follows all functional changes.

Fourteen new native fixture PNGs (seven states × two required sizes) were hash/
dimension checked and visually reviewed ([contact sheet](local-contact.jpg),
[verification](local-screenshot-verification.json)). The large QR decodes from
both full-window 800×1280 and 452×900 images to the exact fixture folder URL;
this is pixel evidence, not a phone/network permission test. Renderer uses the
original P3 recorder/camera plus injected printer/Drive transports and actual
pool/sync/retention passes, never real credentials or requests.


## Stage 2 focused checks and Windows form

Final new-feature checks: **15 PASS / zero failures/errors/skips**, 6.108s
([output](stage2-tests.txt)), covering explicit options, existing-client/config
reuse, verified worker QR/cache, actual background queue resumption, one auto
batch/design, slow/uncertain sends, multiple designs and late UI delivery.
[Eleven-item Windows form with Submit](windows-checklist.html) was checked in
Chromium: all boxes initially empty, metadata import never passes tests, partial
Submit 1/11, persistence/download, no horizontal overflow at 360/452/800px, zero
browser errors ([output](browser-tests.txt), [hash/results](form-verification.json)).
No old twenty-cycle repetition is imposed; paper/phone/offline/restart cases
must be actually tested, otherwise left blank.

To run on Windows in the existing virtual environment, from the repository:

```powershell
git pull --ff-only origin feature/portrait-kiosk-v2-next
python tools/run_portrait_v2.py --print --drive
```

Open the local checklist (cloud file links are not Windows paths):

```powershell
Start-Process ".\docs\qa\portrait-v2-print-drive\windows-checklist.html"
```

If v1 printer/Drive settings already work, reuse them without copying private
values to Git/chat. If not, use the existing [printer guide](../../printer-setup.md)
and ignored local_settings.example.py template, or the existing OAuth variables
PHOTOBOOTH_DRIVE_PARENT_ID/GOOGLE_OAUTH_CLIENT_ID/GOOGLE_OAUTH_CLIENT_SECRET/
GOOGLE_OAUTH_REFRESH_TOKEN. Reopen the GUI after changing private configuration.
Missing configuration gives an explicit safe hint; it does not create a fake QR.
For paper-only testing use `--print`, leave Drive items NOT_RUN. For deliberate
manual printing use `--print --manual-print`.

If no verified folder is ready, consent waits while the existing pool retries;
with cached verified slots, offline capture/print can proceed. If UPLOAD DITAHAN
appears, investigate the existing backend retention setup/ACK through the
[retention runbook](../../photo-retention.md). Do not bypass the guard. Any
remote setup/deployment/deletion is separate from this cloud source work; a
registered deadline alone still does not close BUG-009 or prove actual deletion.

Synthetic renderers and the unittest runner now explicitly clear ambient live
printer/Drive opt-ins. The final fifteen checks also pass when the parent shell
has both flags enabled; isolated fixtures opt in only within their own contexts.
