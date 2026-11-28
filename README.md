# SMKMART

**SMKMART adalah aplikasi kasir dan pengelolaan gudang sederhana untuk toko atau kantin sekolah.** Aplikasi berjalan di terminal dan dibuat dengan Python. Admin mengatur pengguna, barang, dan laporan; petugas gudang mencatat persediaan; kasir melayani penjualan.

## Mulai menggunakan SMKMART

### Cara paling mudah di Windows

1. Pastikan komputer terhubung ke internet saat pemasangan.
2. Buka folder proyek, lalu klik dua kali **`setup.bat`**. Skrip ini menyiapkan Python yang diperlukan dan memasang paket aplikasi.
3. Setelah selesai, klik dua kali **`run.bat`** untuk menjalankan aplikasi.
4. Masuk menggunakan akun yang tercatat di `User.txt`.

Jika Python belum tersedia, `setup.bat` akan menawarkan pemasangan otomatis. Jika ada masalah, jalankan **`cek.bat`** untuk memeriksa instalasi dan berkas data. Pemeriksaan dapat menawarkan perbaikan otomatis.

### Menjalankan secara manual

Jika Python sudah terpasang, buka terminal di folder proyek dan jalankan:

```bash
pip install -r requirements.txt
python "sistem gudang.py"
```

Pada beberapa komputer, gunakan `python3` sebagai pengganti `python`.

Masukkan `0` pada kolom username untuk keluar dari layar login. Akun dan peran pengguna dibaca dari `User.txt`.

## Apa yang bisa dilakukan?

### Admin

- Mengelola pengguna dan kategori barang.
- Menambah, melihat, mencari, mengubah, dan menghapus barang.
- Melihat laporan stok, riwayat transaksi, ringkasan penjualan, dan laba FIFO.
- Mengunduh laporan stok atau penjualan ke Excel.
- Membuka menu Kasir atau menu Gudang.

### Gudang

- Menambah barang baru dan mencatat jumlah, harga jual, harga beli/modal, serta batas minimum stok.
- Melakukan restok; setiap restok mencatat harga beli per unit sebagai batch FIFO baru.
- Mengubah atau menghapus barang, mengelola barcode, dan memulihkan barang dari Recycle Bin.
- Melihat riwayat perubahan stok, ringkasan penjualan, dan laporan Excel.

Saat menambah barang, pilih **1. Pakai barcode** atau **2. Tanpa barcode**. Saat mengubah barang, pilih untuk memasukkan barcode baru, menghapus barcode, atau mempertahankan barcode yang sudah ada.

### Kasir

- Menambahkan barang berdasarkan ID atau memindai barcode.
- Melihat keranjang dan mengurangi atau menghapus jumlah barang.
- Menyelesaikan pembayaran tunai, debit, atau QRIS; pembayaran tunai menghitung kembalian.
- Melihat riwayat transaksi berdasarkan tanggal dan ringkasan penjualan berdasarkan rentang tanggal.

## Barcode dan cara menjual barang

Untuk menjual berdasarkan ID, pilih **Tambah Barang ke Keranjang**, lalu pilih **Masukkan ID barang**. Aplikasi menampilkan daftar barang; masukkan ID dan jumlah yang dibeli.

Untuk barcode, pilih **Scan barcode** atau menu **Barcode Scanner**. Daftar barang yang sudah memiliki barcode akan ditampilkan. Scanner USB yang bekerja seperti keyboard dapat mengirim barcode lalu Enter. Setiap pemindaian menambahkan **satu unit** ke keranjang; pindai kode yang sama lagi untuk menambahkan unit berikutnya. Masukkan `0` untuk keluar dari mode scanner.

Barcode dikelola melalui menu **Kelola Barcode** atau saat menambah/mengubah barang. Barcode harus unik. Angka nol di awal barcode tetap disimpan, misalnya `001234567890`.

## Modal dan laba dengan FIFO

Harga beli barang dapat berubah setiap kali restok. SMKMART menyimpan sisa persediaan dan modal tiap pembelian sebagai batch. Saat barang terjual, sistem memakai batch yang paling lama terlebih dahulu (**FIFO**, *First In, First Out*). Modal barang terjual dihitung dari batch yang benar-benar dipakai; laba adalah penjualan dikurangi modal tersebut.

Masukkan harga modal per unit sebagai angka tanpa pemisah ribuan, misalnya `2800`. Jika modal batch belum diketahui, transaksi tetap dapat dicatat, tetapi laba yang bergantung pada batch itu ditandai belum lengkap. Transaksi lama yang tidak memiliki catatan modal FIFO tidak dihitung ulang.

Jika total stok pada `data.txt` berbeda dari jumlah sisa batch pada `batch_stok.txt`, aplikasi memberi peringatan dan dapat membatalkan restok, perubahan stok, atau checkout. Periksa kedua berkas dan catatan perubahan terlebih dahulu; jangan menebak jumlah untuk menyamakan stok.

## Laporan Excel

Pilih **Ekspor Laporan Excel** pada menu Admin atau Gudang.

- **Daftar Stok** berisi barang, stok, harga jual, modal terakhir, nilai persediaan, barcode, dan keterangan batas restok. Laporan juga merangkum barang per kategori.
- **Laporan Penjualan** dapat dibuat untuk rentang tanggal atau seluruh transaksi. Berkas mencakup transaksi, barang terjual, kategori, dan ringkasan harian, beserta grafik.

Hasil disimpan di folder `exports` dengan tanggal dan waktu pada nama berkas agar ekspor sebelumnya tidak tertimpa. Fitur ini memakai `openpyxl`; jika paket tersebut tidak tersedia, pasang dependensi dengan `pip install -r requirements.txt`.

## Berkas yang digunakan aplikasi

Semua berkas data utama berada di folder proyek.

| Berkas | Isi |
| --- | --- |
| `User.txt` | Username, password/hash, peran, status akun, dan pengaturan admin-only |
| `data.txt` | Daftar barang dan stok saat ini |
| `batch_stok.txt` | Sisa jumlah serta modal per batch persediaan FIFO |
| `Harga asli.txt` | Riwayat harga modal barang yang masuk |
| `kategori.txt` | Daftar kategori barang |
| `riwayat_gudang.txt` | Catatan tambah, restok, ubah, dan penghapusan barang |
| `riwayat_transaksi.txt` | Catatan penjualan dan pembayaran |
| `keranjang.txt` | Berkas keranjang yang disertakan proyek; isi keranjang aktif dikelola selama aplikasi berjalan |
| `exports/` | Folder laporan Excel; dibuat saat ekspor pertama |

### Format data barang

`data.txt` disimpan dalam delapan kolom dengan urutan:

```text
ID,Nama,Stok,HargaJual,Status,BatasRestock,HargaBeliTerakhir,Barcode
```

Contoh:

```text
101,Indomie Goreng,35,3500,aktif,5,2800,089123456789
102,Mie Sedaap Soto,40,3300,aktif,5,2600,0
```

Nilai barcode `0` berarti barang tidak memakai barcode. Kolom barcode kosong dari berkas lama juga tetap dapat dibaca. Barcode diperlakukan sebagai teks agar nol di depannya tidak hilang. Aplikasi masih dapat membaca format lama empat sampai tujuh kolom.

Format dua berkas FIFO dan modal:

```text
batch_stok.txt: ID,Urutan,TanggalMasuk,SisaJumlah,ModalPerUnit
Harga asli.txt: ID,Urutan,HargaModal
```

Jika `batch_stok.txt` belum ada, aplikasi membuat batch pembuka dari stok dan harga beli di `data.txt`. Berkas lama yang tidak memiliki harga beli dapat menghasilkan laba yang belum lengkap.

### Akun dan password

Baris akun menggunakan format `Username,Password/Hash,Peran,Status`. Password untuk akun baru disimpan sebagai hash PBKDF2. Akun lama yang password-nya masih berupa teks biasa dapat masuk seperti biasa dan dimigrasikan ke hash setelah login berhasil. `Kunci=1` mengaktifkan mode admin-only; `Kunci=0` menonaktifkannya.

## Pemeriksaan dan perbaikan instalasi

Klik dua kali `cek.bat` untuk memeriksa Python, paket yang diperlukan, izin tulis, akun pengguna, dan format beberapa berkas data. Hasil `[OK]` berarti pemeriksaan lolos; `[!!]` menunjukkan peringatan; `[!]` menunjukkan masalah yang perlu ditangani. Jika tersedia, skrip menawarkan perbaikan otomatis.

Untuk menjalankan pemeriksaan/perbaikan otomatis dari terminal Windows:

```bat
cek.bat --auto-repair
```

Jika menambahkan paket Python ke kode, perbarui daftar paket dengan `python update_requirements.py`, lalu jalankan kembali `setup.bat`.

## Catatan penting

- SMKMART menyimpan data dalam berkas teks lokal, bukan database. Jangan menjalankan salinan aplikasi yang sama secara bersamaan dari beberapa komputer; perubahan stok dapat saling menimpa.
- Buat salinan cadangan `data.txt`, `batch_stok.txt`, dan berkas riwayat sebelum mengeditnya secara manual.
- Proyek dapat berisi akun lama dalam teks biasa serta data stok dan riwayat contoh. Ganti akun contoh dan tinjau data sebelum penggunaan nyata atau membagikan folder proyek.
- Proyek ini dibuat untuk pembelajaran dan penggunaan skala kecil. Tinjau dan cocokkan stok secara berkala.

## Lisensi

Belum ada berkas lisensi di repositori ini; hak penggunaan dan distribusi belum dinyatakan.
