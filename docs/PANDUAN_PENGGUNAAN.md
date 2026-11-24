# Panduan Pengguna PuskesmasKu

## Overview
PuskesmasKu adalah sistem informasi terpadu untuk pendaftaran, antrean, rekam medis elektronik, farmasi, pembayaran, dan laporan pada puskesmas Kecamatan Sukamaju.

## Branding
- **Nama Aplikasi**: PuskesmasKu
- **Instansi**: Puskesmas Kecamatan Sukamaju
- **Motto**: Melayani dengan hati, untuk masyarakat yang lebih sehat.

## Warna Ungu Aplikasi
- Deep Teal: #0b3b34 (primer)
- Mint: #7ce3c8 (accent)
- Coral: #f3a47b (secondary)

## Menu Navigasi
Sistem memiliki 6 peran utama dengan hak akses berbeda:
1. **Administrator** - Akses penuh ke seluruh modul, pengguna, hak akses, dan pengaturan
2. **Petugas Pendaftaran** - Mengelola data pasien, pendaftaran kunjungan, dan antrean layanan
3. **Dokter** - Memeriksa pasien, mengisi rekam medis elektronik, diagnosis, dan resep
4. **Perawat** - Mengelola alur antrean dan mencatat tanda vital/asesmen awal pasien
5. **Petugas Farmasi** - Mengelola master obat, stok, penerimaan, resep, dan penyerahan obat
6. **Petugas Kasir** - Mengelola tarif, tagihan, verifikasi penjaminan, pembayaran, dan kuitansi

## Login
- Akun default tersedia di aplikasi
- Setiap peran memiliki username dan password masing-masing
- Password contoh: `admin123` untuk administrator dan `123456` untuk akun petugas lainnya
- Username sesuai peran: admin, pendaftaran, dokter, perawat, farmasi, kasir

## Daftar Akun Baru dan Lupa Password
- Jalankan `MULAI-WINDOWS.bat` untuk mengaktifkan server lokal Python.
- Halaman `#/daftar` untuk daftar memakai username, nama, email, dan password.
- Akun baru mendapat peran **Akun Baru** sampai operator memberikan persetujuan.
- Halaman `#/lupa-password`: minta kode verifikasi 6 angka yang dikirim SMTP ke email terdaftar. Kode berlaku 10 menit.
- **Akun demo lama tidak mempunyai email yang terdaftar dalam database SQLite; reset kode email berlaku untuk akun baru.**
- Panduan SMTP dan App Password secara rinci: [PANDUAN_MULAI_DAN_RESET_EMAIL.md](../PANDUAN_MULAI_DAN_RESET_EMAIL.md).

## Fungsi Utama per Modul

### 1. Dashboard
- Menampilkan statistik kunjungan, antrean aktif, resep menunggu, dan pending
- Grafik tren kunjungan/pendapatan 7 hari terakhir
- Tugas prioritas sesuai peran pengguna

### 2. Pendaftaran Pasien
- Daftar pasien baru dengan validasi NIK (16 digit) dan BPJS (13 digit)
- Cari pasien berdasarkan RM atau NIK
- Riwayat kunjungan pasien lengkap dengan detail pemeriksaan

### 3. Antrean Pasien
- Daftarkan antrean baru per poli
- Priority queue untuk lansia, ibu hamil, disabilitas, anak balita, darurat
- Panggil antrean berikutnya, lihat antrean menunggu per poli
- Cetak tiket antrean, suara panggilan opsional

### 4. Rekam Medis Elektronik (EMR)
- Pemeriksaan dokter: keluhan, diagnosis ICD-10, tindakan, resep elektronik
- Asesmen nurse: tanda vital (tekanan darah, nadi, suhu, respirasi, BB, TB, SpO2)
- Selesaikan pemeriksaan, buat bill, simpan kontrol ulang
- Cetak rekam medis lengkap dengan tanda tangan dokter

### 5. Farmasi & Obat
- Master obat: stok, minimum, harga, masa kadaluwarsa
- Penerimaan stok obat dari distributor
- Pengeluaran obat berdasarkan resep
- Resep menunggu diserahkan farmasi
- Stok menipis/habis, obat kedaluwarsa alerts
- Laporan penggunaan obat lengkap

### 6. Pembayaran & Tarif
- Verifikasi penjaminan BPJS (cek SEP)
- Terima pembayaran tunai/QRIS/Transfer/Bank
- Cetak kuitansi/resep digital
- Kelola tarif layanan (konsultasi, tindakan, administrasi)
- Riwayat transaksi lengkap per pasien

### 7. Laporan & Analitik
- 6 tab laporan: Ringkasan, Kunjungan, Poli, Penyakit, Obat, Petugas
- Filter tanggal, poli, status
- Export CSV ke file lokal
- Cetak laporan terformat
- Dashboard kinerja terintegrasi

### 8. Pengguna & Hak Akses
- Daftar lengkap pengguna sistem
- Matriks hak akses per role (editable hanya admin)
- Pengaturan klinik: nama, instansi, alamat, kontak, motto
- Profil pengguna: nama, nomor telepon, perubahan password
- Aktivitas audit log lengkap

### 9. Display Antrean Publik
- Layar antrean tanpa perlu login
- Menampilkan nomor antrean yang sedang dipanggil
- Antrean berikutnya per poli
- Motto puskesmas dan informasi pelayanan
- Bisa diakses dari URL langsung: `#/display`

## Akun Demo
| Peran | Username | Password |
|-------|----------|----------|
| Administrator | admin | admin123 |
| Petugas Pendaftaran | pendaftaran | 123456 |
| Dokter | dokter | 123456 |
| Perawat | perawat | 123456 |
| Petugas Farmasi | farmasi | 123456 |
| Petugas Kasir | kasir | 123456 |
| Dokter Gigi | dokter.gigi | 123456 |
| Pendaftaran (non-aktif) | pendaftaran2 | 123456 |

## Catatan Teknis
- Data klinis demonstrasi lama disimpan di `localStorage` browser; akun baru dan OTP email dikelola server lokal Python dengan SQLite
- Versi data: `PuskesmasKu.db.v1`
- Seed version: 1
- Jika ada perubahan skema, clear localStorage atau bump seed version
- Aplikasi responsif, modern browser expected
- Gunakan `MULAI-WINDOWS.bat` atau `python server.py`. Server statis biasa tidak mendukung registrasi dan email.

## Versi
- Aplikasi: v1.1.0
- Sprint: Sprint 4

---
*Dokumen ini dibuat untuk sistem PuskesmasKu — Aplikasi manajemen puskesmas terintegrasi.*