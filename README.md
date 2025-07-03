# Aplikasi Kasir Desktop - Toko Elvan

![Toko Elvan Logo](logo_only.png)

Aplikasi Point of Sale (POS) atau kasir desktop yang dibuat menggunakan Python dan Tkinter dengan tema modern dari `ttkbootstrap`. Aplikasi ini dirancang untuk mengelola transaksi, produk, dan laporan penjualan untuk toko atau warung.

## Tampilan Aplikasi

| Tampilan Login | Halaman Kasir (Dengan Search Bar) |
| :---: | :---: |
| *(Screenshot halaman login Anda di sini)* | *(Screenshot halaman kasir Anda di sini)* |

| Manajemen Produk | Laporan Penjualan | Struk PDF |
| :---: | :---: | :---: |
| *(Screenshot halaman manajemen produk)* | *(Screenshot halaman laporan)* | *(Screenshot contoh struk PDF)* |


## Fitur Utama

- **Sistem Login**: Hak akses terpisah untuk `admin` dan `kasir`.
- **Splash Screen**: Menampilkan logo toko saat aplikasi pertama kali dijalankan.
- **Antarmuka Kasir Modern**: Dilengkapi dengan *search bar* untuk pencarian produk yang cepat.
- **Manajemen Produk**: Fitur lengkap (Tambah, Edit, Hapus) untuk produk beserta stoknya.
- **Manajemen Pengguna**: Admin dapat menambah dan menghapus akun kasir.
- **Riwayat Lengkap**:
    - **Riwayat Transaksi**: Melihat kembali semua transaksi yang pernah terjadi beserta detailnya.
    - **Riwayat Stok**: Melacak setiap pergerakan stok (masuk karena penambahan, keluar karena penjualan, atau koreksi).
- **Laporan Penjualan**:
    - Filter laporan berdasarkan harian dan bulanan.
    - **Download Laporan ke Excel** untuk analisis lebih lanjut.
- **Cetak Struk ke PDF**:
    - Membuat struk dalam format PDF secara otomatis setelah transaksi.
    - Menyimpan struk di folder `Documents/Struk Warung` pengguna.

## Teknologi yang Digunakan

- **Bahasa**: Python 3
- **Antarmuka (GUI)**: Tkinter & `ttkbootstrap`
- **Database**: SQLite3
- **Pembuatan PDF**: `reportlab`
- **Export Excel**: `openpyxl`
- **Gambar & Ikon**: `Pillow`
- **Interaksi OS (Cetak)**: `pywin32` (untuk Windows)

## Instalasi & Menjalankan Proyek

Untuk menjalankan proyek ini di komputer Anda, ikuti langkah-langkah berikut:

1.  **Clone Repositori**
    ```bash
    git clone [https://github.com/NAMA_ANDA/NAMA_REPO_ANDA.git](https://github.com/NAMA_ANDA/NAMA_REPO_ANDA.git)
    cd NAMA_REPO_ANDA
    ```

2.  **(Sangat Disarankan) Buat Virtual Environment**
    ```bash
    python -m venv venv
    venv\Scripts\activate  # Untuk Windows
    ```

3.  **Instal Semua Pustaka yang Dibutuhkan**
    ```bash
    pip install ttkbootstrap pillow reportlab openpyxl pywin32
    ```

4.  **Inisialisasi Database**
    Jalankan perintah ini satu kali untuk membuat file `warung.db` dan akun `admin` default.
    ```bash
    python database.py
    ```
    - **Username**: `admin`
    - **Password**: `admin`

5.  **Jalankan Aplikasi Utama**
    ```bash
    python main.py
    ```

## Mengemas Aplikasi menjadi `.exe`

Gunakan PyInstaller untuk membuat file `.exe` mandiri. Pastikan semua file aset (`logo.png`, `logo_only.png`, `logo.ico`) ada di folder.

```bash
pyinstaller --onefile --windowed --add-data "logo.png;." --add-data "logo_only.png;." --icon="logo.ico" --name "KasirTokoElvan" main.py
```
File `.exe` final akan berada di dalam folder `dist`.
