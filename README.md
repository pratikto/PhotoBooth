# Meong Photobooth — GUI v2

GUI portrait untuk photobooth Meong: iklan, tutorial, 12 template strip asli,
foto tiga pose, satu retake per desain, hasil lokal, serta Meong Fly DEMO.
Dibangun dengan Kivy, OpenCV dan Pillow; backend foto/printer/Drive yang sudah
bekerja dipakai kembali melalui adapter.

**Pusat pengembangan: `feature/portrait-kiosk-v2-next`.** Owner menetapkan GUI v2
sebagai calon branch utama berikutnya pada **25 Oktober 2026**. GitHub default
branch **masih `master`**; tidak ada rename, merge atau penggantian default pada
pembaruan dokumentasi ini. `python main.py` tetap menjalankan GUI v1.

## Jalankan GUI v2 di Windows

Dari repository dan environment Kivy yang sudah digunakan:

```powershell
git switch feature/portrait-kiosk-v2-next
git pull --ff-only origin feature/portrait-kiosk-v2-next
.\.venv-kivy\Scripts\Activate.ps1
python tools/run_portrait_v2.py
```

Instalasi pertama memerlukan Python 3.11+ (QA memakai Python 3.12), environment
Python, dan `python -m pip install -r requirements.txt`. Jangan membuat ulang
proyek atau menimpa konfigurasi/perubahan lokal untuk mengikuti panduan ini.

Alur lokal: **iklan → MULAI FOTO → tutorial → pilih template/jumlah → UJI FOTO →
persetujuan → tiga foto → review/retake → hasil → iklan**. Jumlah 0–9 berarti
lembar identik; satu desain tetap satu sesi tiga foto. Printer dan Drive hanya
aktif dengan opt-in operator; default menyimpan hasil lokal.

## Pilih mode pengujian

| Mode | Cara menjalankan | Batas |
| --- | --- | --- |
| GUI lokal/default | `python tools/run_portrait_v2.py` | Pembayaran produksi/scanner nonaktif; foto melalui persetujuan UJI FOTO |
| Checkout MOCK lokal | Set `$env:PHOTOBOOTH_V2_CHECKOUT_MOCK='1'`, lalu launcher biasa | QR nonpayable; simulasi konfirmasi dan diskon game, bukan settlement bank |
| QRIS Sandbox | `python tools/run_portrait_v2_sandbox.py` setelah instalasi extras | Merchant uji + simulator resmi; belum diterima di perangkat/provider; tanpa promo game QRIS |

Tutup aplikasi dan hapus flag MOCK (`Remove-Item Env:PHOTOBOOTH_V2_CHECKOUT_MOCK
-ErrorAction SilentlyContinue`) setelah pengujian mode tersebut. Launcher Sandbox
memisahkan mode dan kredensial serta menonaktifkan printer/Drive untuk trial.

Untuk Sandbox, instal `python -m pip install -r requirements-qris.txt`.
Login [Dashboard Midtrans](https://dashboard.midtrans.com/), pilih **Sandbox →
Settings → Access Keys**. Merchant ID dan Server Key Sandbox (awalan
`SB-Mid-server-`) dimasukkan secara lokal saat diminta. Sandbox dibuat saat
pendaftaran; menunggu persetujuan produksi tidak sama dengan menunggu akses
simulasi. [Penjelasan resmi](https://docs.midtrans.com/docs/midtrans-account).
Jangan kirim Server Key ke chat/repository. Gunakan simulator resmi yang dicetak
terminal, bukan aplikasi bank/dompet asli. [Panduan dan recovery](docs/qa/portrait-v2-sandbox/README.md).

## Device Health operator — reuse v1

Pada halaman iklan tekan **F12** atau tahan header Meong **1,5 detik**. Panel
Device Health existing menampilkan enam indikator, inventory OS dan REFRESH di
background. Akses juga tersedia pada Sandbox RECOVERY, tanpa mengubah order.
Capture/game/checkout aktif tidak dapat diinterupsi lewat akses operator ini.

**SIMPAN LAPORAN LOKAL** membuat JSON metadata di `data/diagnostics`, tanpa foto,
key/token, raw logs, alamat jaringan atau queue/serial. READY hanya observasi
terbatas, bukan bukti paper/provider/Drive siap. PILIH DEVICE nonaktif; tidak
mengubah konfigurasi atau membuka kamera kedua. [Panduan/bukti](docs/qa/portrait-v2-operator-health/README.md)
· [8-item form operator dengan Submit](docs/qa/portrait-v2-operator-health/windows-checklist.html).

## Uji akhir dan status saat ini

```powershell
python tools/check_portrait_v2.py
Start-Process docs/qa/portrait-v2-p5/windows-checklist.html
```

Impor `data/diagnostics/windows-readiness.json` ke form, periksa perangkat aktual,
centang hanya tes yang lulus, lalu **Submit Hasil** untuk menyiapkan laporan chat.
Owner telah melaporkan **READY_FOR_MANUAL_TEST pada HEAD `0dc6555`**; ini baru
preflight, bukan bukti lulus pengujian perangkat/provider.

Baseline P5 sebelum increment operator, source **9433010**: **688 tes PASS / 0 skip**;
[CI 40109206417](https://github.com/pratikto/PhotoBooth/actions/runs/40109206417)
tiga job SUCCESS dan 109 PNG terverifikasi. Screenshot 800×1280 dan 452×900
sudah direview. Native CI memiliki satu skip aset palm opsional yang tercakup
dalam local full run. Ini bukti source/fixture, bukan sertifikasi produksi.
[Seluruh bukti, batas dan checkpoint P5](docs/qa/portrait-v2-p5/README.md).

**Masih menunggu bukti:** uji merchant Sandbox dan integrasi Windows baru,
printer fisik, Drive/download/retensi 30 hari (BUG-009), privasi, serta persetujuan
rilis. Promo game bekerja pada simulasi lokal/MOCK; backend QRIS belum punya
kontrak promo tepercaya, sehingga Sandbox meminta persetujuan harga penuh.
Produksi, POS/scanner nyata, deployment dan merge tetap tidak aktif/tidak dilakukan.

## Dokumentasi pengembangan

- [Indeks dokumentasi](docs/README.md) — pilih panduan menurut tugas.
- [Roadmap dan perilaku GUI v2](docs/portrait-kiosk-v2.md).
- [Arsitektur dan kontrak adapter](docs/portrait-kiosk-v2-technical-design.md).
- [Status fitur](docs/FEATURE_STATUS.md), [bug](docs/bug_tracker.md), [handover](docs/DEVELOPMENT_HANDOVER.md).
- [Audit 19 branch beserta SHA/referensi](docs/gui-v2-branch-audit.md).
- [Rencana GUI v2 menjadi branch utama](docs/gui-v2-promotion-plan.md).
- [Aturan reuse, scope dan pengujian](AGENTS.md), [prompt melanjutkan](docs/DEVELOPMENT_PROMPT.md).

Pakai implementasi existing sebelum menulis pengganti. Game menggunakan renderer
asli dari `feature/meong-flappy-challenge`; QRIS menggunakan service/client/journal
dari `feature/qris-payment`. AI Background, Device Health, WhatsApp dan update
lab dithering di branch lain bukan otomatis fitur GUI v2.

Riwayat v1 tetap tersedia di [rilis v1.0.0](docs/releases/v1.0.0.md), QA bertanggal,
dan [README sebelum konsolidasi](https://github.com/pratikto/PhotoBooth/blob/0dc6555d299cdab19d952e92df2ae660cdc4676d/README.md).
Tag v1 dan data/journal operasional tidak diubah oleh pembaruan dokumentasi.
