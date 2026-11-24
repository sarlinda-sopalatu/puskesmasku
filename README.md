# PuskesmasKu — Python + Blue Neumorphism + Firebase

Aplikasi demonstrasi berbasis web. Python menangani server lokal, login email, registrasi, verifikasi email, reset password, profil Firestore dan sesi akun Firebase. HTML/CSS/JavaScript tetap digunakan untuk tampilan serta modul klinis contoh asli. Data klinis contoh tetap berada di localStorage browser. Jangan masukkan data pasien nyata. Tidak ada paket pip yang diperlukan.

## 1. Jalankan dari terminal VS Code (Windows 10/11)

1. Jika Python belum terpasang, unduh Python 3.10 atau lebih baru dari https://www.python.org/downloads/windows/ dan instal. Centang Add Python to PATH bila tersedia. Tutup dan buka kembali VS Code setelah instalasi.
2. Ekstrak ZIP. Buka folder PuskesmasKu yang berisi `app.py` melalui File > Open Folder.
3. Terminal > New Terminal. Periksa dengan `python --version` (atau `py --version`). Ketik `dir` untuk memastikan `app.py` ada.
4. Jalankan:

```powershell
python app.py
```

Jika perintah python tidak dikenali tetapi py tersedia, gunakan `py app.py`. Buka http://localhost:8000/ di browser. Biarkan terminal terbuka; tekan Ctrl+C untuk berhenti. Jika port sudah digunakan, ketik `python app.py --port 8080` dan buka http://localhost:8080/. Jangan menjalankan menggunakan Live Server atau membuka index.html langsung, karena API membutuhkan app.py. Tidak perlu PowerShell script, Flask, pip install, Node.js, XAMPP, ataupun hosting. Internet hanya diperlukan untuk Firebase; mode demo bisa dijalankan offline. Sesi akun Firebase tersimpan dalam memori server dan berakhir saat server dihentikan. Gunakan port yang sama untuk mempertahankan data demo browser.

## 2. Pengaturan Firebase (sekali saja)

Konfigurasi Web App yang sebelumnya diberikan untuk project `puskesmas-arbes` sudah diisi dalam `firebase_config.py`. Nama merek PuskesmasKu tidak harus sama dengan ID project Firebase. Bila Anda ingin memakai project lain, ganti API_KEY dan PROJECT_ID dengan konfigurasi Web App dari project milik Anda.

1. Buka https://console.firebase.google.com/ dan pilih project `puskesmas-arbes`.
2. Project settings > General > Your apps. Pastikan aplikasi Web terdaftar, lalu cocokkan config dengan `firebase_config.py`. Tidak perlu mengaktifkan Analytics atau Firebase Hosting. Jangan memasukkan service account private key atau password Gmail.
3. Build > Authentication > Get started > Sign-in method > Email/Password > Enable > Save. Tidak perlu mengaktifkan Email link sign-in.
4. Authentication > Settings > Authorized domains > Add domain > masukkan `localhost`. Domain tanpa `http://` atau port. Gunakan alamat localhost dalam panduan ini. Jika tetap menggunakan handler reset bawaan Firebase, pastikan domain `puskesmas-arbes.firebaseapp.com` juga tersedia. Jangan menambahkan localhost ke project produksi.
5. Authentication > Templates > Password reset. Gunakan action URL bawaan Firebase, bukan URL file atau localhost. Atur nama pengirim dan nama publik project jika tersedia. Firebase akan menangani halaman penggantian password pada link email; website ini tidak perlu di-hosting sendiri.
6. Build > Firestore Database > Create database (default) > pilih lokasi dan Production mode. Perhatikan batas kuota/biaya Firebase. Buka Rules. Salin isi `firestore.rules` dari proyek ini lalu Publish. **Jika project memiliki rules/data lain, gabungkan match `/profiles/{uid}` secara hati-hati, jangan menimpa aturan aplikasi lain tanpa memeriksanya.** Jangan gunakan aturan `allow read, write: if true`.
7. Kini coba daftar dengan email yang dapat Anda akses. Jangan menggunakan akun demo untuk reset email.

## 3. Daftar akun baru dan peran

Klik Daftar akun sekarang. Isi nama, username tampilan (bukan login akun Firebase), email aktif, nomor HP opsional, peran yang diajukan, password minimal 8 karakter, dan konfirmasi. Klik Buat akun. Firebase membuat akun email dan profil Firestore. Periksa email verifikasi. Klik tautan verifikasi. Masuk dengan **email** dan password. Jika email verifikasi tidak diterima, masuk dan gunakan tombol kirim ulang pada halaman sambutan.

Peran yang tersedia: Administrator (`admin`), Petugas Pendaftaran (`pendaftaran`), Dokter (`dokter`), Perawat (`perawat`), Petugas Farmasi (`farmasi`), Petugas Kasir (`kasir`), Pasien/Pengunjung (`pengunjung`). Akun petugas yang baru mendaftar tetap sebagai `pengunjung` dengan status `pending` hingga email terverifikasi dan pengelola menyetujui. Pasien/Pengunjung hanya melihat halaman sambutan, belum menjadi portal pasien penuh.

### Persetujuan peran petugas

Pengelola Firebase Console memverifikasi identitas pemohon dan email (Authentication > Users, lihat UID akun). Pada Firestore Database > Data > profiles > pilih dokumen dengan UID yang sama. Ubah field `role` dari `pengunjung` menjadi nilai yang sesuai (misalnya `dokter`) dan `status` dari `pending` ke `approved` (keduanya bertipe string). Jangan memberikan `admin` kepada orang yang tidak berwenang. Minta pengguna keluar lalu masuk kembali. Untuk menonaktifkan akun, gunakan Authentication > Users > Disable account dan/atau set status `disabled`. Jangan mengubah role dari menu manajemen akun demo. Pengaturan klinik dan role di dashboard lama hanya merupakan simulasi lokal.

## 4. Uji lupa password melalui email asli

1. Pada login, klik Lupa password?
2. Masukkan alamat email akun yang telah terdaftar pada Authentication > Users.
3. Klik Kirim tautan reset. Firebase menerima permintaan; demi privasi, respons yang sama juga dapat muncul untuk email tidak terdaftar.
4. Buka Gmail/email penerima, periksa Inbox, Spam dan Promotions. Klik tautan reset dari Firebase.
5. Masukkan password baru di halaman Firebase dan simpan. Kembali ke `http://localhost:8000/#/login` lalu masuk dengan email dan password baru. Firebase mengirim **tautan**, bukan OTP 6 digit atau password baru.

## 5. Akun demo lokal

Klik panel Akun demonstrasi untuk memperluas daftar satu kolom. Klik peran untuk mengisi form lalu klik Masuk. Admin: `admin / admin123`. Pendaftaran: `pendaftaran / 123456`. Dokter: `dokter / 123456`. Perawat: `perawat / 123456`. Farmasi: `farmasi / 123456`. Kasir: `kasir / 123456`. Akun demo tidak terdaftar di Firebase, tidak dapat menerima reset email, dan tidak dimaksudkan untuk penggunaan nyata.

## 6. Pemecahan masalah

- `python` tidak dikenali: instal Python, aktifkan PATH, buka kembali VS Code atau coba `py app.py`.
- Untuk pengujian API lokal buka http://localhost:8000/api/health; hasilnya memuat `"backend": "Python"`.

- `app.py` tidak ditemukan: pastikan terminal berada di folder ekstraksi yang tepat (`dir`).
- `OPERATION_NOT_ALLOWED`: aktifkan Email/Password di Authentication.
- `PERMISSION_DENIED`: buat Firestore default dan publish aturan yang disediakan; pastikan project ID cocok.
- `API_KEY_INVALID`/API restriction: salin config asli dari Firebase Console dan periksa pembatasan API (Identity Toolkit API, Token Service API, Firestore API) (panggilan dilakukan dari Python, bukan browser; pembatasan HTTP referrer browser mungkin perlu disesuaikan di project pengembangan).
- Profil tidak ditemukan: akun Auth lama mungkin belum memiliki profil. Pengelola dapat membuat dokumen `profiles/{UID}` secara manual berisi field string `name`, `username`, `email`, `phone`, `requestedRole`, `role`, `status`; gunakan `pengunjung` dan `pending` sebagai role/status awal. Jangan menghapus akun tanpa memastikan pemilik dan kebutuhan migrasi.
- Email tidak masuk: pastikan akun ada di Authentication > Users, cek Spam/Promotions, kuota pengiriman, template email dan action URL. Coba kirim melalui menu reset password pada Firebase Console untuk diagnosis. Tidak perlu SMTP Gmail atau .env.
- Data demo berbeda: localhost, 127.0.0.1 dan port yang berbeda memakai penyimpanan browser berbeda. Data server Python/SQLite dari versi lama tidak otomatis bermigrasi ke Firebase; daftarkan ulang atau migrasikan secara resmi.

## 7. Struktur

`index.html` shell utama; `css/styles.css` tema; `firebase_config.py` konfigurasi publik; `js/auth-api.js` penghubung browser ke Python; `js/app.js` login/router; `js/data.js` data demo dan hak akses lokal; `js/dashboard.js`, `patients.js`, `queues.js`, `exams.js`, `pharmacy.js`, `billing.js`, `reports.js`, `users.js` modul asli; `firestore.rules` aturan profil; `app.py` server Python lokal; `firebase_auth.py` layanan Firebase REST; `firebase_config.py` konfigurasi Firebase; `docs/` dokumentasi modul lama (historis, bukan panduan konfigurasi Firebase).

## 8. Batasan keamanan

Firebase mengamankan autentikasi dan profil cloud, tetapi data klinis dan otorisasi modul lama berada di browser. Demo admin terbuka dan localStorage dapat dimodifikasi melalui DevTools. Gunakan data fiktif saja. Untuk produksi perlu menghapus demo, memindahkan data klinis ke backend yang memiliki aturan akses server-side dan audit, serta menguji pengelolaan sesi dan kepatuhan privasi. Konfigurasi Firebase Console dan pengiriman email nyata harus diuji menggunakan project dan inbox Anda sendiri.

## 9. Pengujian otomatis

Jalankan `python -m unittest discover -s tests -v`. Tes memakai Firebase tiruan, tidak mengirim email nyata. Pengiriman email harus diuji menggunakan akun Firebase milik Anda.
"# puskesmasku" 
