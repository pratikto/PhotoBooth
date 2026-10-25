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
