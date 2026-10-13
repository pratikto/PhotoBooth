# PhotoBooth

Aplikasi photo booth sederhana dengan Python, Tkinter, dan OpenCV.

## Fitur

- Menampilkan preview langsung dari webcam.
- Mengambil satu foto saat tombol AMBIL FOTO ditekan.
- Menyimpan foto JPG ke folder photos.
- Menutup koneksi kamera saat aplikasi ditutup atau tombol Escape ditekan.

## Menjalankan aplikasi

Buka terminal di folder project, lalu jalankan:

    python -m pip install -r requirements.txt
    python main.py

## Jika kamera tidak terdeteksi

Program memakai indeks kamera 0 secara default. Jika menggunakan webcam USB dan tidak muncul, coba ganti nilai camera_index=0 menjadi camera_index=1 di photobooth/app.py.

Di Windows, pastikan izin kamera untuk aplikasi desktop sudah diaktifkan di Settings > Privacy & security > Camera. Tutup aplikasi lain seperti Zoom, Teams, atau Camera jika sedang memakai webcam.

## Susunan kode

- main.py memulai aplikasi.
- photobooth/app.py mengatur jendela, preview, dan tombol.
- photobooth/camera.py mengatur koneksi dan pembacaan frame kamera.
- photobooth/photo_storage.py menyimpan frame sebagai file JPG.
- requirements.txt mencatat library yang dibutuhkan.
- Folder photos dibuat otomatis saat foto pertama diambil.

Folder photos dan file sementara Python tidak disimpan di GitHub.
