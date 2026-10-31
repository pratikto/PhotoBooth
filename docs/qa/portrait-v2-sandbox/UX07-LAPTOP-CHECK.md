# Cek laptop Meong — panduan untuk pemilik, langkah demi langkah

Gunakan [form yang bisa dicentang dan disalin](windows-checklist-ux07.html).
Petunjuk di bawah sama dengan petunjuk di dalam form. Hasil manual masih
**NOT_RUN** sampai dicoba di laptop; fixture otomatis tidak mengisi hasilmu.

## Persiapan

Siapkan laptop Windows, internet, kamera, ponsel untuk menyimpan tiket dan
akun **Midtrans Sandbox**. Printer/Drive tetap **OFF**. Jangan memakai bank atau
e-wallet asli. Uji dengan foto/objek yang boleh kamu gunakan.

Buka folder PhotoBooth di File Explorer, klik bilah alamat, ketik `powershell`,
lalu Enter. Periksa branch dan perubahan lokal:

```powershell
git branch --show-current
git status --short
```

Branch harus `feature/portrait-kiosk-v2-next`. Keluaran status kosong = bersih.
Jika ada perubahan yang tidak dipahami atau branch berbeda, catat dan berhenti
sebelum update; jangan reset/clean. Jika branch sesuai dan perubahan aman:

```powershell
git pull --ff-only origin feature/portrait-kiosk-v2-next
git rev-parse HEAD
Start-Process "docs/qa/portrait-v2-sandbox/windows-checklist-ux07.html"
.\.venv-kivy\Scripts\python.exe tools\run_portrait_v2_sandbox.py
```

Jika lingkunganmu `.venv`, gunakan `.\.venv\Scripts\python.exe`.
Jika lingkungan Kivy sudah aktif, `python tools/run_portrait_v2_sandbox.py`
juga boleh. Jangan memakai `main.py` (v1) atau launcher biasa untuk rangkaian ini.
Biarkan PowerShell terbuka. Isi Merchant ID/Server Key Sandbox di laptop jika
diminta; key disembunyikan, bukan diketik di chat. Pengaturan lokal yang sudah
lengkap bisa menghilangkan prompt. Jangan menimpa pengaturan yang sudah ada.

Untuk versi, jalankan sebelum app atau di PowerShell kedua pada folder sama:

```powershell
.\.venv-kivy\Scripts\python.exe --version
.\.venv-kivy\Scripts\python.exe -m pip show Kivy opencv-python
```

Ganti path bila memakai `.venv`. Catat `Name`/`Version`, bukan semua keluaran.
Windows: Settings → System → About. Layar: System → Display → resolution/Scale.
Resolusi layar berbeda dari ukuran jendela aplikasi. Model kamera boleh ditulis
“bawaan laptop, model belum tahu”; data yang belum diketahui jangan ditebak.

## Cara memilih hasil

- **Lulus / PASS**: semua bagian wajib pada item sudah dicoba dan sesuai.
- **Gagal / FAIL**: ada perilaku salah/error saat benar-benar dicoba.
- **Belum diuji / NOT_RUN**: belum mulai, baru sebagian, atau tertahan langkah lain.
  Hasil parsial tulis di catatan per item. Jika L02 gagal, L03–L08 yang belum
  bisa dicoba tetap NOT_RUN, bukan ikut FAIL. Sentuh tidak berlaku jika perangkat
  tanpa touchscreen; ukuran/reconnect yang tidak diuji tetap keterbatasan.

Urutan: **L01 → L02 → L03 → L04 → L05 → L06 → L07**; simpulkan L06 lengkap
setelah membandingkan foto/retake pada L07. L08 lanjutan dan boleh ditunda.
L09 diamati sepanjang rangkaian. Kamu sendiri boleh memakai PIN operator lokal;
tidak perlu orang pendamping. PIN berubah saat launcher dimulai ulang.

Form menyimpan hasil di browser itu saja. Jika hasil lama muncul, itu bukan
bukti untuk SHA baru. Salin/unduh laporan lama sebelum Kosongkan Form untuk cek
versi baru. Catatan per item dan hasil parsial ikut masuk prompt. Placeholder
contoh bukan hasil pengujian dan tidak ikut disalin jika tidak kamu isi.

## Jika QR pembayaran kedaluwarsa saat L02

Ini berbeda dari restart pesanan yang masih PENDING. Tunggu status expire resmi
dari Midtrans; jangan mengubah jam, database, jurnal atau status lewat kode.
Saat kunjungan masih aktif, expiry yang terverifikasi dan belum dibayar akan
diarsipkan, lalu satu QR pengganti disiapkan di checkout yang sama. Desain,
jumlah lembar dan nominal tetap. Pesanan/ID/QR pengganti serta tiketnya baru.

1. Di **SIMPAN TIKET BARU**, simpan QR tiket baru secara pribadi. Tiket lama
   bukan bukti untuk pesanan pengganti. Klik **SUDAH SIMPAN • TAMPILKAN QRIS**.
2. Lihat pesan **QR sebelumnya kedaluwarsa. Silakan gunakan QR terbaru.**
   Salin link QRIS lagi; jangan memakai URL lama di simulator.
3. Jika QR pengganti kedaluwarsa lagi, app menampilkan **BUAT QR BARU**. Klik
   jika masih ingin melanjutkan; pilihan tidak perlu diulang. Jika tombol itu
   tidak ditekan selama **30 detik**, app kembali ke iklan dan arsip tetap ada.
4. Untuk cek timeout, catat bahwa tetap di checkout sebelum 30 detik, lalu
   kembali ke iklan setelah 30 detik. Rebuild/status background tidak mengulang
   hitungannya. Timer tidak melepas status yang belum pasti atau proses sibuk.

Jika kamera/penyimpanan/koneksi belum siap, QR baru ditahan dengan pesan retry.
PAID tetap mengikuti sesi asli; pembayaran terlambat setelah terminal mengikuti
peninjauan pesanan lama, bukan melunasi pesanan pengganti. Restart/minimize
tidak mengizinkan pembaruan otomatis. Saat startup, unpaid expiry terverifikasi
bisa kembali ke iklan. Tidak perlu PIN/tiket untuk menutup pesanan yang memang
belum dibayar dan tidak punya layanan/foto/kewajiban. Kasus paid tetap terpisah.

Isi catatan L02 dengan hasil pembaruan/timeout. Jika belum menunggu expiry resmi,
tulis bagian ini NOT_RUN; perubahan ID setelah expiry terverifikasi memang
diharapkan. Perbandingan ID harus tetap sama pada uji restart **selama PENDING**.

## Jika langsung ke pemulihan atau gagal mulai

`SESI TERSIMPAN / TIKET PELANGGAN DIPERLUKAN` setelah restart merupakan penjagaan
privasi. Pakai tiket asli → VERIFIKASI TIKET → PULIHKAN SESI FOTO ASLI.
Tiket berbeda dari QR pembayaran, PIN operator dan Server Key. Tiket Sandbox
berlaku 24 jam; simpan secara pribadi sebelum menampilkan QR pembayaran.

Tanpa tiket lama, BANTUAN OPERATOR jika tersedia hanya untuk membaca status
dengan PIN launcher terbaru; PIN tidak menggantikan bukti pemilik foto.
Jika hasil pemeriksaan menunjukkan **PAID / STARTED / OWED** dan muncul
**ARSIPKAN UJI TANPA TIKET**, ini jalur khusus pesanan Sandbox lama yang tidak
pernah terikat tiket. Kamu sendiri boleh menjalankannya:

1. Klik **ARSIPKAN UJI TANPA TIKET**. Baca konfirmasi; klik pertama belum
   mengarsipkan/melepas apa pun. Foto lama tetap terkunci. Batal tersedia.
2. Masukkan PIN launcher terbaru lagi, lalu **KONFIRMASI ISOLASI UJI**.
3. Tunggu pesan sesi lokal sudah diisolasi. Masukkan PIN lagi lalu
   **LEPAS BOOTH • HAK TETAP DISIMPAN**.
4. Setelah kembali ke iklan, mulai kunjungan uji baru melalui alur biasa.
   Simpan tiket baru sebelum menampilkan QR pembayaran, lalu mulai L02 dari awal.

Pesanan/foto/kewajiban lama tetap disimpan untuk pemeriksaan pemilik; ini tidak
menghasilkan tiket pengganti, membuka foto lama, menyatakan layanan selesai,
atau mengembalikan uang. Jika tombol tetap nonaktif, operasi ditolak atau
statusnya berbeda, catat pesan dan berhenti pada langkah itu. Tiket yang
sudah terikat tetapi hilang/kedaluwarsa bukan pesanan legacy tanpa tiket.
Untuk kasus dengan tiket terikat, jalur isolasi biasa tetap berlaku sesuai
syaratnya; tidak ada bypass akses foto melalui PIN. Catat uji legacy ini di
L08 sebagai hasil parsial; jangan menganggap uji kembali dengan tiket A lulus
jika tiket A memang tidak pernah ada.

Jika hanya `PERLU BANTUAN OPERATOR` tanpa tombol seperti screenshot lama,
catat SHA/perintah/teks halaman dan kirim hasil parsial. Jangan mengedit
`visit.json`, database, manifest, counter, mengganti booth, menghapus foto,
membuat profil/pesanan pengganti atau membayar lagi untuk membuka pemulihan.

`python.exe` tidak ditemukan: periksa nama folder lingkungan. `ModuleNotFoundError`:
catat nama modul/perintah. `another launcher is active`: periksa app/terminal lama,
jangan hapus lock. Setup/port/provider error: catat pesan; jangan ganti profil
untuk melewati status tersimpan. Tidak perlu memaksa crash/Task Manager/cabut listrik.

## L01 — Data laptop dan versi

**Untuk apa:** Supaya hasil cek bisa ditelusuri ke versi aplikasi dan laptop yang tepat. SHA adalah nomor versi kode, bukan password.

**Sebelum mulai:** Aplikasi boleh belum dibuka. Gunakan PowerShell di folder PhotoBooth, yaitu folder yang berisi README.md dan tools.

1. Periksa branch dan file lokal dengan perintah di bagian Persiapan.

   **Seharusnya:** Branch tertulis feature/portrait-kiosk-v2-next. git status --short tanpa keluaran berarti bersih; jika ada baris berarti ada perubahan lokal.

2. Jika branch sesuai dan tidak ada perubahan lokal, jalankan git pull --ff-only origin feature/portrait-kiosk-v2-next. Jika ada perubahan atau pull ditolak, berhenti di sini dan catat pesannya; jangan reset atau hapus file.

   **Seharusnya:** Update selesai tanpa konflik. Jika belum bisa update, metadata tetap boleh dicatat, tetapi pengujian versi terbaru belum terbukti.

3. Jalankan git rev-parse HEAD, lalu salin satu baris hasilnya ke kolom SHA. Jalankan perintah versi Python/Kivy/OpenCV di Persiapan memakai lingkungan Python yang sama untuk menjalankan app.

   **Seharusnya:** SHA berupa huruf/angka panjang. Versi paket tercetak. ModuleNotFoundError berarti paket belum ada di lingkungan yang dipakai, bukan hasil uji kamera.

4. Buka Windows Settings → System → About untuk versi Windows. Buka System → Display untuk Display resolution dan Scale. Catat jenis kamera: bawaan laptop atau merek/model USB jika tahu.

   **Seharusnya:** Kolom OS, resolusi, scaling dan kamera terisi berdasarkan laptop ini. Angka resolusi layar bukan ukuran jendela aplikasi.

5. Isi tanggal dan perintah peluncuran yang benar-benar kamu pakai. Data yang tidak diketahui tulis BELUM TAHU, jangan menebak.

   **Seharusnya:** Metadata cukup untuk mengulangi cek. Kolom yang belum diketahui disebutkan di catatan L01.

- **Lulus:** Branch/versi yang diuji jelas dan semua metadata yang diminta sudah dicatat.
- **Gagal:** Perintah atau peluncuran yang dicoba menampilkan error. Catat perintah dan error; jangan menyebutnya kegagalan pembayaran.
- **Belum diuji:** Belum menjalankan perintah atau masih ada metadata yang belum diketahui. Isi hasil parsial di catatan.

Contoh catatan (bukan hasil): L01 — Python 3.12, Windows 11, kamera bawaan. Versi OpenCV belum diketahui; belum diuji lengkap.

## L02 — QR pembayaran, salin link, restart pending

**Untuk apa:** Menguji tombol salin link, transaksi Sandbox, serta kemampuan melanjutkan pesanan yang sama setelah app ditutup.

**Sebelum mulai:** Internet tersedia, akun Midtrans pada Sandbox, aplikasi dijalankan dengan launcher Sandbox. Siapkan ponsel untuk menyimpan tiket. Sesi ini disebut A; itu hanya label catatan.

1. Dari iklan pilih MULAI FOTO, ikuti tutorial, lalu pilih SATU desain dan SATU lembar. Catat nama desain dan nominal. Pilih QRIS SANDBOX lalu LANJUT SANDBOX TANPA PROMO.

   **Seharusnya:** Pilihan/nominal sesuai. Tidak ada diskon game yang diterapkan ke Sandbox. Jika app langsung meminta tiket sesi lama, ikuti petunjuk halaman pemulihan di atas; jangan membuat pengganti.

2. Di SIMPAN TIKET PEMULIHAN, simpan QR ke ponsel secara pribadi, misalnya foto layar yang jelas. Jika scanner QR ponsel menampilkan teks lengkap tiket, simpan teks itu di catatan pribadi. Ini BUKAN QR untuk bayar. Baru klik SUDAH SIMPAN • TAMPILKAN QRIS.

   **Seharusnya:** Tiket tersedia di ponsel untuk L05–L08. Jangan unggah tiket atau teksnya ke chat. Tiket uji berlaku 24 jam; jangan menunda rangkaian cek ke hari lain.

3. Pada MENUNGGU SIMULATOR klik SALIN LINK QRIS. Buka https://simulator.sandbox.midtrans.com/v2/qris/index di browser. Paste ke kolom QRIS URL/URL QR lalu gunakan Scan QR. Periksa nominal dan identitas pesanan yang ditampilkan secara pribadi, tetapi JANGAN konfirmasi pembayaran dulu.

   **Seharusnya:** GUI memberi pesan Link QRIS tersalin. Paste di simulator Midtrans. Simulator membaca URL dan nominal benar. Jika clipboard gagal, coba sekali lagi; fallback URL di terminal hanya workaround, tombol salin belum Lulus.

4. Saat masih belum dibayar, tutup jendela app dengan X. Tunggu PowerShell kembali siap menerima perintah, lalu jalankan launcher Sandbox yang sama lagi. Pertahankan akun/booth/konfigurasi yang sama. Jika diminta bukti pemilik, gunakan tiket A dan VERIFIKASI TIKET.

   **Seharusnya:** App memeriksa/membuka pesanan A yang sama; tidak meminta memilih dan membayar pesanan pengganti. Jika launcher lama belum berhenti, jangan buka instance kedua.

5. Salin link lagi jika tombol tersedia. Baca pesanan di simulator dan bandingkan identitas/nominal dengan sebelum restart. Jangan hanya mengandalkan rupa QR; provider bisa memperbarui gambar. Jika identitas tidak bisa dibandingkan, catat bagian restart BELUM DIUJI.

   **Seharusnya:** Pesanan tetap A, nominal sama, belum terjadi pembayaran kedua. Identitas pesanan cukup disimpan pribadi; laporan chat cukup tulis sama/berubah/tidak dapat dibandingkan.

6. Sekarang pada simulator resmi konfirmasi pembayaran simulasi untuk A. Kembali ke app, tunggu polling sekitar 10 detik atau klik CEK STATUS satu kali. Catat waktu tunggu bila lama.

   **Seharusnya:** App akhirnya menunjukkan PEMBAYARAN UJI TERKONFIRMASI dan LANJUT KE PERSETUJUAN FOTO. Berhasil submit di browser saja belum membuktikan app sudah menerima hasilnya.

- **Lulus:** Tombol salin berhasil, simulator membaca nominal benar, restart mempertahankan pesanan yang sama, dan app menerima pembayaran simulasi.
- **Gagal:** Tombol salin tidak menyalin, URL ditolak, nominal salah, muncul pesanan pengganti, atau pembayaran sudah dikonfirmasi tetapi app tetap error/tertahan. Catat titiknya.
- **Belum diuji:** Akun/internet belum tersedia, tiket belum tersimpan, atau sebagian rangkaian (termasuk restart) belum dicoba. Jangan bayar lagi untuk mengatasi status tidak pasti.

Contoh catatan (bukan hasil): L02 langkah 6 — simulator sudah konfirmasi; app tetap MENUNGGU SIMULATOR selama 90 detik, CEK STATUS sekali tidak berubah.

## L03 — Foto setelah pembayaran simulasi

**Untuk apa:** Memastikan pembayaran tidak langsung memotret dan kemajuan foto bertambah hanya setelah tindakan kamu.

**Sebelum mulai:** L02 sudah sampai PEMBAYARAN UJI TERKONFIRMASI. Gunakan sesi A, bukan transaksi baru.

1. Klik LANJUT KE PERSETUJUAN FOTO. Periksa jumlah desain dan lembar pada persetujuan; cocokkan dengan pilihan awal.

   **Seharusnya:** Satu desain/satu lembar tetap sama. Satu lembar adalah jumlah salinan strip; setiap desain berisi 3 foto, bukan satu foto per lembar.

2. Klik SETUJU & MULAI UJI FOTO. Ketika preview kamera siap, diam 5–10 detik tanpa menekan SIAP dan tanpa menunjukkan gestur telapak ke kamera.

   **Seharusnya:** Kamera boleh menampilkan preview, tetapi hitung mundur dan foto baru tidak berjalan sendiri.

3. Klik SIAP • HITUNG MUNDUR 5 DETIK satu kali. Ubah pose dengan penanda sederhana, misalnya pegang kertas bertulis A1. Tunggu sampai selesai menyimpan.

   **Seharusnya:** Ada hitung mundur, satu foto diambil, lalu kemajuan pindah ke FOTO 2 / 3. Tidak ada rentetan foto dari satu klik.

4. Ambil foto kedua dengan cara yang sama; gunakan penanda A2 agar mudah mengenali foto lama nanti. BERHENTI sebelum mengambil foto ketiga. Catat tampilan FOTO 3 / 3, artinya ada dua foto dan berikutnya giliran foto ketiga.

   **Seharusnya:** Dua foto tersimpan dalam sesi A dan menunggu tindakan berikutnya. Jangan tekan AKHIRI UJI saat sedang menyiapkan uji pemulihan.

- **Lulus:** Persetujuan dan jumlah lembar sesuai; dua capture hanya terjadi setelah tindakan, dengan hitung mundur dan urutan benar.
- **Gagal:** App memotret tanpa tindakan, melewati hitung mundur, menambah capture ganda, atau mengubah desain/jumlah lembar.
- **Belum diuji:** Pembayaran belum terkonfirmasi atau kamera belum bisa digunakan. Catat penyebabnya; jangan menganggap dua foto sudah tersimpan jika belum terlihat kemajuannya.

Contoh catatan (bukan hasil): L03 — dua foto A1/A2 tersimpan; layar FOTO 3 / 3 menunggu SIAP. Satu desain, satu lembar.

## L04 — Minimize dan privasi

**Untuk apa:** Memastikan orang berikutnya tidak melihat foto, QR pembayaran, atau input rahasia dari sesi yang ditinggal.

**Sebelum mulai:** Sesi A punya dua foto dari L03. Kamera sedang menunggu, bukan sedang countdown atau menyimpan.

1. Klik tombol minimize (tanda − pada bingkai Windows), tunggu sekitar 3 detik, lalu klik ikon app di taskbar untuk kembali. Alt+Tab saja berbeda dengan minimize; gunakan tanda − untuk cek ini.

   **Seharusnya:** Tampil SESI TERSIMPAN / TIKET PELANGGAN DIPERLUKAN atau pemeriksaan netral. Foto/strip/QR lama tidak muncul, termasuk saat pertama kembali.

2. Tunggu 5–10 detik tanpa menekan tombol. Jangan arahkan gestur tangan ke kamera.

   **Seharusnya:** Tidak ada hitung mundur, shutter, cetak atau upload otomatis. App tetap memerlukan tiket untuk melanjutkan.

3. Pada kolom tiket ketik TEKS-UJI-JANGAN-VALIDASI. Jangan klik VERIFIKASI TIKET. Minimize lalu restore lagi.

   **Seharusnya:** Input kembali kosong, bukan sekadar masih berisi karakter yang ditutupi bulatan. Foto tetap tidak terbuka. Catat jika tidak dapat memastikan kolom kosong.

- **Lulus:** Setiap restore menyembunyikan data lama, mengosongkan input, dan tidak memulai efek otomatis.
- **Gagal:** Foto/QR lama terlihat walau sesaat, teks lama tetap ada, atau app memotret/mencetak/mengunggah otomatis.
- **Belum diuji:** Minimize/restore atau cek input belum dilakukan. Jika yang dicoba hanya Alt+Tab, catat itu dan ulangi memakai minimize.

Contoh catatan (bukan hasil): L04 langkah 1 — sesaat masih tampak foto A1 setelah restore, lalu baru pindah ke tiket. Ini Gagal privasi.

## L05 — Tiket salah ditolak

**Untuk apa:** Memastikan tiket asal-asalan tidak bisa membuka foto pribadi.

**Sebelum mulai:** Berada di SESI TERSIMPAN dengan kolom Isi tiket pemulihan lengkap setelah L04.

1. Masukkan TIKET-SALAH-UJI-123 (teks contoh ini memang tidak valid). Klik VERIFIKASI TIKET satu kali dan tunggu respons.

   **Seharusnya:** Permintaan ditolak/ada pesan tidak valid. Foto A tidak terlihat, tidak ada kamera resume dan tidak ada pesanan pembayaran baru.

2. Coba kosongkan kolom lalu klik VERIFIKASI TIKET satu kali jika tombol mengizinkan. Jangan mencoba banyak tebakan atau mengubah file agar lolos.

   **Seharusnya:** Input kosong juga tidak membuka foto. Tombol boleh menolak/diabaikan.

3. Catat pesan yang terlihat. Berhenti setelah percobaan ini lalu lanjut ke tiket asli pada L06.

   **Seharusnya:** Kamu tetap di halaman privat. Penolakan tiket salah adalah hasil yang diharapkan, bukan Gagal. Ada pembatasan percobaan; jika diminta menunggu, ikuti dan catat.

- **Lulus:** Tiket salah dan input kosong sama-sama tidak membuka foto/layanan atau membuat pembayaran baru.
- **Gagal:** Tiket salah/kosong membuka foto, memberi izin capture, atau menghasilkan pesanan baru.
- **Belum diuji:** Belum mencoba penolakan, atau halaman tiket belum bisa dicapai karena langkah sebelumnya tertahan.

Contoh catatan (bukan hasil): L05 — tiket salah ditolak, input kosong tidak membuka sesi; foto lama tetap tersembunyi.

## L06 — Tiket asli dan lanjut secara sengaja

**Untuk apa:** Memastikan hanya pemilik tiket asli yang dapat melanjutkan sesi yang sama, tanpa mengulang pembayaran/foto.

**Sebelum mulai:** Punya tiket A yang disimpan pada L02 dan sedang di halaman tiket. L03 menyisakan dua foto.

1. Masukkan TEKS LENGKAP tiket A ke kolom, lalu VERIFIKASI TIKET. Jika hanya punya gambar QR di ponsel, tampilkan gambar itu di depan webcam yang sudah dipakai app lalu pilih SCAN QR TIKET DI KAMERA. Jangan gunakan QR pembayaran, PIN operator, nomor pendek atau nama file gambar.

   **Seharusnya:** App menunjukkan BUKTI PEMILIK TERVERIFIKASI dan tombol PULIHKAN SESI FOTO ASLI. Foto belum tampil hanya karena tiket terverifikasi. Scan gagal karena fokus/silau perlu dicatat terpisah dari validitas tiket.

2. Diam sekitar 5 detik sebelum klik pulihkan. Lalu klik PULIHKAN SESI FOTO ASLI satu kali. Lakukan segera; jika bukti kedaluwarsa, verifikasi tiket lagi.

   **Seharusnya:** Baru setelah tindakan pulihkan, app memeriksa dan membuka kemajuan sesi A. Tidak ada tagihan baru atau capture otomatis.

3. Cocokkan kemajuan: berikutnya FOTO 3 / 3 karena dua foto sudah diambil. Perhatikan nama desain/jumlah lembar bila ditampilkan. Jangan mengklaim nilai yang tidak terlihat; catat BELUM BISA DIBANDINGKAN.

   **Seharusnya:** Kemajuan tidak kembali ke FOTO 1 / 3, tidak meloncat selesai, dan tidak membuat sesi foto pengganti.

4. Biarkan belum mengambil foto ketiga. Lanjut L07 untuk cek tutup/buka pada kemajuan yang sama. Pada review/result di L07 nanti, cocokkan penanda A1/A2 dan kuota retake juga.

   **Seharusnya:** Foto awal dan jatah tetap utuh. Bagian retake/output L06 belum boleh disimpulkan Lulus sebelum dilihat pada L07.

- **Lulus:** Tiket A diterima, foto tetap tersembunyi sebelum pulihkan, sesi yang sama kembali dengan kemajuan benar; setelah L07, A1/A2, desain/lembar dan retake juga cocok.
- **Gagal:** Tiket asli yang benar dan belum kedaluwarsa ditolak tanpa alasan yang bisa dijelaskan, foto terbuka sebelum pulihkan, atau sesi/kemajuan/jatah berubah.
- **Belum diuji:** Tiket asli tidak tersedia/sudah kedaluwarsa, scan belum terbaca, atau bagian pembandingan L07 belum dilakukan. Jangan menebak tiket atau memakai PIN sebagai pengganti.

Contoh catatan (bukan hasil): L06 — tiket diterima; sebelum pulihkan tidak ada foto. FOTO 3 / 3 kembali. Perbandingan A1/A2 menunggu L07.

## L07 — Tutup/buka pada foto sebagian, retake, hasil

**Untuk apa:** Menguji pemulihan pada tiga titik: foto sebagian, sesudah satu retake, dan hasil strip jadi. Tidak perlu Task Manager, cabut listrik, atau merusak file.

**Sebelum mulai:** Sesi A masih menunggu foto ketiga setelah L06. Simpan tiket dan catatan tahap. Jangan tutup saat sedang hitung mundur/menyimpan/membuat strip.

1. Bagian A — saat FOTO 3 / 3 menunggu SIAP, tutup app dengan X. Tunggu terminal kembali ke prompt. Jalankan perintah Sandbox yang sama lagi. Gunakan tiket A → VERIFIKASI TIKET → PULIHKAN SESI FOTO ASLI.

   **Seharusnya:** Sebelum bukti: tidak ada foto lama. Sesudah pulihkan: tetap menunggu foto ketiga, tanpa countdown/capture otomatis. Restart launcher memberi PIN operator baru; tiket A tetap tiket yang sama.

2. Ambil foto ketiga dengan penanda A3 melalui tombol SIAP. Di halaman review, cocokkan A1/A2/A3. Klik RETAKE pada satu foto, misalnya foto kedua; ambil ulang melalui countdown dengan penanda A2-R.

   **Seharusnya:** Hanya foto yang dipilih berubah, dua lainnya tetap. Satu retake per desain digunakan; tombol RETAKE berikutnya tidak memberi jatah baru.

3. Bagian B — ketika kembali ke review dan retake selesai tersimpan, tutup/buka app seperti Bagian A. Verifikasi tiket A lalu pulihkan.

   **Seharusnya:** Foto A2-R tetap menggantikan pilihan kedua, A1/A3 tetap, retake tidak tersedia lagi. Tidak perlu mengulang retake atau membayar.

4. Klik PAKAI FOTO INI • BUAT STRIP. Tunggu hasil strip selesai. Cocokkan tiga pose/penanda, desain dan jumlah lembar dengan catatan awal. Simpan catatan hasil secara pribadi; jangan kirim wajah/foto asli ke chat.

   **Seharusnya:** Strip sesuai pilihan terakhir. Di Sandbox cetak belum diaktifkan dan Drive OFF; tidak adanya kertas atau QR download bukan Gagal pengujian ini.

5. Bagian C — saat hasil stabil, JANGAN klik SELESAI • KEMBALI IKLAN dulu. Tutup/buka app lagi, gunakan tiket A dan tindakan pulihkan. Cocokkan strip/pose yang sama.

   **Seharusnya:** Hasil lama kembali setelah bukti, tanpa memotret, mengulang retake, mencetak atau mengunggah. Secara visual hasil sama; kesamaan hash/file adalah bukti otomatis terpisah, bukan sesuatu yang harus kamu hitung.

6. Catat A/B/C masing-masing: berhasil, masalah, atau belum dicoba. Biarkan sesi A untuk L08 jika ingin menguji pelepasan. Kalau berhenti di sini, hak/foto tetap tersimpan; jangan menghapus data untuk kembali ke iklan.

   **Seharusnya:** Satu hasil Lulus L07 mencakup ketiga titik. Jika hanya A berhasil, hasil keseluruhan masih Belum diuji dengan catatan A berhasil.

- **Lulus:** Ketiga titik A/B/C berhasil; foto terpilih, retake, kemajuan dan strip tetap benar, tanpa efek otomatis.
- **Gagal:** Salah satu titik yang benar-benar dicoba kehilangan/mengubah foto, mengembalikan jatah retake, membuka foto tanpa bukti atau memulai tindakan otomatis.
- **Belum diuji:** Baru sebagian titik dicoba atau langkah sebelumnya menghalangi. Catat A/B/C agar bagian yang sudah berhasil tidak perlu diulang tanpa alasan.

Contoh catatan (bukan hasil): L07 — A berhasil, B berhasil (A2-R tetap dan retake habis), C belum dicoba; hasil keseluruhan Belum diuji.

## L08 — Pelepasan, pengunjung berikutnya, kembali ke sesi asli

**Untuk apa:** Menguji pemilik tunggal (kamu sendiri) melepas pemakaian booth dengan PIN lokal, tanpa menghapus hak sesi A, lalu membuka kunjungan B dan kembali ke A.

**Sebelum mulai:** Bagian lanjutan, boleh ditunda. Sesi A sudah dibayar simulasi, tiket A tersedia, app tidak sibuk. Kamu memegang PowerShell launcher terbaru. Tidak butuh orang/operator tambahan.

1. Minimize/restore untuk kembali ke halaman tiket, lalu klik BANTUAN OPERATOR. Di terminal cari baris Local Sandbox operator PIN (keep private). Gunakan delapan digit dari PELUNCURAN TERBARU. Jangan salin baris itu ke checklist/chat.

   **Seharusnya:** Muncul OPERATOR SANDBOX. PIN bukan tiket pelanggan dan bukan Server Key. Jika PIN tidak ada, berhenti/catat; jangan menebak, mengubah konfigurasi atau memakai PIN lama.

2. Masukkan PIN lalu klik PERIKSA STATUS OPERATOR. Tunggu hasil. Baca Pembayaran, Layanan, Kewajiban dan Masalah. Pemeriksaan ini hanya membaca status, bukan mengembalikan uang atau mengizinkan melihat foto.

   **Seharusnya:** Status dapat diperiksa tanpa menampilkan foto A. Kolom PIN dikosongkan setelah dikirim; ini memang normal. Bila koneksi/provider bermasalah, catat pesan dan jangan paksa pelepasan.

3. Masukkan PIN LAGI, kemudian klik ISOLASI SESI LAMA satu kali. Tunggu hingga ada pesan Sesi lokal sudah diisolasi dan tombol berubah menjadi LEPAS BOOTH • HAK TETAP DISIMPAN.

   **Seharusnya:** App menonaktifkan pemakaian sesi lama untuk melepas booth. Halaman pelanggan baru belum boleh dianggap bebas hanya karena isolasi dimulai. Jika tombol nonaktif atau isolasi ditolak, catat keadaan, jangan bypass.

4. Masukkan PIN LAGI lalu klik LEPAS BOOTH • HAK TETAP DISIMPAN. Tunggu konfirmasi/halaman iklan. ACK berarti backend sudah menerima bukti pelepasan; arsip berarti ikatan kunjungan lama disimpan. Kamu tidak perlu mengirim ACK manual atau mengedit file.

   **Seharusnya:** Booth kembali siap kunjungan baru setelah pelepasan terkonfirmasi, tanpa mengklaim foto sudah dicetak/refund atau menghapus hak A. Jika gagal/tertahan, jangan mulai pesanan pengganti.

5. Sebagai pengunjung B, klik MULAI FOTO dan pilih desain lain agar mudah dibedakan. Buat pesanan uji baru melalui alur normal dan simpan tiket B sendiri. JANGAN konfirmasi pembayaran B; cukup sampai QR menunggu simulator.

   **Seharusnya:** Tidak ada foto/strip/input tiket A yang muncul di kunjungan B. Pesanan B memang kunjungan baru setelah pelepasan, bukan pembayaran ulang untuk memulihkan A.

6. Saat B aktif, periksa apakah ada cara normal di layar untuk membuka tiket A. Jika tombol lookup lama tidak tersedia, catat itu sebagai penjagaan akses. Jangan memakai endpoint/kode, jangan menyuntik tiket lewat file dan jangan meninggalkan B untuk memaksa A.

   **Seharusnya:** A tidak mengambil alih kunjungan B. Bila jalur untuk submit tiket A memang tidak ada, kamu hanya membuktikan penjagaan GUI; pengujian penolakan backend tetap bukti otomatis terpisah.

7. Karena B masih BELUM dibayar, pilih BATALKAN PESANAN UJI pada pesanan B. Tunggu PESANAN UJI DITUTUP lalu SELESAI / KEMBALI IKLAN. Jika B ternyata sudah PAID atau pembatalan tidak pasti, berhenti dan catat; jangan menganggap booth bebas.

   **Seharusnya:** Baru setelah B ditutup terkonfirmasi, booth bebas. Tidak ada pembatalan/refund terhadap A.

8. Dari iklan klik PUNYA TIKET PEMULIHAN. Gunakan tiket A → VERIFIKASI TIKET → PULIHKAN SESI FOTO ASLI.

   **Seharusnya:** Hanya sesi A/strip A yang kembali, bukan B, tanpa pembayaran ulang atau capture otomatis. Kamu boleh mengakhiri A melalui tombol selesai yang tersedia setelah seluruh cek selesai.

- **Lulus:** Pemeriksaan/isolasikan/lepas selesai, B tidak melihat A dan tidak diambil alih lewat GUI, B ditutup terkonfirmasi, lalu tiket A mengembalikan sesi A saat booth bebas. Ini hasil GUI Sandbox saja.
- **Gagal:** PIN yang benar gagal tanpa alasan jelas, booth memberi kunjungan baru sebelum konfirmasi, hak A hilang, foto bocor ke B, atau tiket A membuka sesi B.
- **Belum diuji:** Belum ingin menjalankan bagian lanjutan, tidak memegang PIN terbaru/tiket A, tombol tertahan atau tahap B/return belum bisa dicoba. Catat tahap terakhir; jangan menjalankan trik untuk meloloskan.

Contoh catatan (bukan hasil): L08 langkah 3 — PIN diterima saat inspect, tetapi ISOLASI nonaktif. Layar tertulis layanan tertunda. B dan return belum diuji.

## L09 — Layout, input, respons, kamera

**Untuk apa:** Memastikan kontrol terbaca/terjangkau dan perangkat tetap bisa digunakan pada ukuran layar laptop. Ukuran browser checklist berbeda dengan ukuran jendela app.

**Sebelum mulai:** Lakukan cek layout pada halaman yang dijumpai di L02–L08. Cek cabut kamera hanya jika kamera USB milikmu dan booth bebas/tidak ada capture atau penyimpanan berjalan.

1. Layout — lihat halaman template, tiket, QR pembayaran, persetujuan, kamera, review, hasil dan operator. Ubah ukuran JENDELA APP dengan menyeret tepinya. Target pengujian adalah area app 800×1280 dan 452×900, jika layar memungkinkan.

   **Seharusnya:** Teks/tombol penting terlihat, tidak saling menimpa dan tetap bisa diklik/di-scroll. Bila hanya ukuran perkiraan, tulis perkiraan; jangan mengklaim ukuran tepat tanpa pengukuran. Laptop 1080p bisa tidak memuat tinggi 1280: tandai target itu belum diuji.

2. Input — klik kolom tiket/PIN, ketik, gunakan Backspace lalu paste (Ctrl+V) pada kolom tiket. Pakai input uji yang tidak dikirim jika belum waktunya klaim. Pada layar sentuh, coba sentuhan juga; bila tidak punya touchscreen tulis tidak tersedia.

   **Seharusnya:** Fokus/input berfungsi, teks rahasia tetap dimasking, pilihan tidak berubah karena sentuhan yang tidak dimaksud. Jangan merekam/melaporkan isi rahasia.

3. Klik cepat — gunakan CEK STATUS / PERIKSA STATUS dengan dua klik berdekatan sekali. Amati apakah tombol sementara dinonaktifkan lalu aktif kembali. Jangan lakukan spam pada bayar, SIAP, RETAKE atau LEPAS BOOTH.

   **Seharusnya:** App tetap merespons dan tidak membuat pesanan/capture baru. Tombol nonaktif selama proses berlangsung boleh normal; catat jika lama beserta durasi yang teramati.

4. Kamera USB — setelah sesi aman selesai/booth bebas, cabut kamera lalu pasang lagi di port yang sama, tunggu sekitar 10 detik. Buka langkah pemeriksaan/persiapan kamera melalui alur normal. Jangan sengaja memulai pembayaran baru hanya untuk melampaui kamera yang belum siap.

   **Seharusnya:** Preview/persiapan kamera kembali berfungsi, atau app memberi pesan yang jelas dan tidak menjual layanan ketika kamera belum siap. Catat jika harus restart; jangan otomatis menyebut reconnect Lulus hanya karena restart memulihkan kamera. Kamera bawaan tidak perlu dibongkar/dinonaktifkan.

5. Isi catatan dengan ukuran yang benar-benar dicoba, halaman bermasalah, mouse/touch/keyboard, dan hasil reconnect. Jika target ukuran/reconnect belum dicoba, tulis alasan dan hasil bagian lain.

   **Seharusnya:** Bagian yang tak tersedia tidak berubah menjadi Lulus. Cek sentuh tidak berlaku bila perangkat memang tanpa touchscreen; target ukuran atau reconnect yang belum teruji tetap dicatat sebagai keterbatasan.

- **Lulus:** Seluruh pemeriksaan yang berlaku sudah dicoba dan berfungsi, kedua ukuran target benar-benar diverifikasi, serta reconnect kamera yang diminta berhasil. Sebutkan touch tidak berlaku bila laptop tanpa touchscreen.
- **Gagal:** Tombol terpotong/tidak dapat dijangkau, input salah, app hang, klik ganda menimbulkan efek ganda, atau reconnect yang dicoba gagal. Catat ukuran/durasi tepatnya.
- **Belum diuji:** Target ukuran tidak muat/tidak terukur, kamera bawaan tidak bisa diuji cabut-pasang, atau hanya sebagian kontrol dicoba. Hasil parsial tetap berguna; keseluruhan belum diuji lengkap.

Contoh catatan (bukan hasil): L09 — 452×900 perkiraan: semua tombol terlihat. 800×1280 tidak muat layar. Mouse/keyboard OK; tanpa touch; kamera bawaan, reconnect belum diuji.

## Istilah dan batas yang tidak perlu kamu simulasikan

Pending = menunggu pembayaran; settlement = pembayaran selesai di simulator;
app tetap perlu memverifikasinya. Retake = ambil ulang satu foto, satu kesempatan
per desain. Lembar = salinan strip, tidak menambah sesi capture.

Isolasi = menghentikan pemakaian sesi lama dengan aman; ACK = konfirmasi backend
menerima pelepasan; arsip = menyimpan ikatan kunjungan lama. GUI mengurusnya.
Melepas booth tidak berarti refund, hasil cetak sudah diterima, atau kewajiban hilang.

Fixture/mock = uji otomatis memakai perangkat/data tiruan. Gangguan sender
SENDING/UNCERTAIN, lost ACK, kegagalan arsip, fence dan kesamaan hash sudah punya
bukti otomatis tersendiri; tidak diminta direkayasa pengguna lewat file/DB/printer.
L08 hanya bukti GUI Sandbox, bukan bukti host paid-print komersial.

Source fixture ca7827c: **1229 run / 1225 PASS / 4 optional SKIP / 0 FAIL/ERROR**;
CI40985975287 ketiga job SUCCESS. Ini terpisah dari SHA/hasil laptop.
Paid-print host komersial belum dipasang. PAY-22 dan WEB-01–08 tetap BLOCKED;
Windows/Ubuntu mini-PC, merchant, kertas, ponsel/Drive/deletion, privasi operasional,
support/kompensasi dan release punya gate sendiri. Form ini tidak menyatakan
seluruh UX-07/AR-13 selesai dan tidak mengaktifkan produksi atau transport Sandbox.

## Kirim hasil

Isi hasil dan catatan tiap item → **Salin Hasil untuk Chat** → paste dan kirim.
Jika clipboard diblokir: **Tampilkan Prompt** lalu Ctrl+A/Ctrl+C pada kotak prompt,
atau **Unduh Hasil .txt**. Boleh kirim sebagian. Contoh format masalah:

```text
L07 bagian B, setelah buka app lagi:
Harapan: A2-R tetap dan retake habis.
Terlihat: A2 lama kembali, tombol RETAKE aktif.
Terjadi: 1 dari 1 percobaan.
Bagian C belum dicoba karena B bermasalah.
```

Jangan sertakan Server Key, PIN, tiket/QR rahasia, token, database atau foto pribadi.
Jika perlu gambar, potong/samarkan bagian rahasia di salinan screenshot, jangan
ubah foto asli. Cukup tulis identitas pesanan sama/berubah, bukan payload/linknya.
