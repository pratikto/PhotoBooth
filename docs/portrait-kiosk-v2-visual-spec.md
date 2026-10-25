# FEAT-022 — Spesifikasi visual dan interaksi GUI v2

Status **25 Oktober 2026**. Branch `feature/portrait-kiosk-v2-next`, source
fungsional **9433010**. Dokumen ini membedakan keputusan tampilan, implementasi
aktif dan gate acceptance. [Roadmap](portrait-kiosk-v2.md) · [fitur](FEATURE_STATUS.md).

## A. Main photobooth approved concept board

![Approved main concept](assets/portrait-v2/meong-main-flow-approved.webp)

## B. Meong Fly approved concept board

![Approved revised Meong Fly concept](assets/portrait-v2/meong-fly-revised-approved.webp)

[Asal/hash aset](assets/portrait-v2/README.md). Artboard adalah arah visual;
contoh harga Rp25.000, panah menuju pembayaran setelah game, dan ilustrasi
scanner tidak menjadi kontrak alur/tarif atau bukti integrasi produksi.

## Koreksi owner yang berlaku

| Area | Keputusan dan implementasi sekarang |
| --- | --- |
| Identitas | Cosmic navy/pixel-space, cyan/pink/gold, frame tombol dari game asli; jangan mendesain ulang mascot |
| Tipografi | Wordmark Meong bergaya pixel; **caption tombol aplikasi utama native Roboto, bersih, tanpa ikon wajib**. Bitmap caption yang ditolak bukan standar v2 |
| Header | Wordmark terpusat. Meong animasi besar sejajar tulisan, terbang dua arah; kaki/bagian belakang, pelangi dan print bergerak; kontak memutar wordmark satu kali lalu kembali rapi |
| Halaman pertama | Media iklan dengan CTA direct/game/help. Undangan berada di atas permukaan iklan yang sama, bukan home terpisah |
| Tutorial | Empat langkah sesuai urutan, scroll sampai akhir; acknowledgement sekali per kunjungan, reset ketika aman kembali idle |
| Galeri | 12 strip asli rasio 1:3; tiga preview utuh dengan strip tengah fokus. Judul PILIH TEMPLATE STRIP mengambang di dalam box di atas desain |
| Panah/swipe | Panah mengambang di sudut bawah kiri/kanan preview; gambar mengikuti drag dan slide nyata. Vertikal/gerakan pendek tidak mengganti pilihan |
| Ringkasan | − / jumlah / + terpusat di kolom kiri, lembar/sesi singkat; total/hemat di kanan. Label CETAK di samping kontrol sudah dihapus |
| Game | Original Stage/Flow/render/assets, satu scene menyatu hingga sisi window, responsif tanpa distorsi/kecepatan nonlinear. Meong tetap di kiri area permainan |
| Game navigation | Intro/scan/hasil tanpa KEMBALI KE IKLAN; AKHIRI GAME saat bermain tetap tersedia. Win/Lose → tutorial iff unseen → template, tanpa MAIN LAGI |
| Mouse | Klik kanan tidak membuat titik multitouch atau menjalankan action |
| Audio | Gambar iklan+BGM GUI; video+audio sendiri; loop game terpisah. Tombol aktif sekali cue pada semua halaman, minimize/close tidak meninggalkan suara |
| Harga | Satu sesi/desain + N lembar; MOCK win diskon sekali. Sandbox menampilkan harga penuh/tanpa promo sebelum order dibuat |
| Camera/result | Preview mirror; original/review/print tidak dicerminkan. Maksimum satu retake/desain, jumlah lembar tidak menambah pose |

## C. Corrected navigation — two entry paths, one photo journey

Direct: iklan/undangan → tutorial jika belum dilalui → galeri.
Game: iklan/undangan → intro → **kode DEMO manual** sekali pakai → gameplay →
menang/kalah → tutorial jika belum dilalui → galeri. Scanner nyata/POS tetap off;
kemampuan scan pada branch game standalone bukan otomatis fitur GUI v2.

Dari galeri, jalur lokal memakai UJI FOTO dan persetujuan. MOCK opt-in mempunyai
QR simulasi nonpayable. Sandbox khusus memakai konfirmasi harga, provider QR,
status/grant backend lalu persetujuan foto. Jangan tampilkan kontrol manual
untuk memalsukan PAID di mode Sandbox. [Kontrak teknis](portrait-kiosk-v2-technical-design.md).

## D. Screen inventory — more than nine screens

| ID | Screen/state | Source v2 sekarang |
| --- | --- | --- |
| M00 | Iklan | Aktif, image/video/fallback, CTA direct/game/help |
| M01 | Undangan inline | Manual DEMO dan face inviter optional; batas sensor/perangkat tetap diuji |
| M02 | Tutorial | Aktif, empat langkah/scroll/acknowledgement |
| M03 | Galeri/quantity/total | Aktif, 12 template asli, swipe, count, quote dan promo simulasi |
| M04 | Cart/promo | Ringkasan di galeri; MOCK divalidasi ledger lokal, promo QRIS belum tersedia |
| M05 | Payment waiting | MOCK atau Sandbox opt-in yang dibedakan jelas; default payment nonaktif |
| M06 | Cancel/unknown/recovery | State safety aktif; operator hold bukan bebas kembali idle |
| M07 | Persetujuan/kamera | Foto lokal atau setelah grant Sandbox; kesiapan kamera tetap nyata |
| M08 | Countdown ×3 | Aktif, lima detik, shutter setelah capture berhasil |
| M09 | Review/retake | Aktif, satu retake satu foto per desain |
| M10 | Composition/delivery/print | Source tersedia; default lokal, printer/Drive opt-in; uncertain print tidak diklaim sukses |
| M11 | Result/QR download | Strip dan status benar; QR hanya saat folder valid tersedia, bukan QR pembayaran |
| M12 | Safe finish/idle | Reset visit/cart ketika aman; payment/photo/print pending dilindungi |
| G00/G01 | Intro/rules | Original renderer terintegrasi; satu kesempatan dan simulasi reward |
| G02 | Receipt DEMO | Input DEMO, duplicate rejection; POS/scanner produksi tidak aktif |
| G03 | Gameplay/pause | Original animation/physics dengan layout adapter responsif |
| G04/G05 | Win/Lose | Tanpa replay; lanjut tutorial/galeri, reward tidak menjadi payment authority |

## QA visual yang harus dijaga

800×1280 dan 452×900 wajib, juga 360×640, window pendek/lebar dan Windows scaling
saat tersedia. Tidak ada strip gepeng/terpotong, caption keluar frame, hasil resize
yang mereset sesi, animasi lama yang tertinggal, atau tombol tertutup panel lain.
Nilai win/price harus sesuai mode yang ditampilkan.

[109 screenshot source 9433010](qa/portrait-v2-p5/ci-screenshot-verification.json),
[Sandbox contact](qa/portrait-v2-p5/sandbox-contact.jpg),
[galeri/foto/game](qa/portrait-v2-p5/regression-contact.jpg).
Owner melaporkan visual/audio terakhir 8/8 dan “udah clear semua”, pada HEAD yang
tidak dicatat; bukti itu tetap owner-reported. Preflight HEAD 0dc6555 sudah siap,
namun [Windows acceptance P5](qa/portrait-v2-p5/windows-checklist.html) belum dikirim.

Riwayat konsep/screen target sebelum P3/P4 tersedia pada
[versi sebelum konsolidasi](https://github.com/pratikto/PhotoBooth/blob/0dc6555d299cdab19d952e92df2ae660cdc4676d/docs/portrait-kiosk-v2-visual-spec.md).
Jangan mengubah status perangkat/provider menjadi PASS berdasarkan gambar mock.
