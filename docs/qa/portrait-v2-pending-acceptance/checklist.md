# Checklist semua gate GUI v2 yang belum teruji (49 item)

Tanggal: ____  HEAD: ____  Branch: feature/portrait-kiosk-v2-next

Windows/resolusi/scaling: ____  Kamera/index: ____  Speaker: ____

Booth/profil: ____  Printer uji/lebar cetak: ____

Putaran Sandbox BARU selesai: ____

Centang hanya hasil aktual yang lulus. Kosong = gagal/belum diuji. Laporan lama tetap dicatat. G01/G02 memerlukan minimal 20 putaran Sandbox baru; tidak memakai hitungan foto/game lama.

## A. Profil Windows dan integrasi build terbaru

- [ ] A01 Jalankan check_portrait_v2.py; impor JSON, lalu cocokkan HEAD/branch, Windows, resolusi, scaling, kamera/index dan speaker dengan perangkat yang benar. READY_FOR_MANUAL_TEST tidak meluluskan tes.
- [ ] A02 Launcher biasa membuka iklan lalu tutorial wajib dan galeri. Profil layout 2 membuat PB00X/Local, Cache, _state dan minimal 25 folder READY lokal yang benar-benar kosong. Default tanpa --print/--drive tidak mengirim cetak/upload atau transaksi.
- [ ] A03 Pada profil baru, pilih A×2 + B×1: dua sesi Photo/01 dan Photo/02. Tiga foto dan satu retake per desain bekerja; raw menyimpan semua JPEG asli pada resolusi/orientasi kamera, color dan bw berisi strip yang disetujui.
- [ ] A04 Cek touchscreen pada 800×1280 dan 452×900; bila tersedia 360×640 dan scaling Windows yang dipakai. Consent, strip/QR/status, panel operator dan semua tombol terjangkau; resize tidak menghapus foto, pilihan atau jumlah.
- [ ] A05 Cek singkat kamera pada profil baru: preview bergerak tanpa perlu tap, countdown lima detik, satu shutter per foto berhasil. Kamera terputus/minimize membatalkan countdown; pulihkan tidak memakai frame lama atau memotret otomatis.
- [ ] A06 Cek singkat game/audio/tombol pada build yang dicatat: game asli dan kode DEMO sekali pakai, posisi/gerak saat resize, satu aksi/satu bunyi. Musik gambar/video/game sesuai halaman; minimize/keluar tidak meninggalkan suara. Laporan lulus lama tetap disimpan; tidak perlu mengulang 20 putaran lokal.

## B. Cetak fisik dan hasil mirror — printer uji

- [ ] B01 Dengan --print, pilih satu desain dua lembar. Setelah tiga foto disetujui, cetak mulai otomatis dan benar-benar keluar tepat dua strip identik/cut. Status spool sukses saja tidak cukup.
- [ ] B02 Pilih A×2 + B×1: keluar dua strip A dan satu B dari dua sesi foto, bukan tiga sesi. Desain dan jumlah lembar fisik sama dengan pilihan.
- [ ] B03 Bandingkan preview/review, color, bw, kertas dan strip digital: area foto mirror konsisten, teks/logo/QR normal, tanpa mirror dua kali. Cek desain kotak dan hati, clipping serta kualitas pada lebar printer yang dikonfigurasi.
- [ ] B04 Saat folder Drive nyata sudah diketahui, pindai QR di KERTAS dengan ponsel. QR terbaca dan membuka folder transaksi yang benar; cek margin/ukuran QR dan hasil cetak, bukan hanya QR di layar.
- [ ] B05 Saat printer uji mengirim, tap persetujuan/kontrol cepat, resize dan minimize/pulihkan. GUI tetap responsif; tepat satu batch per desain, tanpa antrean aksi lama atau lembar tambahan.
- [ ] B06 Pada kegagalan printer/interupsi kirim yang diuji secara terkontrol, aplikasi menahan hasil UNCERTAIN untuk inspeksi. Restart tidak mengaku kertas sudah keluar atau mengirim ulang otomatis; operator memeriksa kertas/journal sebelum lanjut.

## C. Drive nyata, offline dan pemulihan antrean

- [ ] C01 Dengan --drive dan backend siap, transaksi uji mengunggah semua raw termasuk retake, color dan bw ke Photo/NN yang benar. Status terverifikasi baru muncul setelah semua berkas diakui; tidak bercampur dengan transaksi/booth lain.
- [ ] C02 Pindai QR BESAR DI LAYAR menggunakan ponsel sebagaimana pengunjung tanpa login operator. Folder/unduhan benar dan berkas lengkap; raw tetap asli, strip digital mirror sesuai hasil. UPLOAD_COMPLETE saja tidak cukup.
- [ ] C03 Setelah folder nyata tercadangkan dan tersimpan lokal, putuskan koneksi. Foto/cetak tetap bekerja memakai tujuan yang sama; setelah online, berkas masuk ke folder yang sama tanpa duplikasi dan tanpa cetak ulang.
- [ ] C04 Pada profil uji yang pertama kali dijalankan OFFLINE tanpa cadangan Drive, foto/cetak lokal tetap bisa dimulai. Tanpa tujuan nyata, tidak ada QR palsu; kertas menyebut upload tertunda. Online kembali mengikat ID transaksi yang sama.
- [ ] C05 Uji kondisi cadangan Drive HABIS pada profil uji khusus: transaksi berikut tetap berjalan lokal dengan ID unik, termasuk setelah restart. Jangan menghapus counter/ledger untuk memaksa kondisi ini. Belum mencoba kondisi habis berarti kosong.
- [ ] C06 Selesaikan kunjungan saat upload tertunda, tutup lalu buka lagi dengan --drive. Antrean lama selesai tanpa foto/charge/cetak baru dan tanpa menulis ulang color/bw. Jika halaman hasil sudah ditutup, operator mengambil hasil menurut ID; idle tidak menampilkan foto pengunjung lama.
- [ ] C07 Buat foto dengan Drive NONAKTIF, lalu buka aplikasi dengan --drive. Foto LOCAL_ONLY tersebut tidak ikut diunggah diam-diam; hanya transaksi dengan niat Drive yang melanjutkan antrean.

## D. Setup Google dan cache global/lokal — FEAT-004

- [ ] D01 Perbarui Code.gs di project yang benar, jalankan setupBoothStorage dan deploy versi baru pada /exec yang sama. Root memiliki Global_Advertisement, Global_Template dan Photobooth/PB00X/Local/Advertisement serta Local/Template; token tetap lokal, isi old tidak dibuka/diubah.
- [ ] D02 Setelah --drive tersambung, tiap booth/profil uji memiliki minimal 25 folder transaksi READY Drive yang kosong. Jika dua profil tersedia, cek PB001 dan PB002 memakai folder/ID/ledger yang terpisah; jangan menganggap booth kedua lulus tanpa dicoba.
- [ ] D03 Pasang aset iklan global dan aset khusus booth: setiap booth yang diuji punya salinan global, aset lokal hanya tampil di booth tujuan. Playlist/jadwal/durasi sesuai konfigurasi; gambar memakai musik GUI, video audio sendiri dan pergantian video tidak membekukan kontrol.
- [ ] D04 Sinkronkan pack template lengkap (layout_80mm.json, PNG dan mask) dan template lokal. Galeri/hasil sesuai pack; global berlaku di semua booth yang diuji, lokal hanya di booth tujuan. Tanpa pack global, 12 desain bawaan tetap tersedia.
- [ ] D05 Setelah sinkronisasi lengkap, putuskan Drive lalu tutup/buka aplikasi: iklan dan template global/lokal tetap tersedia dari cache. Aset yang belum pernah diunduh tidak dianggap tersedia offline.
- [ ] D06 Putuskan unduhan pembaruan atau gunakan pack uji yang tidak valid: versi lama tetap dapat dipakai; pembaruan tidak aktif sebagian. Sesudah berkas lengkap dan valid, versi baru dapat diaktifkan.
- [ ] D07 Saat sinkron selesai di tengah pemilihan/foto/review atau panel Device Health terbuka, halaman/pilihan/foto/panel tetap utuh. Konten baru aktif hanya saat idle setelah overlay/panel ditutup, tanpa audio ganda atau data sesi tereset.

## E. Retensi aktual — BUG-009 tetap terbuka sampai ada bukti

- [ ] E01 Jalankan setupPhotoRetention sebagai akun pelaksana Web App yang benar. Drive API v3 siap dan tepat satu trigger cleanupPhotoRetention bertipe CLOCK dijadwalkan tiap jam; trigger lain tetap utuh.
- [ ] E02 Deploy versi baru backend, lalu check_drive_retention.py dengan default layout 2 menunjukkan READY untuk booth yang dipakai. Catat hasil aman; READY tidak dianggap bukti foto terhapus.
- [ ] E03 Jalankan diagnosis lagi: hanya membaca status, tanpa membuat folder, upload, memasang trigger atau meminta penghapusan. Laporan tidak memuat token/key, URL/ID sensitif atau raw log.
- [ ] E04 Pada kondisi uji ketika ACK retensi/timer belum siap, upload ditahan tanpa status terverifikasi palsu. Foto/cetak lokal tetap berjalan; setelah setup benar, transaksi yang sama dapat melanjutkan tanpa reprint.
- [ ] E05 HANYA pada fixture sintetis yang diotorisasi, buktikan foto lokal setelah 15 hari dihapus dari raw/color/bw, sementara manifest/tombstone/counter, aset/cache dan folder READY tetap ada. Jangan memakai foto pelanggan atau mengubah jam Windows.
- [ ] E06 HANYA pada fixture sintetis yang diotorisasi, cleanup aktual menghapus permanen transaksi Drive yang lewat 30 hari, bukan sekadar Trash. Termasuk transaksi lama yang baru mendapat folder saat reconnect; tanpa pengujian penghapusan nyata, kosong.
- [ ] E07 Retry registrasi, reconnect dan restart tidak memperpanjang tanggal mulai/kedaluwarsa asli. Foto lokal yang sudah kedaluwarsa tidak hidup kembali/terunggah ulang akibat callback atau reconnect terlambat.
- [ ] E08 Amati eksekusi trigger per jam yang benar-benar sukses saat GUI tertutup. Foto yang belum kedaluwarsa, aset, READY dan booth di luar scope tetap terlindungi; buktikan scope/log tanpa membuka isi old.

## F. QRIS Sandbox akun asli — simulator resmi saja

- [ ] F01 Akun Sandbox benar-benar dapat diakses. Launcher khusus meminta Merchant ID dan Sandbox Server Key tersembunyi; backend/GUI terbuka. Key tidak ada di GUI/laporan. Tanpa akses akun, bagian Sandbox tetap belum diuji.
- [ ] F02 Gallery → QRIS SANDBOX menampilkan persetujuan harga penuh/tanpa promo game sebelum order dibuat. Harga satu desain satu/dua lembar Rp10.000/Rp15.000; A×2 + B×1 Rp25.000. Diskon DEMO tidak mengotorisasi diskon provider.
- [ ] F03 QR dari provider Sandbox nyata tampil dan simulator RESMI menunjukkan order/jumlah yang sama. Jangan menggunakan aplikasi bank/dompet atau endpoint produksi.
- [ ] F04 Sebelum settlement simulator diverifikasi backend, foto tidak dapat dimulai; UJI FOTO tidak bisa melewati checkout, timeout browsing tidak membuang order aktif.
- [ ] F05 Settlement simulator diverifikasi backend → consent foto → tiga foto/review/hasil → seluruh desain selesai. STARTED/COMPLETED tercatat sesuai alur; tidak ada override PAID manual.
- [ ] F06 Tap lanjut/status cepat berulang: hanya satu order/charge provider, satu grant dan satu transaksi foto. Saldo/hasil yang belum diverifikasi tidak dianggap lunas.
- [ ] F07 Putuskan koneksi/backend saat menunggu, kemudian pulihkan: status tak pasti tetap menahan alur; refresh memulihkan order yang sama tanpa permintaan pembayaran baru.
- [ ] F08 Batalkan order pending: keluar hanya setelah status terminal dikonfirmasi backend. Jika settlement menang saat pembatalan, hak foto tetap terjaga.
- [ ] F09 Tutup/buka saat pending atau sudah dibayar tetapi belum capture: order yang sama dipulihkan tanpa charge baru. Jangan menghapus journal untuk melewati recovery.
- [ ] F10 Abort/restart setelah capture mungkin dimulai: masuk bantuan operator/RECOVERY; tidak otomatis mengulang foto, cetak, refund atau reset. Operator mencocokkan journal dan manifest dahulu.

## G. Ketahanan integrasi Sandbox baru

- [ ] G01 Selesaikan minimal 20 putaran BARU Sandbox → foto → hasil → iklan, dengan resize/minimize di beberapa putaran: tanpa crash, lag mengganggu, audio hilang, charge atau sesi ganda. Dua puluh putaran foto/game lama tidak dihitung di sini.
- [ ] G02 Sesudah minimal 20 putaran Sandbox tersebut, tutup/buka aplikasi: kamera/audio normal, order selesai tetap selesai, tidak ada charge/capture/cetak otomatis atau suara tertinggal.

## H. Privasi dan review paket acceptance

- [ ] H01 Operator meninjau consent foto, siapa yang dapat mengakses folder/unduhan, retensi dan penyimpanan lokal. Parent booth/global tidak dibuka untuk pengunjung; QR hanya menunjuk transaksi sendiri, idle tidak membocorkan foto lama.
- [ ] H02 Impor/simpan laporan readiness, operator dan retensi dari perangkat aktual: metadata sesuai, tanpa foto pelanggan, token/key, raw log atau identitas sensitif. Bukti yang dibagikan cukup disamarkan.
- [ ] H03 Operator/owner meninjau hasil yang benar-benar diuji, kegagalan/item kosong, source yang dipakai dan checkpoint rollback. Journal/counter dipertahankan; review ini tidak menjalankan atau mengotorisasi merge, perubahan default branch, deployment layanan atau rilis produksi.

## Catatan masalah / alasan belum diuji

____

Tidak ada aktivasi produksi, scanner/POS, webhook publik, promo QRIS tepercaya, merge/default branch atau rilis dalam checklist ini. Tidak membuka/mengubah old.
