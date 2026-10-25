# Prompt melanjutkan Meong Photobooth GUI v2

Diperbarui **25 Oktober 2026**. Gunakan branch yang sudah ada; jangan memulai
ulang dari master. [Protocol](DEVELOPMENT_PROTOCOL.md) dan root [AGENTS](../AGENTS.md)
mengatur reuse, scope, tes, push dan bukti.

## Copy/paste untuk melanjutkan

> Repository: pratikto/PhotoBooth.
> Branch wajib: **feature/portrait-kiosk-v2-next**.
> GUI v2 adalah pusat pengembangan/calon branch utama, tetapi GitHub default
> masih master. Jangan membuat branch baru, mengubah master/default/rename,
> merge, release atau deploy tanpa instruksi operasi tersebut.
>
> Tugas dan scope yang saya minta: **[ISI TUGAS]**.
> Batas/perangkat/hasil yang diharapkan: **[ISI JIKA ADA]**.
>
> Baca README.md → docs/README.md → portrait-kiosk-v2.md → FEATURE_STATUS.md →
> DEVELOPMENT_HANDOVER.md → bug_tracker.md → next_step.md → DECISIONS.md dan
> test_checklist.md. Source fungsional baseline terakhir 9433010, bukti 0dc6555;
> cek HEAD remote terkini dahulu, jangan mengandalkan angka ini jika sudah maju.
>
> Pertahankan P3 foto, original game renderer, checkout MOCK/Sandbox dan native
> tipografi yang sudah diterima. Jangan mengulang implementasi yang sudah ada.
> Periksa docs/gui-v2-branch-audit.md dan branch referensi terkait read-only,
> refresh source SHA, reuse kode/GUI/renderer/aset yang bekerja, lalu catat adapter
> yang memang diperlukan. Jangan mengintegrasikan fitur kandidat hanya karena
> dokumentasi branch-nya ada.
>
> Kerjakan seluruh scope yang sudah diotorisasi tanpa approval per perubahan
> kecil. Beri update singkat, lakukan tahap yang reviewable, jalankan tes relevan,
> perbaiki failure, commit/push ke branch wajib lalu verifikasi remote HEAD.
> Untuk source akhir jalankan satu regresi lengkap; jangan menghabiskan Actions
> credits untuk mengulang run hijau pada perubahan dokumen. Docs-only memakai
> validasi link/referensi/hash dan skip CI, bukan rerun GUI.
>
> Perubahan GUI direview pada 800×1280 dan 452×900; sertakan ukuran kecil/lebar
> jika relevan. Jaga speed/spacing game seragam dan Meong di kiri, callback lama
> mati, audio satu owner, foto original tidak dicerminkan, serta satu retake/desain.
>
> Payment Sandbox harus server quote/grant/ACK; jangan pakai PAID/skor/amount dari
> GUI sebagai authority. Promo game QRIS belum punya kontrak tepercaya; default
> produksi/POS/scanner off. Jangan hapus journal/data atau replay charge/foto/
> print untuk melewati status tidak pasti. Key hanya diinput lokal, tidak ke chat.
>
> Bedakan source PASS, laporan owner, preflight, merchant dan perangkat fisik.
> Owner preflight HEAD 0dc6555 ready belum meluluskan P5. Isi metadata kosong
> tetap unknown; jangan menganggap checklist kosong lulus atau menjalankan ulang
> 20 putaran lama tanpa alasan. Gate 20 Sandbox baru mengikuti form P5.
>
> Update dokumen yang faktanya berubah (status/bug/decision/QA/handover/changelog)
> dan laporkan perubahan, tes, commit/remote, bukti, bug/gate serta langkah aman
> berikutnya. Hentikan bagian yang tidak dapat diselesaikan aman di dalam scope;
> jangan menyamarkan blocker provider/hardware sebagai PASS.

## Referensi cepat

- [Status dan checkpoint](DEVELOPMENT_HANDOVER.md).
- [Sandbox/P5 commands dan evidence](qa/portrait-v2-p5/README.md).
- [26-item Windows form dengan Submit](qa/portrait-v2-p5/windows-checklist.html).
- [Audit semua branch](gui-v2-branch-audit.md).
- [Branch utama berikutnya: gate dan operasi yang berbeda](gui-v2-promotion-plan.md).

Persetujuan terdahulu tetap berlaku pada scope yang dinyatakan. Tugas dokumen
ini sendiri tidak memberi izin fitur baru, produksi, deployment atau merge.
