# FEAT-022 — GUI v2: arsitektur dan kontrak integrasi

Snapshot dokumentasi **25 Oktober 2026** pada branch
`feature/portrait-kiosk-v2-next`; source operator **ea394e8** (780 full PASS/CI SUCCESS), baseline P5 **9433010**.
[Ruang lingkup/roadmap](portrait-kiosk-v2.md) · [audit reuse](gui-v2-branch-audit.md).

## 1. Prinsip kelanjutan

GUI v2 sudah mengintegrasikan P3/P4; tidak lagi sebatas prototype galeri atau
placeholder game. Gunakan adapter kecil dan implementasi existing yang bekerja.
Default GitHub masih master, launcher default main.py masih v1. Arah menuju GUI v2
sebagai branch utama mengikuti [promotion plan](gui-v2-promotion-plan.md), tanpa
mengotorisasi operasi repository atau produksi melalui dokumen ini.

## 2. Inventaris source yang aktif

| Tanggung jawab | Modul | Kontrak |
| --- | --- | --- |
| Native window dan page lifecycle | `kiosk_v2/app.py`, `flow.py`, `viewport.py` | Dedicated launcher, revision guard untuk aksi halaman lama, browse timeout hanya halaman aman |
| Tema/caption/header | `theme.py`, `button_art.py`, `branding.py`, `brand_flight.py` | Frame original game, caption native tanpa ikon wajib; animasi/pause/dispose dibatasi header |
| Galeri dan warmup | `gallery.py`, `previews.py` | 12 strip asli, CPU preview di worker, texture preload bertahap, swipe/drag dan animasi tidak menumpuk |
| Audio | `audio.py`, `mixer.py`, `game_music.py`, `shutter.py` | Owner v2 tunggal, tidak berbagi lifecycle AudioManager v1; musik gambar/video/game dan SFX terpisah |
| Kamera/sensor/live preview | `devices.py`, `sensors.py`, `live_preview.py` | Async camera/frame mailbox, off-GUI preview/detector, mirror hanya display, palm memakai countdown SIAP yang sama |
| Foto/capture/review/result | `photo_views.py`, `photos.py`, `photo_drive.py` | PhotoJobs single-flight, TransactionStore/PhotoSession/catalog/printer/Drive existing; original tidak ditimpa mirror/retake |
| Game | `game_scene.py`, `game_layout.py`, `game_views.py`, `demo_game.py` | Original MeongFlyStage/Flow/renderer/emitter direuse; durable one-use DEMO ledger, bukan POS authority |
| Promo/checkout MOCK | `game_offer.py`, `mock_checkout.py`, `checkout_views.py` | SQLite menghitung harga dan memvalidasi DEMO attempt; satu diskon/admission, QR nonpayable |
| Sandbox host | `sandbox_checkout.py`, `sandbox_views.py` | KioskCheckout/QrisKioskClient existing; GameJobs single-flight, no GUI merchant key, durable photo handoff |
| Payment service | `checkout_backend.py`, `checkout_store.py`, `payment_quote.py`, `qris_api.py`, `booth_auth.py` | Server quote, auth booth, idempotency, grant/service state, rekonsiliasi independen |
| Provider/QR/network | `midtrans_sandbox.py`, `midtrans_verify.py`, `qris_evidence.py`, `qris_images.py`, `qris_kiosk_client.py` | Sandbox-only, verifikasi order/merchant/amount/currency/ref, bounded I/O, allowlist QR, tanpa redirect |
| Durable visit | `qris_session.py` | Atomic journal + lease per proses; context mode/endpoint/booth, restart hold, no replay |
| Diagnosis/readiness | `diagnostics.py`, `performance.py`, `readiness.py` | Log lokal/HEAD, pengukuran preview; inventory read-only tanpa probe camera/printer/provider dan tanpa secret |

Path tanpa prefix pada baris GUI berada di `photobooth/kiosk_v2/`; shared services
berada di `photobooth/`. Lihat [peta repository](ARCHITECTURE.md).

## 3. Alur foto dan orientasi

Default/local membutuhkan persetujuan UJI FOTO, tidak membuat pembayaran.
Satu desain terpilih menghasilkan satu PhotoSession, tiga original dan maksimum
satu retake. Jumlah lembar 0–9 bukan penambahan sesi. JPEG asli tetap resolusi
capture; preview dibatasi ukurannya dan mirror dilakukan pada texture display.
Foto yang diganti retake tetap disimpan sesuai manifest, bukan menimpa original.

`PhotoJobs` mencegah antrian tap ganda. Countdown dibatalkan saat minimize,
pergantian halaman atau kamera hilang. Tidak ada auto-capture saat aplikasi pulih.
Print adalah aksi operator/opt-in; hasil tidak pasti membutuhkan pemeriksaan,
bukan retry otomatis. Drive membutuhkan konfigurasi dan retention guard; QR hasil
hanya tersedia jika folder yang benar benar-benar tersedia.

Default data P3: `data/kiosk-v2-p3/`. Game/MOCK: `data/kiosk-v2-p4/`.
Merchant Sandbox: `data/kiosk-v2-sandbox/<merchant>/<booth>/`, journal `visit.json`,
backend `orders.sqlite`, foto di subtree `photo-tests/`. Isolasi ini tidak boleh
dihilangkan dengan mengganti ke journal/folder v1.

## 4. Harga dan otoritas pembayaran

`catalog`/`workflow` menghitung Rp5.000 per desain/sesi + Rp5.000 per lembar.
Kemenangan DEMO menawarkan Rp2.500 sekali/order pada simulasi lokal/MOCK.
**Skor, amount dan diskon GUI tidak menjadi bukti pembayaran atau promo QRIS.**
Service QRIS referensi hanya menerima cart/quantities dan menghitung harga server.
Belum ada trusted merchant promo API; native Sandbox menampilkan konfirmasi
**harga penuh tanpa promo** sebelum order dibuat, tidak mengubah nominal diam-diam.

`tools/run_portrait_v2_sandbox.py` memanggil helper merchant trial existing dengan
entry/environment khusus v2. Backend menerima Server Key Sandbox; GUI hanya token
booth. Inherited merchant credentials di GUI atau mode MOCK/Sandbox bersamaan
fail closed. Backend loopback; tidak ada public webhook/tunnel/deployment.
Readiness backend tidak membuktikan kredensial merchant atau settlement.

## 5. Durable Sandbox → foto

`CREATING → WAITING → RESERVED → STARTING → STARTED → COMPLETING → COMPLETED`.
Pembatalan melalui `CANCELLING → CANCELLED`; ketidakpastian dapat berakhir di
`RECOVERY`. Atomic journal disimpan **sebelum** request charge pertama.

- Retry memakai checkout key/order yang sama; paid/cancel race direkonsiliasi
  backend, bukan diputuskan UI. Satu grant stabil tidak boleh menciptakan sesi baru.
- RESERVED → persetujuan → durable STARTING → satu transaksi foto → bind txid →
  ACK STARTED. Countdown/capture tidak tersedia sebelum ACK untuk txid yang sama.
- Seluruh sesi desain selesai → request/ACK COMPLETED. Abort atau restart setelah
  capture mungkin berjalan memerlukan operator recovery; tidak replay foto/cetak.
- Pending/unknown/paid tidak bisa ditinggal lewat browse timeout atau ganti cart.
  Recovery sengaja tidak memiliki tombol reset paid-order/refund otomatis.
- Stop menunggu worker berakhir sebelum melepas lease; callback halaman yang
  sudah pensiun tidak mendapat kesempatan menjalankan aksi baru.

[Runbook dan kegagalan/recovery](qa/portrait-v2-sandbox/README.md).

## 6. Game, resize, animasi dan audio

26 file original Meong Fly direferensikan pada SHA `672e3f7`; service QRIS pada
`3cc8a8e`. [Hash/provenance game](qa/portrait-v2-meong-reuse/README.md) dan
[QRIS](qa/portrait-v2-sandbox/reused-source.json). Pengecualian yang terdokumentasi:
adapter layout/input v2 dan injectable launcher entry/environment/notice;
legacy UI v1 tidak ditumpangkan ke window v2.

World game dicenter dengan skala konsisten untuk seluruh lintasan. Jangan memakai
skala nonlinear posisi asteroid jauh/dekat atau right-align spawn yang mendorong
Meong ke kanan (BUG-015/016). Resize tidak mengganti fisika, spawn spacing atau
reset skor/sesi; minimize memerlukan resume game manual. Header flight punya
batas/pause/dispose sendiri; bukan mengubah physics engine game.

Iklan video memiliki audio sendiri; iklan gambar memakai BGM GUI. Tutorial,
galeri, foto dan checkout memakai satu loop GUI; game memakai loop berbeda.
Setiap enabled action mengeluarkan satu cue; tidak ada sound owner v1 paralel.

## Operator health seam / FEAT-008

Actual `HealthPanelMixin.show_health_settings` dan caption helper v1 dipakai
direct; worker `_refresh_device_health` diekstrak verbatim ke class shell agar
v1 app tidak diinstansiasi/ditimpa. Original lock/scheduling/error guards tetap.
Adapter hanya memetakan root.after → Kivy Clock, frame mailbox v2 → read-only
camera view, config printer lazy di worker, dan tombol ke audio owner v2.

F12/hold header membuka panel hanya idle atau Sandbox RECOVERY. Face invitation
terhenti selama modal; iklan/audio/visit tetap. Input epoch menolak release lama
setelah modal, single tap baru tetap bekerja. Close/minimize/stop mengakhiri modal
serta guard callback. Probe/export single-flight; hasil lama tidak mengecat panel
baru atau meninggalkan kontrol report terkunci.

JSON report hanya inventory aman + enam status allowlisted, bukan raw messages,
photos/logs/keys/address/serial/queue/QR/order. Semua acceptance fisik/provider tetap
NOT_RUN. Tidak ada device selection callback/setting writes, kamera baru, print
payload, watchdog/restart atau upload. [Proof](qa/portrait-v2-operator-health/README.md).

## 7. Bukti dan batas

Source 9433010: 688 full PASS / nol skip; CI tiga job SUCCESS, 109 PNG diverifikasi,
800×1280/452×900 direview. Native CI satu skip aset model opsional, tercakup local
full. [P5 proof](qa/portrait-v2-p5/README.md). Preflight Windows owner pada HEAD
0dc6555 = READY_FOR_MANUAL_TEST, **bukan** acceptance merchant/perangkat.

P5 merchant, hardware, print/paper, Drive/retensi 30 hari, privasi dan release
belum tersertifikasi. AI/Device Health/WhatsApp/update lab lain tetap referensi,
bukan bagian inventory aktif hanya karena ditemukan pada branch lain.
