# FEAT-022 — Meong Photobooth GUI v2: spesifikasi dan roadmap

Status **25 Oktober 2026**. Pusat pengembangan/calon branch utama:
**feature/portrait-kiosk-v2-next**. Default GitHub masih master. Source fungsional
terakhir **9433010**; bukti **0dc6555**. [Handover](DEVELOPMENT_HANDOVER.md).

GUI v2 melanjutkan proyek yang sudah ada, dengan GUI/audio owner tersendiri dan
reuse backend/renderer yang bekerja. Tidak memulai ulang kamera, template,
printer, Drive, game atau payment service. [Audit branch](gui-v2-branch-audit.md).

## Operator increment setelah persiapan P5

Owner pada 25 Oktober meminta safe source development terus berjalan meskipun
laptop belum sempat diuji, dan menegaskan reuse v1. Device Health read-only dengan
actual panel/worker existing sekarang dipasang melalui adapter v2, plus ekspor
laporan lokal yang redacted. [Panduan/bukti dan form operator](qa/portrait-v2-operator-health/README.md).
Gate merchant/perangkat tetap terpisah, bukan alasan memulai ulang atau berhenti
pada source work yang aman. Tidak ada perubahan default branch/produksi.

## Alur dan aturan produk

1. **Iklan** adalah halaman pertama. MULAI FOTO, MAIN MEONG FLY, CARA PAKAI dan
   undangan ada pada satu permukaan media; undangan wajah adalah overlay.
2. **Tutorial wajib sekali per kunjungan**, direct maupun setelah menang/kalah:
   Pilih Template → Bayar → Ambil 3 Foto → Cetak & Scan QR. Langkah yang
   menggambarkan layanan tidak berarti semua integrasi produksi aktif.
3. **Galeri** berisi 12 template asli 80×240 mm, 3 slot foto + 1 QR download.
   Swipe/panah bergeser nyata, strip tengah fokus; −/jumlah/+ menentukan 0–9
   lembar per desain, satu sesi tiga foto per desain terpilih.
4. **Lokal/default:** UJI FOTO → persetujuan → tiga capture/countdown lima detik →
   review/satu retake → komposisi/hasil → iklan. Printer/Drive opt-in operator.
5. **Game DEMO:** intro → kode DEMO sekali pakai → game asli → menang/kalah →
   tutorial jika belum dilalui → galeri. Tidak ada main ulang; scanner/POS nyata
   tetap tidak aktif. Kode yang sudah dipakai tetap ditolak setelah restart.
6. **MOCK opt-in:** checkout lokal berlabel nonpayable, ledger diskon/quote dan
   satu admission menuju persetujuan foto. Menang: Rp2.500 sekali/order, capped.
7. **Sandbox opt-in:** konfirmasi harga penuh/tanpa promo → QR provider Sandbox →
   backend memverifikasi settlement → grant → persetujuan foto → journal STARTING →
   satu transaksi foto → ACK STARTED → capture → seluruh desain selesai → ACK
   COMPLETED. Pending/unknown/paid/recovery tidak dibuang oleh timeout browsing.

Tarif source: **Rp5.000 per desain/sesi + Rp5.000 per lembar**. Satu desain satu
lembar Rp10.000, dua lembar Rp15.000. MOCK menang menjadi Rp7.500/Rp12.500.
Sandbox **belum menerima promo game**: backend referensi belum punya kontrak
bukti promo. Tidak boleh mengirim skor/amount GUI sebagai otoritas diskon.
QR pembayaran berbeda dari QR folder/download hasil foto.

## Roadmap dan gate yang sebenarnya

| Tahap | Source sekarang | Bukti / gate tersisa |
| --- | --- | --- |
| P0 | VisitFlow/tutorial-once/protected lifecycle | Regresi source tersedia |
| P1 | Audio v2 satu owner, WAV SDL2, minimize/close, SFX | Owner melaporkan audio v2 normal; regresi perangkat P5 tetap khusus source yang diuji |
| P2/P2.5/P2.6–P2.8 | Iklan/overlay/tutorial/galeri responsif, swipe/transisi/header dan tipografi terbaru | Laporan Windows terdahulu diterima sesuai metadata; screenshot source akhir tersedia |
| P3a | Kamera async, face invitation, preview mirror, optional palm | Owner melaporkan perbaikan respons/preview/palm; reconnect/fisik/metadata masih mengikuti checklist |
| P3b | Tiga foto asli, retake per desain, komposisi, print/Drive opt-in | Default lokal; paper/Drive/retensi tidak disimpulkan dari tes mock |
| P4a | Renderer/flow/aset game terbaru direuse langsung, DEMO ledger satu kesempatan | Game/visual owner-reported PASS; POS/scanner nyata tidak aktif |
| P4b MOCK | Quote/ledger/promo/admission lokal | Sudah dalam source/regresi, tidak merupakan pembayaran bank |
| P4b Sandbox | Service/client/journal QRIS existing + native v2 adapter dan launcher terisolasi | Merchant simulator/perangkat belum diuji; promo QRIS tepercaya belum tersedia |
| P5 | Readiness CLI, form Submit/import metadata, regresi dan paket screenshot/rollback | **SIAP ACCEPTANCE, BELUM SERTIFIKASI**: Windows integrasi baru, merchant, printer, privasi/Drive dan signoff |
| Transisi branch utama | Arah owner tercatat; audit 19 branch selesai | Operasi default/rename/merge/launcher/release belum dilakukan; [rencana](gui-v2-promotion-plan.md) |

Owner pada 24 Oktober meminta P4b lalu P5, uji manual di akhir. Pada 25 Oktober
menyampaikan preflight **HEAD 0dc6555 → READY_FOR_MANUAL_TEST**. Output ini tidak
mencakup acceptance kamera/speaker/merchant/printer/Drive; metadata file yang
belum dikirim tidak diisi dari laporan lama.

## Visual dan media yang dipertahankan

Portrait 10.1 inci, referensi **800×1280** dan **452×900**, dengan resize kecil/
landscape. Cosmic pixel space dan frame tombol dari game; caption aplikasi
utama **native Roboto yang bersih, tanpa ikon wajib**, bukan bitmap caption yang
sudah ditolak. Wordmark MEONG PHOTOBOOTH terpusat; Meong animasi lebih besar,
sejajar, dengan kaki/pelangi/print dan efek tabrakan wordmark.

Iklan gambar memakai BGM GUI; video memakai audionya sendiri. Tutorial/galeri/
foto/Sandbox berbagi BGM tanpa restart berlapis; game memakai musik berbeda.
Setiap aksi tombol aktif berbunyi sekali. Minimize/close dan perpindahan halaman
mengakhiri owner/callback lama dengan aman.

![Main photobooth approved artboard](assets/portrait-v2/meong-main-flow-approved.webp)

![Meong Fly approved artboard](assets/portrait-v2/meong-fly-revised-approved.webp)

[Interpretasi visual terkini](portrait-kiosk-v2-visual-spec.md) ·
[asal dan hash aset](assets/portrait-v2/README.md). Artboard adalah arah visual;
nominal contoh dan panah lama tidak mengubah alur/tarif source.

## Pengujian dan kelanjutan

Source 9433010: **688 full PASS / 0 skip**, CI tiga job SUCCESS,
109 PNG source/hash/dimensi terverifikasi. Native CI punya satu skip aset palm
opsional; local full dengan aset model mencakupnya. Semua bukti dibedakan dari
perangkat/provider. [P5](qa/portrait-v2-p5/README.md) ·
[form 26 item](qa/portrait-v2-p5/windows-checklist.html) ·
[status fitur](FEATURE_STATUS.md) · [bug](bug_tracker.md).

Gunakan [README](../README.md) untuk perintah launcher. Produksi, promo QRIS,
scanner/POS, deployment, merge dan rilis tidak diaktifkan. Jangan menghapus
journal untuk melewati order yang belum pasti; operator harus rekonsiliasi.
Master/tag v1 dan seluruh branch referensi tetap dipertahankan.
