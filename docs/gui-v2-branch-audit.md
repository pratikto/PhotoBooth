# Audit dokumentasi lintas branch — GUI v2

Tanggal: **25 Oktober 2026 (Asia/Jakarta)**. Repository `pratikto/PhotoBooth`.
Snapshot remote: **19 branch**, diperiksa dengan `git ls-remote --heads origin`;
objek dibaca melalui `git show <SHA>:<path>`, tanpa switch/merge atau push ke
branch referensi. Metadata GitHub menunjukkan default branch masih **master**.

Owner meminta dokumentasi GUI v2 diperbarui dengan referensi tiap branch dan
menyatakan GUI v2 kelak menjadi branch utama. Saat ini pusat pengembangan GUI v2
adalah **feature/portrait-kiosk-v2-next**. Pernyataan arah tersebut belum mengubah
GitHub default branch, launcher default, proteksi, PR base atau rilis.

## Cakupan audit

Setiap branch diinventarisasi README/dokumennya. README, indeks/status/keputusan/
handover yang tersedia serta panduan fitur terkait ditinjau untuk membedakan
aturan yang masih berlaku, implementasi yang benar-benar direuse, dan eksperimen
terpisah. [Manifest branch, daftar dokumen, SHA dan hash sumber](reference/branch-doc-audit-2026-10-25.json)
memungkinkan pemeriksaan ulang. Ini **audit dokumentasi/source**, bukan eksekusi
ulang pengujian di 19 branch. Bukti tes lama tetap terikat source aslinya.

## Peta semua branch

| Branch / snapshot | Dokumen utama yang dirujuk | Temuan | Implikasi untuk GUI v2 |
| --- | --- | --- | --- |
| `backup/feature-kivy-gui-pre-printer-separation-20261017` · `1c717b9` | [README.md](https://github.com/pratikto/PhotoBooth/blob/1c717b940802c0f3f4d20ef26d7ea55960cb66e7/README.md) | Arsip sebelum pemisahan printer; GUI/audio dan transport saat itu. | HISTORIS; jangan pulihkan seluruh snapshot atau aturan harga lama. |
| `backup/feature-thermal-printer-pre-rebase-20261017` · `105e9b3` | [README.md](https://github.com/pratikto/PhotoBooth/blob/105e9b3c323973c61b0134b042fd6b55d2a1ea03/README.md) | Arsip transport printer sebelum rebase; prioritas LAN/Wi-Fi/USB. | HISTORIS; tidak mengungguli perilaku batch/uncertain terbaru. |
| `backup/master-pre-v1-20261019` · `d4852cb` | [README.md](https://github.com/pratikto/PhotoBooth/blob/d4852cb56d2eea92ae135a5ab38ce3676e2f3381/README.md) | Prototype Tkinter/satu foto sebelum rilis v1. | ROLLBACK HISTORIS; bukan dasar memulai ulang GUI v2. |
| `docs/feat-021-whatsapp-photo-delivery` · `aebde84` | [docs/DECISIONS.md](https://github.com/pratikto/PhotoBooth/blob/aebde8438833d27aeed25f3873229aca64d11636/docs/DECISIONS.md) | WhatsApp direncanakan sebagai kanal tambahan; QR Google Drive tetap ada. | DESAIN SAJA; tidak ditemukan integrasi WhatsApp di v2. |
| `docs/meong-fly-tutorial-gate-20261021` · `980af99` | [docs/DECISIONS.md](https://github.com/pratikto/PhotoBooth/blob/980af99798b67084aff517f36d76e2c1af767c02/docs/DECISIONS.md) | Tutorial wajib sekali per kunjungan setelah direct entry atau hasil game. | ATURAN SUDAH DITERAPKAN di VisitFlow v2; catatan design-only branch lama bersifat historis. |
| `docs/post-v1-release-reconciliation-20261019` · `359e8e5` | [docs/README.md](https://github.com/pratikto/PhotoBooth/blob/359e8e56cee8c049ff927433cab562804d082f41/docs/README.md) | Pisahkan status source, laporan operator, bukti CI dan baseline v1. | ATURAN DOKUMENTASI DIPAKAI; jumlah tes/deferral lama bukan status v2 sekarang. |
| `feature/ai-background-studio` · `eb368c1` | [docs/DEVELOPMENT_HANDOVER.md](https://github.com/pratikto/PhotoBooth/blob/eb368c11b52ee4e88d5644b07a79b7bdd9178f2d/docs/DEVELOPMENT_HANDOVER.md) | Backend offline + kontrol Original/Clean Studio pada GUI v1, cache model dan fallback; CI backend terpisah dari GUI/perangkat. | KANDIDAT; belum diintegrasikan ke GUI v2. Model, latency dan Windows/paper QA masih gate. |
| `feature/device-health` · `dbbe055` | [docs/device-health.md](https://github.com/pratikto/PhotoBooth/blob/dbbe055bb1281ad065a5ba0c3593cfbfbd388bd3/docs/device-health.md) | Panel operator read-only, staged selection untuk restart, Windows discovery completeness; CANDIDATE/RETURNED tidak membuktikan perangkat siap. | KANDIDAT; tidak ada Health Settings panel di v2. Jangan otomatis reconnect/hot-swap/merge; riwayat revert tetap dihormati. |
| `feature/dither-tuning` · `e89e6ee` | [docs/dither-gui-parameter-guide.md](https://github.com/pratikto/PhotoBooth/blob/e89e6ee1c758abc169ee250ee9285022f41cfc3b/docs/dither-gui-parameter-guide.md) | Panduan parameter 24 Oktober; Floyd/Bayer/Dizzy lab, Auto Tune dan enhancement opsional, threshold label hanya pada mode terkait. | LAB LEBIH BARU; versi lab ini tidak otomatis ada di v2. Backend printer yang sudah dipakai v2 dipertahankan. |
| `feature/kivy-gui` · `38fbaa5` | [README.md](https://github.com/pratikto/PhotoBooth/blob/38fbaa5c8f3d599848d33c82c2b2af5cf3aa6f8f/README.md) | Riwayat v1: template asli, satu sesi/desain dan N copy, printer RAW batch, mirror preview dan rilis source. | BACKEND TERPILIH SUDAH DIPAKAI; main.py/UI/audio v1 bukan launcher/owner audio v2. |
| `feature/local-photo-session-mvp` · `a3c1618` | [README.md](https://github.com/pratikto/PhotoBooth/blob/a3c161856eab22c5d98790aa1ab03c015fa2e8c2/README.md) | Prototype Tkinter, transaksi/folder/counter/upload queue. Quantity dahulu berarti sesi terpisah. | HISTORIS; quantity v2 berarti lembar, bukan sesi tambahan. |
| `feature/meong-flappy-challenge` · `672e3f7` | [docs/features/FEAT-021-meong-fly.md](https://github.com/pratikto/PhotoBooth/blob/672e3f7089bb40940e5b41644ceb656aa63aafbb/docs/features/FEAT-021-meong-fly.md) | Renderer/flow/sprite/emitter asli, game satu kesempatan; branch ini juga punya local DEMO scanner camera dan bukti terkait. | RENDERER SUDAH DIREUSE langsung (26 file); scanner/POS asli tetap tidak aktif pada v2. Bukti branch bukan bukti semua integrasi v2. |
| `feature/portrait-kiosk-gui` · `92101d9` | [docs/portrait-kiosk-v2.md](https://github.com/pratikto/PhotoBooth/blob/92101d9f778e0c8f282a616bb815b52dda1d37b2/docs/portrait-kiosk-v2.md) | Prototype awal P0–P2 portrait dan isolasi GUI/audio dari v1. | LELUHUR PENGEMBANGAN; status placeholder/tiada kamera pada snapshot ini sudah usang untuk v2-next. |
| `feature/portrait-kiosk-v2-next` · `0dc6555` | [docs/qa/portrait-v2-p5/README.md](https://github.com/pratikto/PhotoBooth/blob/0dc6555d299cdab19d952e92df2ae660cdc4676d/docs/qa/portrait-v2-p5/README.md) | GUI aktif P2/P3/P4 DEMO+MOCK+Sandbox, persiapan P5; source 9433010 dan bukti 0dc6555. | UTAMA UNTUK PENGEMBANGAN GUI v2; calon branch utama repository setelah gate dan instruksi pemindahan. |
| `feature/qris-payment` · `3cc8a8e` | [docs/QRIS_SANDBOX_TRIAL.md](https://github.com/pratikto/PhotoBooth/blob/3cc8a8e360e8c2100a3077b755664eb61d0216ea/docs/QRIS_SANDBOX_TRIAL.md) | Backend quote, autentikasi booth, rekonsiliasi provider, journal/grant, launcher merchant Sandbox terisolasi. | BACKEND/CLIENT/JOURNAL DIREUSE; adapter GUI v2 sendiri. Tidak ada kontrak promo Meong Fly tepercaya atau aktivasi produksi. |
| `feature/thermal-printer` · `a38d4a6` | [README.md](https://github.com/pratikto/PhotoBooth/blob/a38d4a67e0f4938ac33d8c165c2dd52f0baf8ca7/README.md) | Backend printer dan GUI operator awal; sebagian dokumentasi memakai tarif/quantity lama. | BACKEND TERKAIT SUDAH ADA; jangan mengganti printer terbaru dengan snapshot UI/aturan lama. |
| `fix/kivy-music-playback` · `27f3801` | [docs/DEVELOPMENT_HANDOVER.md](https://github.com/pratikto/PhotoBooth/blob/27f3801b235d81dc0a49ab201f3e143b62314413/docs/DEVELOPMENT_HANDOVER.md) | Tip sama dengan master pada audit; riwayat musik v1 dan revert FEAT-008. | HISTORIS/V1; audio owner v2 terpisah, jangan menghidupkan dua lifecycle. |
| `master` · `27f3801` | [docs/README.md](https://github.com/pratikto/PhotoBooth/blob/27f3801b235d81dc0a49ab201f3e143b62314413/docs/README.md) | Default GitHub saat audit; baseline v1 setelah perbaikan/revert. Tag v1.0.0 tetap immutable. | DEFAULT SAAT INI, bukan target commit dokumentasi ini. Belum diganti atau di-merge. |
| `revert/feat-008-stage-a-20261019` · `57ff555` | [docs/DEVELOPMENT_HANDOVER.md](https://github.com/pratikto/PhotoBooth/blob/57ff555e15fbe6a0150900fe3d6c5177a11e46d6/docs/DEVELOPMENT_HANDOVER.md) | Mencatat pencabutan merge FEAT-008 yang tidak diotorisasi. | JEJAK GOVERNANCE; referensi branch bukan izin merge atau aktivasi ulang. |

## Konflik yang diselesaikan di dokumentasi GUI v2

- README v1 menyebut game, kamera dan QRIS seluruhnya belum ada; sekarang GUI v2
  mempunyai foto lokal, game DEMO, checkout MOCK dan adapter Sandbox opt-in.
  Produksi/POS/promo QRIS tepercaya tetap berbeda dan belum aktif.
- Instruksi membuat branch dari master diganti dengan melanjutkan branch v2
  yang sudah ada. Master dan tag v1 disimpan sebagai baseline historis.
- Harga lama per quantity/session di prototype tidak berlaku untuk v2: satu
  sesi tiga foto per desain, jumlah 0–9 menentukan lembar; Rp5.000/desain +
  Rp5.000/lembar. Kemenangan mengurangi MOCK Rp2.500 sekali/order; Sandbox
  meminta konfirmasi harga penuh tanpa promo, sampai ada kontrak backend promo.
- Istilah FEAT-021 dipakai tiga topik terpisah: Meong Fly, AI Background Studio
  dan rencana WhatsApp. Pertahankan ID historis dan selalu tambah nama/branch;
  jangan menganggapnya satu fitur atau diam-diam merombak nomor. GUI v2 tetap
  **FEAT-022**, QRIS **FEAT-020**.
- UI/audio v1, prototype Tkinter, scanner game standalone, AI, Device Health dan
  lab dithering terbaru tidak dinyatakan aktif hanya karena ada di branch lain.
- Bukti v2 terakhir: source **9433010**, **688 full PASS / 0 skip**,
  [CI 40109206417](https://github.com/pratikto/PhotoBooth/actions/runs/40109206417)
  tiga job SUCCESS, 109 PNG terverifikasi. Native CI punya satu skip model palm
  opsional; local full dengan aset model mencakupnya. Bukti ini tidak dipindah
  menjadi PASS provider/Windows/paper/Drive.

## Aturan reuse untuk pekerjaan berikutnya

Sebelum port fitur, refresh SHA remote branch terkait, baca kode/GUI/tesnya,
periksa kecocokan dengan adapter v2, dan reuse implementasi yang bekerja.
Catat pengecualian konkret dan hash sumber. Audit ini tidak mengotorisasi
integrasi baru, merge, penghapusan branch, pembayaran produksi atau deployment.
Lihat [rencana menjadikan GUI v2 branch utama](gui-v2-promotion-plan.md).
