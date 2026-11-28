# SMKMART — Sistem Pengelolaan Gudang dan Kasir

SMKMART adalah aplikasi berbasis terminal untuk membantu pengelolaan persediaan dan transaksi pada toko/kantin sekolah. Aplikasi ditulis dengan Python dan menyimpan data pada berkas teks di folder proyek.

## Fitur

### Admin
- Menambah, melihat, mencari, mengubah, dan menghapus barang.
- Mengelola pengguna dan kategori.
- Melihat peringatan ketika stok barang di bawah batas restock yang ditetapkan.
- Menghitung modal penjualan memakai FIFO dari batch stok.
- Melihat ringkasan penjualan dan laporan stok.
- Mengekspor daftar stok dan laporan penjualan ke berkas Excel (`.xlsx`) lengkap dengan tabel dan pie chart.

### Gudang
- Menambah, melihat, mencari, mengubah, dan menghapus barang.
- Menambah stok barang dengan mencatat modal per unit untuk batch FIFO.
- Saat menambah barang, memilih **Pakai barcode** atau **Tanpa barcode**. Saat mengubah barang, dapat memasukkan barcode baru, mempertahankan barcode, atau menghapusnya.
- Mendaftarkan dan mengelola barcode produk melalui menu **Kelola Barcode**.
- Melihat riwayat perubahan gudang dan ringkasan penjualan.
- Memulihkan barang dari Recycle Bin atau menghapusnya secara permanen.
- Mengekspor daftar stok dan laporan penjualan ke berkas Excel (`.xlsx`) lengkap dengan tabel dan pie chart.

### Kasir
- Menambah barang lewat pilihan **Masukkan ID barang** atau **Scan barcode**.
- Memindai barcode USB untuk menambahkan satu unit produk ke keranjang pada setiap pemindaian.
- Menambahkan barang ke keranjang dan menghapusnya dari keranjang.
- Melakukan checkout dengan pembayaran tunai, debit, atau QRIS.
- Menggabungkan barang yang sama dalam satu baris keranjang dan mengurangi jumlah satu per satu.
- Menghitung kembalian untuk pembayaran tunai.
- Melihat riwayat transaksi berdasarkan rentang tanggal atau bulan.
- Melihat ringkasan penjualan berdasarkan rentang tanggal.

## Teknologi

- Python 3
- Modul pustaka standar Python.
- `openpyxl` (opsional) untuk fitur ekspor Excel. Fitur lain tetap berjalan tanpa pustaka ini.

Pasang dependensi ekspor Excel dengan:

```bash
pip install -r requirements.txt
```

## Menjalankan aplikasi

### Cara cepat di Windows (disarankan)

1. Pasang Python 3 dan centang **Add Python to PATH** saat instalasi.
2. Klik dua kali `setup.bat` sekali saja. Skrip ini membuat virtual environment `.venv` lalu memasang seluruh dependensi dari `requirements.txt`.
3. Jalankan aplikasi dengan mengklik dua kali `run.bat`.
4. Kalau ada dependensi baru, cukup jalankan `setup.bat` lagi.

### Cara manual

1. Pasang Python 3.
2. Unduh atau klon repositori ini, lalu buka terminal di folder proyek.
3. Pasang dependensi:

   ```bash
   pip install -r requirements.txt
   ```

4. Jalankan:

   ```bash
   python "sistem gudang.py"
   ```

   Pada sebagian sistem, gunakan `python3` sebagai pengganti `python`.

Aplikasi meminta username dan password saat dijalankan. Data akun dibaca dari `User.txt`; gunakan akun yang sudah dikonfigurasi di berkas tersebut. Masukkan `0` pada username untuk keluar dari layar login.

Untuk menambahkan barang dari menu kasir, pilih **Tambah Barang ke Keranjang**, lalu pilih masukkan ID atau scan barcode. Pilihan ID menampilkan daftar barang dan meminta ID serta jumlah yang dibeli. Pilihan scan membuka mode pemindai. Menu **Barcode Scanner** juga membuka mode tersebut secara langsung.

Scanner USB yang berfungsi sebagai keyboard dapat mengirim kode barcode lalu Enter. Mode scanner menampilkan daftar barang yang memiliki barcode. Daftarkan barcode terlebih dahulu melalui menu admin/gudang **Kelola Barcode** atau saat menambah/mengubah barang. Setiap pemindaian menambahkan satu unit; pindai kode yang sama berulang kali untuk menambah jumlah barang tersebut. Masukkan `0` untuk keluar dari mode scanner.

Saat menambah barang, pilih `1` untuk memakai barcode lalu masukkan kodenya, atau `2` untuk tanpa barcode. Saat mengubah barang, pilih `1` untuk memasukkan barcode baru, `2` untuk menghapus barcode, atau `0` untuk mempertahankan barcode sekarang. Barcode harus unik dan disimpan sebagai teks, sehingga angka nol di awal tetap terjaga.

## Berkas data

Berkas berikut berada di direktori yang sama dengan program:

| Berkas | Kegunaan |
| --- | --- |
| `User.txt` | Data login, peran, status akun, dan pengaturan admin-only |
| `data.txt` | Data barang: ID internal, nama, stok, harga jual, status, batas restock, harga beli terakhir, dan barcode |
| `batch_stok.txt` | Sisa jumlah dan modal per unit dari setiap batch persediaan FIFO |
| `Harga asli.txt` | Riwayat harga modal masuk dengan urutan per barang |
| `kategori.txt` | Daftar kategori barang |
| `riwayat_gudang.txt` | Catatan perubahan persediaan |
| `riwayat_transaksi.txt` | Catatan transaksi penjualan |
| `keranjang.txt` | Berkas yang disertakan; isi keranjang aktif disimpan sementara selama aplikasi berjalan |
| `exports/` | Folder hasil ekspor Excel; dibuat otomatis saat ekspor pertama dijalankan |

Data disimpan sebagai teks lokal, bukan di basis data. Aplikasi membaca format `data.txt` lama empat sampai tujuh kolom dan menyimpan format saat ini dalam delapan kolom: `ID,Nama,Stok,HargaJual,Status,BatasRestock,HargaBeliTerakhir,Barcode`. Nilai barcode `0` berarti barang tidak memakai barcode; nilai kosong dari data lama tetap dapat dibaca. Barcode diperlakukan sebagai teks agar angka nol di depannya tetap terjaga. Untuk format lama tujuh kolom, aplikasi mengenali angka 8, 12, 13, atau 14 digit sebagai barcode; angka lain dianggap sebagai harga beli.

Baris akun pada `User.txt` menggunakan format `Username,Password/Hash,Peran,Status`. Akun baru dan password yang diganti disimpan sebagai hash PBKDF2 dengan salt. Akun lama yang masih memakai password teks biasa tetap dapat login dan otomatis dimigrasikan ke hash setelah login berhasil. Baris `Kunci=1` mengaktifkan mode admin-only; `Kunci=0` menonaktifkannya.

Setiap barang baru dan restok meminta harga beli/modal per unit. Batch stok disimpan dalam `batch_stok.txt` dengan format `ID,Urutan,TanggalMasuk,SisaJumlah,ModalPerUnit`. Saat checkout, barang diambil dari batch tertua terlebih dahulu; stok dan modal di tiap batch berkurang sesuai jumlah yang terjual. `Harga asli.txt` menyimpan riwayat modal dengan format `ID,Urutan,HargaModal`. Jika `batch_stok.txt` belum ada, stok lama dimigrasikan sekali menjadi batch pembuka memakai harga beli yang tersimpan di `data.txt`; stok tanpa harga modal akan tetap tercatat, tetapi laba transaksi yang memakai stok tersebut ditandai belum lengkap. Perubahan jumlah stok lewat menu ubah barang juga membuat atau mengurangi batch FIFO.

Buat salinan cadangan berkas data sebelum mengubahnya secara manual. Jangan menghapus atau mengganti nama berkas yang diperlukan aplikasi.

## Mengelola dependensi

`requirements.txt` memuat semua modul pihak ketiga. Setelah menambah `import` baru di kode, perbarui daftarnya dengan:

```bash
python update_requirements.py
```

Skrip ini memindai seluruh berkas `.py`, mengabaikan modul pustaka standar dan modul lokal, memetakan nama import ke paket PyPI yang benar (misalnya `PIL` menjadi `Pillow`), lalu menulis ulang `requirements.txt`. Versi yang sudah dipin akan dipertahankan. Setelah itu jalankan:

```bash
pip install -r requirements.txt
```

atau klik `setup.bat` di Windows. Modul yang sudah tidak dipakai akan otomatis dihapus dari daftar.

## Ekspor Excel

Pilih menu **Ekspor Laporan Excel** pada Menu Admin atau Menu Gudang, lalu pilih jenis laporan:

- **Daftar Stok**: sheet `Stok` berisi seluruh barang dengan harga jual, harga beli terakhir, nilai persediaan, barcode, dan keterangan stok. Baris dengan stok di bawah batas restock diberi warna merah, sedangkan yang aman berwarna hijau. Sheet `Per Kategori` merangkum jumlah barang, total stok, dan nilai persediaan per kategori beserta pie chart.
- **Laporan Penjualan**: masukkan rentang tanggal, atau kosongkan untuk seluruh transaksi. Berkas berisi sheet `Transaksi`, `Barang Terjual` (dengan pie chart proporsi unit terjual), `Kategori` (dengan pie chart proporsi pendapatan), dan `Ringkasan Harian`.

Berkas disimpan di folder `exports` dengan nama berisi tanggal dan waktu, sehingga ekspor sebelumnya tidak tertimpa. Barcode ditulis sebagai teks agar angka nol di depan tetap terjaga. Jika `openpyxl` belum terpasang, aplikasi menampilkan instruksi pemasangan dan fitur lain tetap dapat digunakan.

## Catatan keamanan dan batasan

Repositori dapat memuat akun lama dalam teks biasa serta berkas riwayat dan persediaan contoh. Akun lama dimigrasikan ke hash setelah login berhasil, tetapi sampai saat itu password lama masih terbaca di `User.txt`. Ganti atau hapus akun contoh sebelum penggunaan nyata; tinjau juga riwayat dan data stok sebelum membagikan repositori.

Aplikasi ini dirancang sebagai proyek pembelajaran berbasis terminal. Data lokal tidak menyediakan akses serentak yang aman untuk banyak pengguna. Aplikasi memeriksa akumulasi jumlah barang di keranjang dan memvalidasi ulang stok saat checkout, tetapi tetap sebaiknya digunakan oleh satu pengguna pada satu waktu.

Kode aplikasi berada di `sistem gudang.py`. Alur interaktif dimulai melalui fungsi `main()` hanya saat file dijalankan langsung; mengimpor modul tidak akan menampilkan menu login.

## Lisensi

Belum ada berkas lisensi di repositori ini. Hak penggunaan dan distribusi belum dinyatakan.
