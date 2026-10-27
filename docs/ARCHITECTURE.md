# Meong Photobooth — GUI v2 architecture

## 27 October — failed-delivery retry isolation

Owner timing identifies repeated old bind failures as 70.782s of a 122.719s
queued-to-QR session; exact ValueError cause/installed SHA remain unknown.
Healthy-first scheduling, one recovery/30s, persisted 30–300s backoff and safe
bind codes are implemented; known folder/transaction conflicts remain protected.
67 focused service and 11 native delivery tests PASS; full/CI evidence follows.
Code.gs unchanged; no redeploy required. [Scope, evidence, updates and limits](qa/drive-delivery-performance/RETRY.md).

## 27 October — Drive delivery priority and timing

The owner prioritizes customer upload/GUI responsiveness. Source now uses one
file per transaction per pass, chunk-yielding content sync, incremental five-slot
reserve batches with startup/periodic reconciliation, and verified cross-version
asset reuse. Structured monotonic timing distinguishes queue/request stages.
Known-delay production root cause remains unmeasured; native/fixture evidence
and exact update/rollback steps are in the [delivery runbook](qa/drive-delivery-performance/README.md).
No deployed Google version, actual throughput or cloud deletion is certified.

**27 October FEAT-009 addition:** `kiosk_v2/recovery.py` reads existing local
state without service/device imports, and the ordinary launcher owns a kernel
lease for its full lifetime. The external watchdog requests the extra pre-GUI
recovery gate. Windows cmd / Ubuntu graphical-session unit are generated, never
installed; automatic restart stays off. Windows is the development host, Ubuntu
the deployment target. [Detailed scope, evidence and limits](qa/portrait-v2-recovery/README.md).

Updated **26 October 2026** after documentation baseline `f36ebad`; latest functional source
`fc26e3d` (mirrored v2 output/copy), current audit base `19e3f4d`. [Current status](FEATURE_STATUS.md) distinguishes source evidence,
owner reports and pending acceptance. Development: `feature/portrait-kiosk-v2-next`;
GitHub default `master`, default launcher `main.py` still v1.

## Entry points and layers

| Layer | Location | Responsibility |
| --- | --- | --- |
| Ordinary v2 launcher | `tools/run_portrait_v2.py` | Process-only window/input setup, diagnostics and v2 application |
| Merchant Sandbox launcher | `tools/run_portrait_v2_sandbox.py` | Reused isolated trial helper, loopback backend, booth-only GUI credentials, printer/Drive forced off |
| Read-only preflight | `tools/check_portrait_v2.py` | Source/dependency/display metadata JSON; no device/provider probes |
| V2 presentation/controllers | `photobooth/kiosk_v2/` | Flow/widgets/gallery/audio, revision guards and worker adapters |
| Shared photo services | `catalog.py`, `workflow.py`, `camera.py`, `transaction_store.py`, `manifest_io.py` | Original templates, session/copy rules, camera, atomic manifests/counters |
| Shared printer/Drive | `printer.py`, `printer_settings.py`, `drive_storage.py`, `drive_pool.py`, `drive_sync.py`, `retention.py` | Operator opt-in transports/storage; physical/cloud acceptance separate |
| Original Meong Fly | `photobooth/meong_fly*.py` + v2 scene/layout host | Original Stage/Flow/render/art/emitter; v2 owns its DEMO ledger |
| QRIS protocol | `checkout_backend.py`, `checkout_store.py`, `qris_*`, `midtrans_*`, `booth_auth.py`, `payment_quote.py` | Server authority, verification and durable admission |
| Operator health | `ui_health.py`, shared device/hardware services, `v1_health_controller.py` + v2 adapters | Original observation panel/backend/extracted worker, safe reports |
| Legacy v1 | `main.py`, `photobooth/app.py`, `ui_kivy.py`, `audio.py` | Separate launcher/application/audio lifecycle; not instantiated by v2 |

Shared filenames without a prefix are under `photobooth/`.
[Detailed module/contracts](portrait-kiosk-v2-technical-design.md) ·
[dated branch/provenance map](gui-v2-branch-audit.md).

## Trust and durability

One selected design creates three originals and permits one retake; quantity
means copies. V2 review and photo areas of result/printed/digital strip mirror;
full-resolution original JPEGs and detector input stay original, artwork/text/QR
stay normal, and v1 defaults/old saved outputs are unchanged. Single-flight photo/game/payment/report workers
and page/epoch guards prevent stale actions and duplicate work.

Sandbox uses backend quotes and independently verified settlement. A stable
one-use grant, durable STARTING before allocation and STARTED ACK before countdown
protect photo admission. Uncertain/pending/paid states survive browsing timeout
and restart; no automatic charge/capture/print replay. Local MOCK promotion is
not a trusted merchant discount. Paper output is not inferred from spool success.

The v2 Drive adapter requires retention acknowledgement before upload. This does
not prove deployed 30-day deletion (BUG-009). Photo download QR and payment QRIS
remain separate. [Retention scope](photo-retention.md).

Profiles are isolated under `data/kiosk-v2-p3`, `data/kiosk-v2-p4` and
`data/kiosk-v2-sandbox/<merchant>/<booth>`. Preserve journals/manifests on rollback.

## Booth storage and shared content

The ordinary launcher uses 25 empty per-booth reserves, durable claims,
Photo/NN/raw,color,bw local session files and offline content caches. The owner
corrected the **cloud** tree to Photobooth/PB001/Photo/00000001/{raw,bw,color}.
BoothDriveClient maps existing local session paths into these three flat remote
directories, prefixing filenames with session IDs. Code.gs scopes reserve,
binding, uploads and retention to the numbered Photo folders. Local state is
preserved; physical copies reuse the saved exact BW raster.

Reserve/bind acknowledgements require verified anyone-reader sharing plus a
numbered-layout marker before Python trusts their links. Binding errors persist
safe GUI categories instead of silently waiting. An authenticated empty legacy
reserve can be moved without changing its folder ID; unrelated/nonempty content
requires review. The installed Apps Script deployment still needs updating.
See [contract](photobooth-storage-layout.md) and
[repair setup/evidence](qa/drive-photo-layout/README.md). All old contents remain excluded.

## Operator reuse and separate candidates

Ordinary v2 --print/--drive opt-ins reuse the existing saved v1 configuration,
thermal/Drive clients and durable PhotoJobs/PhotoTest. Approved strips auto-print
once/design; the existing isolated upload queue starts/resumes without a new
photo visit. Status snapshots gate consent on verified folders and update a
large result QR only after file verification. Native helpers are adapters, not
parallel printer/cloud backends. The dedicated merchant trial keeps delivery off.
[Contracts and proof](qa/portrait-v2-print-drive/README.md).

`ui_health.py` and imported health services match `dbbe055`; the original worker
method is extracted verbatim into `v1_health_controller.py`. V2 adapts cached
frames, Kivy scheduling, lazy printer config and UI/audio lifetime. Manual open/
refresh only; no second camera, print payload, device switching, watchdog,
automatic upload or order mutation. [Provenance](qa/portrait-v2-operator-health/README.md).

BUG-018 adds per-control fresh-press/consumed-release admission in the v2 adapter.
Rapid repeats within 0.75 seconds are dropped, without deferred commands/SFX;
close remains independent of report/probe busy state. Original v1 services/UI
and worker remain unchanged. [Correction evidence](qa/portrait-v2-health-clicks/README.md).

Device staging/switching, AI Background Studio, WhatsApp, newer dithering lab,
central ads/licensing/fleet/POS remain separate candidate scopes. Readiness CLI,
health observations and physical acceptance answer different questions.

## Historical record

The [pre-audit version](https://github.com/pratikto/PhotoBooth/blob/5f09eff9998c942ed54feef0cf0563fc3944611b/docs/ARCHITECTURE.md) preserves the complete dated history. Its former “current”, approval, branch and next-step statements apply only to their recorded stage. Use the current documents linked above for continuation.

