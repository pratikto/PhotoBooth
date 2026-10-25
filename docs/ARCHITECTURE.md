# Arsitektur Meong Photobooth — GUI v2

**25 Oktober 2026** · active development `feature/portrait-kiosk-v2-next` ·
source operator teruji `ea394e8` (780 full PASS/CI SUCCESS); baseline P5 `9433010`. Default repository masih master/v1;
GUI v2 adalah calon utama menurut owner. [Rencana](gui-v2-promotion-plan.md).

## Entry point dan lapisan

| Lapisan | Lokasi | Peran |
| --- | --- | --- |
| Launcher utama GUI v2 untuk development | `tools/run_portrait_v2.py` | Config window/input + diagnostics, tidak mengganti main.py |
| Launcher merchant Sandbox v2 | `tools/run_portrait_v2_sandbox.py` | Reuse merchant-trial helper, backend loopback/kunci terisolasi, GUI v2 khusus |
| Preflight read-only | `tools/check_portrait_v2.py` | Metadata source/dependensi/display ke JSON; tidak menguji perangkat/provider |
| Presentation/controller v2 | `photobooth/kiosk_v2/` | Page flow, native widgets, gallery, animation/audio ownership, worker adapters |
| Existing photo backend | `catalog.py`, `workflow.py`, `camera.py`, `transaction_store.py`, `manifest_io.py` | Master templates, sessions/copies/originals, manifest/counter atomik |
| Existing printer/Drive | `printer.py`, `printer_settings.py`, `drive_storage.py`, `drive_pool.py`, `drive_sync.py`, `retention.py` | Operator opt-in, physical/remote acceptance terpisah |
| Original Meong Fly | `photobooth/meong_fly*.py` + v2 scene/layout adapter | Stage/Flow/render/art/emitter existing, DEMO ledger milik v2 |
| Existing QRIS Sandbox protocol | `checkout_backend.py`, `checkout_store.py`, `qris_*`, `midtrans_*`, `booth_auth.py`, `payment_quote.py` | Server authority dan durable admission, bukan status PAID dari GUI |
| Legacy v1 | `main.py`, `photobooth/app.py`, `ui_kivy.py`, `audio.py` | Tetap ada untuk baseline/history; lifecycle GUI/audio tidak dicampur ke v2 |

Nama shared backend di tabel berada di `photobooth/`. Daftar modul v2 dan kontrak
lengkap: [desain teknis](portrait-kiosk-v2-technical-design.md). Peta semua branch
beserta SHA/file referensi: [audit](gui-v2-branch-audit.md).

## Operator increment — actual v1 reuse

`photobooth/ui_health.py` and device/hardware services are byte-identical to
dbbe055. `v1_health_controller.py` contains the verbatim original v1 worker method
in a standalone shell; the v1 app is not instantiated or changed.
`kiosk_v2/health_service.py` adapts existing cached-frame/heartbeat and lazy config;
`operator_health.py` mounts the same panel with v2 audio/modal/input lifecycle;
`health_report.py` uses existing inventory/atomic JSON helpers for safe metadata.
There is no new probe schedule, second camera, print payload, device selection,
public upload or order mutation. [Provenance and limits](qa/portrait-v2-operator-health/README.md).

## Durability dan batas trust

- Satu desain → tiga capture dan maksimum satu retake; count → lembar, bukan
  sesi tambahan. Preview mirror tidak mengubah source image/print/QR.
- PhotoJobs/GameJobs single-flight dan revision guards mencegah antrian tap,
  worker/UI blocking, atau aksi callback dari halaman lama.
- MOCK diskon lokal tidak menjadi promo tepercaya QRIS. Sandbox quote dari
  backend, settlement diverifikasi independen, grant sekali pakai dan ACK service
  wajib sebelum countdown. Pending/unknown/paid tidak terkena timeout browsing.
- Print tidak pasti tidak dikirim ulang otomatis. Restart capture Sandbox
  mengharuskan rekonsiliasi operator, tidak replay atau membuat charge baru.
- Drive QR bukan QRIS; retensi target 15 hari lokal/30 hari cloud belum berarti
  BUG-009 sudah terverifikasi. Delivery/privacy harus dinyatakan sesuai bukti.

Data default v2 terisolasi di `data/kiosk-v2-p3`, `data/kiosk-v2-p4`, dan
`data/kiosk-v2-sandbox/<merchant>/<booth>`. Jangan menghapus/mengganti data atau
journal v1/pembayaran untuk menyelesaikan uji atau rollback.

## Fitur terpisah yang belum menjadi arsitektur v2

Read-only Device Health panel/report kini direuse pada v2; device staging/switching, AI Background Studio, WhatsApp dan lab dithering terbaru tetap terpisah. Preflight v2 bukan pengganti operator
Health panel/hardware reconnect. Konfigurasi licensing/Free–Business–Enterprise,
central ads/per-machine sync, fleet control dan merchant POS masih desain/backlog.

Bukti source 688 full PASS/CI/screenshot ada di [P5](qa/portrait-v2-p5/README.md).
Tidak ada perubahan source aplikasi saat konsolidasi dokumentasi ini.
[Arsitektur sebelum konsolidasi](https://github.com/pratikto/PhotoBooth/blob/0dc6555d299cdab19d952e92df2ae660cdc4676d/docs/ARCHITECTURE.md)
mempertahankan riwayat v1 dan proposal lama.
