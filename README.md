# SMKMART — Sistem Pengelolaan Gudang dan Kasir

SMKMART adalah aplikasi berbasis terminal untuk membantu pengelolaan persediaan dan transaksi pada toko/kantin sekolah. Aplikasi ditulis dengan Python dan menyimpan data pada berkas teks di folder proyek.

## Fitur

### Admin
- Menambah, melihat, mencari, mengubah, dan menghapus barang.
- Mengelola kategori serta menambah stok barang.
- Mendaftarkan dan mengelola barcode produk.
- Melihat riwayat perubahan gudang dan ringkasan penjualan.
- Memulihkan barang dari Recycle Bin atau menghapusnya secara permanen.
- Melihat peringatan ketika stok barang kurang dari lima.

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
- Modul pustaka standar Python; tidak ada dependensi pihak ketiga yang diperlukan.

## Menjalankan aplikasi

1. Pasang Python 3.
2. Unduh atau klon repositori ini, lalu buka terminal di folder proyek.
3. Jalankan:

   ```bash
   python "sistem gudang.py"
   ```

   Pada sebagian sistem, gunakan `python3` sebagai pengganti `python`.

Aplikasi meminta username dan password saat dijalankan. Data akun dibaca dari `User.txt`. Gunakan akun yang sudah dikonfigurasi di berkas tersebut. Masukkan `0` untuk username dan password jika ingin keluar dari layar login.

## Berkas data

Berkas berikut berada di direktori yang sama dengan program:

| Berkas | Kegunaan |
| --- | --- |
| `User.txt` | Data login dan peran pengguna |
| `data.txt` | Data barang, stok, harga, status, batas restock, dan barcode |
| `kategori.txt` | Daftar kategori barang |
| `riwayat_gudang.txt` | Catatan perubahan persediaan |
| `riwayat_transaksi.txt` | Catatan transaksi penjualan |
| `keranjang.txt` | Berkas data keranjang yang disertakan dalam repositori |

Data disimpan sebagai teks lokal, bukan di basis data. Buat salinan cadangan berkas data sebelum mengubahnya secara manual. Jangan menghapus atau mengganti nama berkas yang diperlukan aplikasi.

## Catatan keamanan dan batasan

Repositori saat ini menyertakan data akun dalam teks biasa dan berkas riwayat yang berisi data contoh. Jangan gunakan akun atau data bawaan untuk lingkungan nyata. Sebelum penggunaan bersama atau produksi, pindahkan kredensial dari repositori, gunakan penyimpanan kata sandi yang aman, dan tinjau riwayat transaksi sebelum membagikan repositori.

Aplikasi ini dirancang sebagai proyek pembelajaran berbasis terminal. Data lokal tidak menyediakan akses serentak yang aman untuk banyak pengguna. Aplikasi memeriksa akumulasi jumlah barang di keranjang dan memvalidasi ulang stok saat checkout, tetapi tetap sebaiknya digunakan oleh satu pengguna pada satu waktu.

Kode aplikasi berada di `sistem gudang.py`. Alur interaktif dimulai melalui fungsi `main()` hanya saat file dijalankan langsung; mengimpor modul tidak akan menampilkan menu login.

## Lisensi

Belum ada berkas lisensi di repositori ini. Hak penggunaan dan distribusi belum dinyatakan.
