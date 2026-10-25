# GUI v2 sebagai calon branch utama

Keputusan arah owner, **25 Oktober 2026**: GUI v2 akan menjadi branch utama.
Dokumen ini menyiapkan transisi; bukan bukti bahwa transisi GitHub sudah terjadi.

| Peran | Keadaan saat audit |
| --- | --- |
| Pusat pengembangan GUI v2 dan target commit saat ini | `feature/portrait-kiosk-v2-next` |
| Default branch GitHub saat ini | `master` · `27f3801` |
| Baseline source v1 yang immutable | tag `v1.0.0` · `07ce51d` |
| Source fungsional v2 terakhir diuji | `9433010` · bukti dokumentasi `0dc6555` |
| Calon produk/branch utama berikutnya | GUI v2, setelah gate dan instruksi operasi GitHub |

## Gate sebelum pemindahan

| Gate | Bukti / status |
| --- | --- |
| Source dan reuse lintas branch terdokumentasi | [Audit 19 branch](gui-v2-branch-audit.md); game/QRIS direuse, eksperimen lain dipetakan |
| Regresi source fungsional | 688 PASS / nol skip; tiga job CI SUCCESS, 109 PNG; [P5](qa/portrait-v2-p5/README.md) |
| Windows metadata | Owner menjalankan preflight pada HEAD `0dc6555`: READY_FOR_MANUAL_TEST; bukan acceptance perangkat/provider |
| Windows end-to-end/touch/audio/camera/resize | Laporan lama diterima sesuai batasnya; [form P5](qa/portrait-v2-p5/windows-checklist.html) dan uji integrasi baru belum diserahkan |
| Merchant Sandbox / status / recovery | Source tersambung, uji merchant nyata belum ada. Sandbox keys tersedia lewat dashboard Sandbox; persetujuan produksi adalah proses terpisah |
| Promo game yang dipercaya backend QRIS | Belum ada kontrak; jangan memberi nilai diskon dari GUI/game lokal |
| Printer fisik dan uncertain recovery | Opt-in/operator; hasil spooler bukan bukti jumlah kertas |
| Drive download, privasi dan retensi 30 hari | BUG-009 OPEN; bukti penghapusan cloud belum ada |
| Default branch / proteksi / PR / release operation | Belum dijalankan atau diberi instruksi operasi terpisah |

Tidak semua eksperimen perlu dimasukkan sebelum pemindahan. Device Health, AI,
WhatsApp dan lab dithering terbaru tetap kandidat terpisah dengan persetujuan,
kecocokan adapter dan bukti regresi masing-masing. Cakupan/kelonggaran gate saat
pemindahan harus dinyatakan owner secara eksplisit; jangan menyamakan menjadikan
branch default dengan sertifikasi produksi.

## Operasi saat owner meminta pemindahan

1. Konfirmasi keadaan repo dan source final yang diuji; simpan ref/tag v1 dan
   checkpoint v2 tanpa mengubah jurnal transaksi atau data pelanggan.
2. Tentukan operasi yang diminta: menjadikan branch v2 yang ada sebagai default,
   rename, atau PR/merge. Ketiganya berbeda; audit ini tidak memilihnya sendiri.
3. Tinjau branch protection/check wajib, PR base yang masih terbuka, CI branch
   filters, dokumentasi clone/update dan kebijakan launcher. Mengubah default
   GitHub tidak otomatis mengubah `python main.py`, yang masih menjalankan v1.
4. Jalankan hanya operasi yang diinstruksikan, verifikasi remote/default/settings,
   lalu perbarui dokumentasi, rollback dan release notes sesuai bukti.
5. Pengaktifan QRIS produksi, scanner/POS, promo nyata, deployment dan release
   membutuhkan cakupan tersendiri. Jangan mengaktifkannya karena branch pindah.

Dokumentasi sekarang tetap memakai branch v2 yang ada, launcher khusus dan
checkpoint terverifikasi. Tidak dibuat branch pengembangan baru, tidak ada merge,
rename/default-branch change, atau perubahan pada master/branch referensi.
