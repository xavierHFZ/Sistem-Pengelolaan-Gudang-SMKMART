# SMKMART — Sistem Pengelolaan Gudang dan Kasir

SMKMART adalah aplikasi berbasis terminal untuk membantu pengelolaan persediaan dan transaksi pada toko/kantin sekolah. Aplikasi ditulis dengan Python dan menyimpan data pada berkas teks di folder proyek.

## Fitur

### Admin
- Menambah, melihat, mencari, mengubah, dan menghapus barang.
- Mengelola kategori serta menambah stok barang.
- Mendaftarkan dan mengelola barcode produk.
- Menghitung modal penjualan memakai FIFO dari batch stok.
- Melihat riwayat perubahan gudang dan ringkasan penjualan.
- Memulihkan barang dari Recycle Bin atau menghapusnya secara permanen.
- Melihat peringatan ketika stok barang di bawah batas restock yang ditetapkan.
- Mengekspor daftar stok dan laporan penjualan ke berkas Excel (`.xlsx`) lengkap dengan tabel dan pie chart.

### Kasir
- Mencari dan memilih barang berdasarkan ID.
- Memindai barcode USB untuk menambahkan produk ke keranjang.
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

1. Pasang Python 3.
2. Unduh atau klon repositori ini, lalu buka terminal di folder proyek.
3. Jalankan:

   ```bash
   python "sistem gudang.py"
   ```

   Pada sebagian sistem, gunakan `python3` sebagai pengganti `python`.

Aplikasi meminta username dan password saat dijalankan. Data akun dibaca dari `User.txt`. Gunakan akun yang sudah dikonfigurasi di berkas tersebut. Masukkan `0` untuk username dan password jika ingin keluar dari layar login.

Untuk memakai Barcode Scanner, pilih menu **Barcode Scanner** pada menu kasir. Scanner USB yang berfungsi sebagai keyboard dapat mengirim kode barcode lalu Enter. Daftarkan barcode produk terlebih dahulu melalui menu admin **Kelola Barcode** atau saat menambah/mengubah barang. Setiap pemindaian menambahkan satu unit; pemindaian kode yang sama menambah jumlah pada baris keranjang yang sama. Masukkan `0` untuk keluar dari mode scanner.

## Berkas data

Berkas berikut berada di direktori yang sama dengan program:

| Berkas | Kegunaan |
| --- | --- |
| `User.txt` | Data login dan peran pengguna |
| `data.txt` | Data barang: ID internal, nama, stok, harga jual, status, batas restock, harga beli terakhir, dan barcode opsional |
| `batch_stok.txt` | Sisa jumlah dan modal per unit dari setiap batch persediaan FIFO |
| `Harga asli.txt` | Riwayat harga modal masuk dengan urutan per barang |
| `kategori.txt` | Daftar kategori barang |
| `riwayat_gudang.txt` | Catatan perubahan persediaan |
| `riwayat_transaksi.txt` | Catatan transaksi penjualan |
| `keranjang.txt` | Berkas yang disertakan; isi keranjang aktif disimpan sementara selama aplikasi berjalan |
| `exports/` | Folder hasil ekspor Excel; dibuat otomatis saat ekspor pertama dijalankan |

Data disimpan sebagai teks lokal, bukan di basis data. Aplikasi membaca format `data.txt` lama empat sampai tujuh kolom dan menyimpan format saat ini dalam delapan kolom: `ID,Nama,Stok,HargaJual,Status,BatasRestock,HargaBeliTerakhir,Barcode`. Barcode diperlakukan sebagai teks agar angka nol di depannya tetap terjaga. Untuk format lama tujuh kolom, aplikasi mengenali angka 8, 12, 13, atau 14 digit sebagai barcode; angka lain dianggap sebagai harga beli.

Setiap barang baru dan restok meminta harga beli/modal per unit. Batch stok disimpan dalam `batch_stok.txt` dengan format `ID,Urutan,TanggalMasuk,SisaJumlah,ModalPerUnit`. Saat checkout, barang diambil dari batch tertua terlebih dahulu; stok dan modal di tiap batch berkurang sesuai jumlah yang terjual. `Harga asli.txt` menyimpan riwayat modal dengan format `ID,Urutan,HargaModal`. Jika `batch_stok.txt` belum ada, stok lama dimigrasikan sekali menjadi batch pembuka memakai harga beli yang tersimpan di `data.txt`; stok tanpa harga modal akan tetap tercatat, tetapi laba transaksi yang memakai stok tersebut ditandai belum lengkap. Perubahan jumlah stok lewat menu ubah barang juga membuat atau mengurangi batch FIFO.

Buat salinan cadangan berkas data sebelum mengubahnya secara manual. Jangan menghapus atau mengganti nama berkas yang diperlukan aplikasi.

## Ekspor Excel

Pilih menu **Ekspor Laporan Excel** pada Menu Admin atau Menu Gudang, lalu pilih jenis laporan:

- **Daftar Stok**: sheet `Stok` berisi seluruh barang dengan harga jual, harga beli terakhir, nilai persediaan, barcode, dan keterangan stok. Baris dengan stok di bawah batas restock diberi warna merah, sedangkan yang aman berwarna hijau. Sheet `Per Kategori` merangkum jumlah barang, total stok, dan nilai persediaan per kategori beserta pie chart.
- **Laporan Penjualan**: masukkan rentang tanggal, atau kosongkan untuk seluruh transaksi. Berkas berisi sheet `Transaksi`, `Barang Terjual` (dengan pie chart proporsi unit terjual), `Kategori` (dengan pie chart proporsi pendapatan), dan `Ringkasan Harian`.

Berkas disimpan di folder `exports` dengan nama berisi tanggal dan waktu, sehingga ekspor sebelumnya tidak tertimpa. Barcode ditulis sebagai teks agar angka nol di depan tetap terjaga. Jika `openpyxl` belum terpasang, aplikasi menampilkan instruksi pemasangan dan fitur lain tetap dapat digunakan.

## Catatan keamanan dan batasan

Repositori saat ini menyertakan data akun dalam teks biasa dan berkas riwayat yang berisi data contoh. Jangan gunakan akun atau data bawaan untuk lingkungan nyata. Sebelum penggunaan bersama atau produksi, pindahkan kredensial dari repositori, gunakan penyimpanan kata sandi yang aman, dan tinjau riwayat transaksi sebelum membagikan repositori.

Aplikasi ini dirancang sebagai proyek pembelajaran berbasis terminal. Data lokal tidak menyediakan akses serentak yang aman untuk banyak pengguna. Aplikasi memeriksa akumulasi jumlah barang di keranjang dan memvalidasi ulang stok saat checkout, tetapi tetap sebaiknya digunakan oleh satu pengguna pada satu waktu.

Kode aplikasi berada di `sistem gudang.py`. Alur interaktif dimulai melalui fungsi `main()` hanya saat file dijalankan langsung; mengimpor modul tidak akan menampilkan menu login.

## Lisensi

Belum ada berkas lisensi di repositori ini. Hak penggunaan dan distribusi belum dinyatakan.
