# Dokumentasi Meong Photobooth — GUI v2

Diperbarui **25 Oktober 2026 (Asia/Jakarta)**. Pusat pengembangan GUI v2 adalah
**feature/portrait-kiosk-v2-next**, calon branch utama berikutnya menurut owner.
Default GitHub yang terverifikasi masih **master**. Gunakan launcher khusus v2;
`python main.py` tetap v1. [Rencana transisi](gui-v2-promotion-plan.md).

## Mulai dari kebutuhanmu

| Kebutuhan | Dokumen kanonis |
| --- | --- |
| Instalasi, launcher, pilihan mode | [README repository](../README.md) |
| Roadmap P0–P5, alur dan status milestone | [Spesifikasi GUI v2](portrait-kiosk-v2.md) |
| Modul, worker, audio, payment/photo lifecycle | [Desain teknis](portrait-kiosk-v2-technical-design.md) · [peta arsitektur](ARCHITECTURE.md) |
| Mockup dan koreksi tampilan terbaru | [Spesifikasi visual](portrait-kiosk-v2-visual-spec.md) · [asal aset](assets/portrait-v2/README.md) |
| Apa yang sudah aktif vs rencana | [FEATURE_STATUS.md](FEATURE_STATUS.md) |
| Keputusan produk dan batas persetujuan | [DECISIONS.md](DECISIONS.md) |
| Bug dan prioritas operasional | [bug_tracker.md](bug_tracker.md) |
| Tugas aman berikutnya / backlog | [next_step.md](next_step.md) |
| Lanjut development tanpa memulai ulang | [DEVELOPMENT_HANDOVER.md](DEVELOPMENT_HANDOVER.md) · [prompt](DEVELOPMENT_PROMPT.md) |
| Aturan kerja/reuse/test/push | [AGENTS.md](../AGENTS.md) · [DEVELOPMENT_PROTOCOL.md](DEVELOPMENT_PROTOCOL.md) |
| Hasil tes dan acceptance | [test_checklist.md](test_checklist.md) · [indeks QA](qa/README.md) |
| Riwayat perubahan | [CHANGELOG.md](CHANGELOG.md) |
| Branch referensi dan rencana branch utama | [Audit 19 branch](gui-v2-branch-audit.md) · [promotion plan](gui-v2-promotion-plan.md) |

## Paket operasional terbaru

- **[P5 Windows acceptance](qa/portrait-v2-p5/README.md)**: perintah launch,
  metadata preflight, bukti 688 full PASS, CI/source/screenshot dan rollback.
- **[Form 26 item dengan Submit](qa/portrait-v2-p5/windows-checklist.html)**:
  impor `windows-readiness.json`; kosong berarti gagal/belum diuji. Import tidak
  mencentang tes dan laporan 20 putaran lama tidak meluluskan integrasi baru.
- **[P4b QRIS Sandbox](qa/portrait-v2-sandbox/README.md)**: kredensial lokal,
  simulator, harga tanpa promo, izin backend sekali pakai dan recovery.
- **[P3 foto/printer/Drive](qa/portrait-v2-p3/README.md)** dan
  [preview/button acceptance](qa/portrait-v2-preview-redraw/README.md): bukti
  tahap terdahulu; default lokal, bukan launcher Sandbox atau sertifikasi P5.
- **[Reuse game asli](qa/portrait-v2-meong-reuse/README.md)** dan
  [tipografi terbaru](qa/portrait-v2-readable-type/README.md): jejak visual/QA.

Preflight Windows owner pada HEAD **0dc6555** menghasilkan
**READY_FOR_MANUAL_TEST**. Source fungsional **9433010** diuji 688 PASS / nol skip;
[CI 40109206417](https://github.com/pratikto/PhotoBooth/actions/runs/40109206417)
tiga job SUCCESS, 109 PNG. Uji merchant/provider/perangkat/retensi/privasi dan
rilis tetap terpisah. **P5 siap diuji, belum tersertifikasi komersial.**

## Cara membaca referensi lama

Dokumen QA bertanggal dan tag `v1.0.0` mempertahankan fakta pada SHA aslinya.
Status prototype P0–P2, tarif quantity/session lama, placeholder game, atau klaim
“tidak ada kamera/QRIS sama sekali” tidak mewakili GUI v2 sekarang. Jangan
menerapkan ulang instruksi branch/merge/fitur dari snapshot referensi.

Panduan [advertising-and-qris.md](advertising-and-qris.md),
[photo-retention.md](photo-retention.md), [dither-tuning-lab.md](dither-tuning-lab.md)
dan [rilis v1](releases/v1.0.0.md) tetap berguna sesuai konteks v1/backendnya;
launcher, status dan kontrol v2 mengikuti dokumen kanonis di atas. Panduan
lab dithering yang lebih baru tersedia di branch referensi, bukan otomatis di v2.

[Indeks sebelum konsolidasi](https://github.com/pratikto/PhotoBooth/blob/0dc6555d299cdab19d952e92df2ae660cdc4676d/docs/README.md)
disimpan di riwayat Git. Dokumentasi ini tidak mengubah source aplikasi, default
branch, master, deployment, produksi atau persetujuan release.
