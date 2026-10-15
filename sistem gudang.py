import os
import re
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.txt")
RIWAYAT_GUDANG_FILE = os.path.join(BASE_DIR, "riwayat_gudang.txt")
RIWAYAT_TRANSAKSI_FILE = os.path.join(BASE_DIR, "riwayat_transaksi.txt")
KATEGORI_FILE = os.path.join(BASE_DIR, "kategori.txt")

data_barang = {}
keranjang = []
kategori_by_id = {}
kategori_by_name = {}
next_kategori_id = 1
current_user = ""

pengulangan = False
kasir = False
login = True

def insertion_sort(arr, left, right, key_func, reverse=False):
    for i in range(left + 1, right + 1):
        temp = arr[i]
        j = i - 1
        while j >= left:
            cond = (key_func(arr[j]) < key_func(temp)) if reverse else (key_func(arr[j]) > key_func(temp))
            if cond:
                arr[j + 1] = arr[j]
                j -= 1
            else:
                break
        arr[j + 1] = temp

def merge(arr, l, m, r, key_func, reverse=False):
    len1, len2 = m - l + 1, r - m
    left = arr[l:m + 1]
    right = arr[m + 1:r + 1]
    i = j = 0
    k = l
    while i < len1 and j < len2:
        cond = (key_func(left[i]) >= key_func(right[j])) if reverse else (key_func(left[i]) <= key_func(right[j]))
        if cond:
            arr[k] = left[i]
            i += 1
        else:
            arr[k] = right[j]
            j += 1
        k += 1
    while i < len1:
        arr[k] = left[i]
        i += 1
        k += 1
    while j < len2:
        arr[k] = right[j]
        j += 1
        k += 1

def tim_sort(arr, key_func=lambda x: x[0], reverse=False):
    RUN = 32
    n = len(arr)
    for i in range(0, n, RUN):
        insertion_sort(arr, i, min((i + RUN - 1), (n - 1)), key_func, reverse)
    size = RUN
    while size < n:
        for left in range(0, n, 2 * size):
            mid = min((left + size - 1), (n - 1))
            right = min((left + 2 * size - 1), (n - 1))
            if mid < right:
                merge(arr, left, mid, right, key_func, reverse)
        size = 2 * size
    return arr

def muat_kategori():
    global next_kategori_id
    kategori_by_id.clear()
    kategori_by_name.clear()
    max_id = 0
    if os.path.exists(KATEGORI_FILE):
        with open(KATEGORI_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(",")
                    if len(parts) == 2:
                        kid = int(parts[0].strip())
                        nama = parts[1].strip()
                        kategori_by_id[kid] = nama
                        kategori_by_name[nama.lower()] = kid
                        max_id = max(max_id, kid)
    next_kategori_id = max_id + 1

def simpan_kategori():
    with open(KATEGORI_FILE, "w", encoding="utf-8") as f:
        f.writelines(f"{kid},{kategori_by_id[kid]}\n" for kid in sorted(kategori_by_id.keys()))

def tambah_kategori(nama):
    global next_kategori_id
    nama = nama.strip()
    if not nama:
        return None
    if nama.lower() in kategori_by_name:
        return kategori_by_name[nama.lower()]
    kid = next_kategori_id
    kategori_by_id[kid] = nama
    kategori_by_name[nama.lower()] = kid
    next_kategori_id += 1
    simpan_kategori()
    return kid

def get_nama_kategori(kid):
    return kategori_by_id.get(kid, "Tanpa Kategori")

def id_ke_kategori(id_barang):
    return id_barang // 100

def generate_id(id_kategori):
    base = id_kategori * 100
    max_seq = 0
    for detail in data_barang.values():
        if id_ke_kategori(detail['id']) == id_kategori:
            seq = detail['id'] - base
            max_seq = max(max_seq, seq)
    if max_seq >= 99:
        return None
    return base + max_seq + 1

def hitung_transaksi_hari_ini():
    if not os.path.exists(RIWAYAT_TRANSAKSI_FILE) or os.path.getsize(RIWAYAT_TRANSAKSI_FILE) == 0:
        return 0
    hari_ini = datetime.now().strftime("%Y-%m-%d")
    jumlah = 0
    with open(RIWAYAT_TRANSAKSI_FILE, "r", encoding="utf-8") as f:
        for line in f:
            m = re.match(r"Tanggal\s*:\s*(\d{4}-\d{2}-\d{2})", line.strip())
            if m and m.group(1) == hari_ini:
                jumlah += 1
    return jumlah

def muat_data():
    data_barang.clear()
    muat_kategori()
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(",")
                    if len(parts) == 5:
                        id_barang, nama, stok, harga, status = [p.strip() for p in parts]
                        data_barang[nama] = {
                            "id": int(id_barang),
                            "stok": int(stok),
                            "harga": int(harga),
                            "status": status
                        }
                    elif len(parts) == 4:
                        id_barang, nama, stok, harga = [p.strip() for p in parts]
                        data_barang[nama] = {
                            "id": int(id_barang),
                            "stok": int(stok),
                            "harga": int(harga),
                            "status": "aktif"
                        }

def simpan_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        for nama, detail in data_barang.items():
            f.write(f"{detail['id']},{nama},{detail['stok']},{detail['harga']},{detail['status']}\n")

def get_flat_items():
    items = []
    for kid in sorted(kategori_by_id.keys()):
        kat_items = [(nama, detail) for nama, detail in data_barang.items()
                     if id_ke_kategori(detail['id']) == kid and detail.get('status', 'aktif') == 'aktif']
        kat_items.sort(key=lambda x: x[1]['id'])
        items.extend(kat_items)
    return items

def tampilkan_tabel_grouped(items=None, judul="DAFTAR BARANG"):
    if items is None:
        items = get_flat_items()
    else:
        items = [(nama, detail) for nama, detail in items if detail.get('status', 'aktif') == 'aktif']
    if not items:
        print("\n[!] Data barang masih kosong atau tidak ada barang aktif.")
        return
    print("\n==========================================================================")
    print(f"                         {judul}")
    print("==========================================================================")
    for kid in sorted(kategori_by_id.keys()):
        kat_items = [(nama, detail) for nama, detail in items if id_ke_kategori(detail['id']) == kid]
        if not kat_items:
            continue
        kat_items.sort(key=lambda x: x[1]['id'])
        print(f"\nKategori: {kategori_by_id[kid]} (ID: {kid}, Range: {kid*100+1}-{kid*100+99})")
        print("--------------------------------------------------------------------------")
        print(f"{'ID':<6} {'Nama Barang':<30} {'Stok':<8} {'Harga':<12}")
        print("--------------------------------------------------------------------------")
        for nama, detail in kat_items:
            harga_fmt = f"Rp{detail['harga']:,.0f}".replace(",", ".")
            print(f"{detail['id']:<6} {nama:<30} {detail['stok']:<8} {harga_fmt:<12}")
            if detail['stok'] < 5:
                print(f"     --> [!] Peringatan: Stok {nama} tersisa {detail['stok']}. Segera restock!")
    print("\n==========================================================================")

def cari_barang_linear(data_barang):
    if not data_barang:
        print("\n[!] Data barang masih kosong.")
        return
    print("\n==========================================================================")
    print("                         PENCARIAN BARANG (LINEAR SEARCH)                 ")
    print("==========================================================================")
    print("1. Cari berdasarkan ID barang")
    print("2. Cari berdasarkan nama barang")
    print("3. Cari berdasarkan ID kategori")
    print("0. Batal")
    print("==========================================================================")
    pilih = input("Masukkan pilihan pencarian (0-3): ").strip()
    if pilih == "0":
        return
    hasil = []
    if pilih == "1":
        try:
            id_cari = int(input("Masukkan ID barang yang dicari: "))
        except ValueError:
            print("\n[!] ID barang harus berupa angka!")
            return
        for nama, detail in data_barang.items():
            if detail.get('status', 'aktif') == 'aktif' and detail['id'] == id_cari:
                hasil.append((nama, detail))
                break
    elif pilih == "2":
        kata_kunci = input("Masukkan nama barang yang dicari: ").strip().lower()
        if not kata_kunci:
            print("\n[!] Nama barang tidak boleh kosong!")
            return
        for nama, detail in data_barang.items():
            if detail.get('status', 'aktif') == 'aktif' and kata_kunci in nama.lower():
                hasil.append((nama, detail))
    elif pilih == "3":
        try:
            kid = int(input("Masukkan ID kategori yang dicari: "))
        except ValueError:
            print("\n[!] ID kategori harus berupa angka!")
            return
        if kid not in kategori_by_id:
            print(f"\n[!] Kategori dengan ID {kid} tidak ditemukan.")
            return
        for nama, detail in data_barang.items():
            if detail.get('status', 'aktif') == 'aktif' and id_ke_kategori(detail['id']) == kid:
                hasil.append((nama, detail))
    else:
        print("\n[!] Pilihan tidak valid.")
        return
    if not hasil:
        print("\n[!] Barang tidak ditemukan.")
        return
    print("\n==========================================================================")
    print("                             HASIL PENCARIAN                              ")
    print("==========================================================================")
    print(f"{'ID':<6} {'Kategori':<20} {'Nama Barang':<30} {'Stok':<8} {'Harga':<12}")
    print("==========================================================================")
    for nama, detail in hasil:
        harga_fmt = f"Rp{detail['harga']:,.0f}".replace(",", ".")
        kat_nama = get_nama_kategori(id_ke_kategori(detail['id']))
        print(f"{detail['id']:<6} {kat_nama:<20} {nama:<30} {detail['stok']:<8} {harga_fmt:<12}")
    print("==========================================================================")

def summary_penjualan():
    if not os.path.exists(RIWAYAT_TRANSAKSI_FILE) or os.path.getsize(RIWAYAT_TRANSAKSI_FILE) == 0:
        print("\n[!] Belum ada riwayat transaksi.")
        return
    nama_bulan = {
        1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
        7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"
    }
    transaksi_bulanan = {}
    with open(RIWAYAT_TRANSAKSI_FILE, "r", encoding="utf-8") as file:
        isi = file.read()
    transaksi = isi.split("=== TRANSAKSI ===")
    for data in transaksi:
        if not data.strip():
            continue
        tanggal_match = re.search(r"Tanggal\s*:\s*(\d{4}-\d{2}-\d{2})", data)
        total_match = re.search(r"TOTAL:\s*Rp([\d.]+)", data)
        if tanggal_match and total_match:
            tanggal = datetime.strptime(tanggal_match.group(1), "%Y-%m-%d")
            total = int(total_match.group(1).replace(".", ""))
            bulan_key = tanggal.strftime("%Y-%m")
            tanggal_key = tanggal.day
            if bulan_key not in transaksi_bulanan:
                transaksi_bulanan[bulan_key] = {}
            if tanggal_key not in transaksi_bulanan[bulan_key]:
                transaksi_bulanan[bulan_key][tanggal_key] = 0
            transaksi_bulanan[bulan_key][tanggal_key] += total
    if not transaksi_bulanan:
        print("\n[!] Tidak ada data transaksi yang dapat dibaca.")
        return
    bulan_tersedia = sorted(transaksi_bulanan.keys())
    while True:
        print("\n==========================================================================")
        print("                         SUMMARY PENJUALAN")
        print("==========================================================================")
        print("Pilih bulan yang ingin dilihat:")
        print()
        for idx, bulan_key in enumerate(bulan_tersedia, start=1):
            tahun, bulan = map(int, bulan_key.split("-"))
            print(f"{idx}. {nama_bulan[bulan]} {tahun}")
        print("0. Kembali")
        print("==========================================================================")
        pilihan = input("Masukkan pilihan bulan: ").strip()
        if pilihan == "0":
            return
        try:
            nomor_bulan = int(pilihan)
            if nomor_bulan < 1 or nomor_bulan > len(bulan_tersedia):
                print("\n[!] Pilihan bulan tidak valid.")
                continue
            bulan_dipilih = bulan_tersedia[nomor_bulan - 1]
            tahun, bulan = map(int, bulan_dipilih.split("-"))
            data_harian = transaksi_bulanan[bulan_dipilih]
            print("\n==========================================================================")
            print(f"                    PENJUALAN {nama_bulan[bulan].upper()} {tahun}")
            print("==========================================================================")
            print(f"{'Tanggal':<25} {'Total Penjualan':>20}")
            print("--------------------------------------------------------------------------")
            total_bulan = 0
            for tanggal in sorted(data_harian.keys()):
                total_hari = data_harian[tanggal]
                total_bulan += total_hari
                total_fmt = f"Rp{total_hari:,.0f}".replace(",", ".")
                print(f"{tanggal:02d} {nama_bulan[bulan]:<18} {total_fmt:>20}")
            print("--------------------------------------------------------------------------")
            total_bulan_fmt = f"Rp{total_bulan:,.0f}".replace(",", ".")
            print(f"{'TOTAL BULAN':<25} {total_bulan_fmt:>20}")
            print("==========================================================================")
            input("\nTekan Enter untuk kembali...")
        except ValueError:
            print("\n[!] Masukkan angka yang valid.")

def tambah_barang():
    nama_barang = input("Masukkan nama barang: ").strip()
    if not nama_barang:
        print("\n[!] Nama barang tidak boleh kosong!")
        return
    if nama_barang in data_barang:
        status = data_barang[nama_barang].get('status', 'aktif')
        if status == 'aktif':
            print(f"\n[!] Barang '{nama_barang}' sudah ada. Gunakan menu Restok untuk menambah stok.")
        else:
            print(f"\n[!] Barang '{nama_barang}' sudah ada namun berstatus terhapus. Silakan cek Recycle Bin untuk restore atau hapus permanen.")
        return
    if not kategori_by_id:
        print("\n[!] Belum ada kategori. Silakan tambah kategori baru.")
        kat_baru = input("Masukkan nama kategori baru: ").strip()
        if not kat_baru:
            print("\n[!] Nama kategori tidak boleh kosong!")
            return
        id_kat = tambah_kategori(kat_baru)
    else:
        print("\nPilih Kategori:")
        for kid in sorted(kategori_by_id.keys()):
            print(f"{kid}. {kategori_by_id[kid]} (Range ID: {kid*100+1}-{kid*100+99})")
        print("0. Tambah Kategori Baru")
        pilih_kat = input("Masukkan pilihan kategori: ").strip()
        if pilih_kat == "0":
            kat_baru = input("Masukkan nama kategori baru: ").strip()
            if not kat_baru:
                print("\n[!] Nama kategori tidak boleh kosong!")
                return
            if kat_baru.lower() in kategori_by_name:
                print(f"\n[!] Kategori '{kat_baru}' sudah ada dengan ID {kategori_by_name[kat_baru.lower()]}.")
                return
            id_kat = tambah_kategori(kat_baru)
        else:
            try:
                id_kat = int(pilih_kat)
                if id_kat not in kategori_by_id:
                    print("\n[!] Pilihan kategori tidak valid.")
                    return
            except ValueError:
                print("\n[!] Masukkan angka yang valid.")
                return
    try:
        jumlah_barang = int(input("Masukkan jumlah barang: "))
        harga_barang = int(input("Masukkan harga barang: "))
    except ValueError:
        print("\n[!] Error: Jumlah dan harga harus berupa angka!")
        return
    id_barang = generate_id(id_kat)
    if id_barang is None:
        print(f"\n[!] Range ID kategori {kategori_by_id[id_kat]} sudah penuh (maks 99 barang per kategori).")
        return
    data_barang[nama_barang] = {
        "id": id_barang,
        "stok": jumlah_barang,
        "harga": harga_barang,
        "status": "aktif"
    }
    simpan_data()
    with open(RIWAYAT_GUDANG_FILE, "a", encoding="utf-8") as r_file:
        r_file.write(f"[TAMBAH] Barang Baru: {nama_barang} | ID: {id_barang} | Kategori: {kategori_by_id[id_kat]} (ID: {id_kat}) | Jumlah: {jumlah_barang} | Harga: Rp{harga_barang:,.0f}\n".replace(",", "."))
    print(f"\n[V] Barang '{nama_barang}' berhasil ditambahkan dengan ID {id_barang}!")

def restok_barang():
    if not data_barang:
        print("\n[!] Data barang masih kosong. Silakan tambah barang baru.")
        tambah_barang()
        return
    active_items = [(nama, detail) for nama, detail in data_barang.items() if detail.get('status', 'aktif') == 'aktif']
    if not active_items:
        print("\n[!] Tidak ada barang aktif. Silakan tambah barang baru.")
        tambah_barang()
        return
    tampilkan_tabel_grouped(judul="PILIH BARANG UNTUK RESTOK")
    print("0. Tambah Barang Baru")
    try:
        id_input = int(input("\nMasukkan ID barang yang ingin di-restock (0 untuk tambah baru): "))
    except ValueError:
        print("\n[!] Error: Masukkan angka yang valid!")
        return
    if id_input == 0:
        tambah_barang()
        return
    nama_target = None
    for nama, detail in data_barang.items():
        if detail.get('status', 'aktif') == 'aktif' and detail['id'] == id_input:
            nama_target = nama
            break
    if nama_target is not None:
        try:
            jumlah_restock = int(input(f"Masukkan jumlah stok tambahan untuk '{nama_target}': "))
            if jumlah_restock <= 0:
                print("\n[!] Jumlah restock harus lebih dari 0.")
                return
            data_barang[nama_target]['stok'] += jumlah_restock
            simpan_data()
            with open(RIWAYAT_GUDANG_FILE, "a", encoding="utf-8") as r_file:
                r_file.write(f"[RESTOK] {nama_target} +{jumlah_restock} (Total Stok: {data_barang[nama_target]['stok']})\n")
            print(f"\n[V] Restock berhasil! Stok {nama_target} sekarang: {data_barang[nama_target]['stok']}")
        except ValueError:
            print("\n[!] Error: Masukkan angka yang valid!")
    else:
        print("\n[!] ID barang tidak ditemukan atau barang sudah terhapus.")

def ubah_barang():
    if not data_barang:
        print("\n[!] Data barang masih kosong.")
        return
    active_items = [(nama, detail) for nama, detail in data_barang.items() if detail.get('status', 'aktif') == 'aktif']
    if not active_items:
        print("\n[!] Tidak ada barang aktif.")
        return
    tampilkan_tabel_grouped(judul="PILIH BARANG UNTUK DIUBAH")
    try:
        id_input = int(input("\nMasukkan ID barang yang ingin diubah: "))
    except ValueError:
        print("\n[!] Error: Masukkan angka yang valid!")
        return
    nama_lama = None
    for nama, detail in data_barang.items():
        if detail.get('status', 'aktif') == 'aktif' and detail['id'] == id_input:
            nama_lama = nama
            break
    if nama_lama is not None:
        detail_lama = data_barang[nama_lama]
        id_kat_lama = id_ke_kategori(detail_lama['id'])
        nama_baru = input(f"Masukkan nama barang baru (kosongkan jika tetap '{nama_lama}'): ").strip()
        if not nama_baru:
            nama_baru = nama_lama
        print("\nPilih Kategori:")
        for kid in sorted(kategori_by_id.keys()):
            print(f"{kid}. {kategori_by_id[kid]}")
        print("0. Tambah Kategori Baru")
        pilih_kat = input(f"Pilihan kategori (kosongkan jika tetap '{get_nama_kategori(id_kat_lama)}'): ").strip()
        if not pilih_kat:
            id_kat = id_kat_lama
        elif pilih_kat == "0":
            kat_baru = input("Masukkan nama kategori baru: ").strip()
            if not kat_baru:
                print("\n[!] Nama kategori tidak boleh kosong!")
                return
            if kat_baru.lower() in kategori_by_name:
                id_kat = kategori_by_name[kat_baru.lower()]
            else:
                id_kat = tambah_kategori(kat_baru)
        else:
            try:
                id_kat = int(pilih_kat)
                if id_kat not in kategori_by_id:
                    print("\n[!] Pilihan kategori tidak valid.")
                    return
            except ValueError:
                print("\n[!] Masukkan angka yang valid.")
                return
        try:
            jumlah_baru = int(input("Masukkan jumlah barang baru: "))
            harga_baru = int(input("Masukkan harga barang baru: "))
        except ValueError:
            print("\n[!] Error: Masukkan input angka yang valid!")
            return
        if nama_baru != nama_lama:
            if nama_baru in data_barang:
                print("\n[!] Nama barang baru sudah ada.")
                return
            del data_barang[nama_lama]
        if id_kat != id_kat_lama:
            id_barang_baru = generate_id(id_kat)
            if id_barang_baru is None:
                print(f"\n[!] Range ID kategori {kategori_by_id[id_kat]} sudah penuh.")
                if nama_baru != nama_lama:
                    data_barang[nama_lama] = detail_lama
                return
        else:
            id_barang_baru = detail_lama['id']
        data_barang[nama_baru] = {
            "id": id_barang_baru,
            "stok": jumlah_baru,
            "harga": harga_baru,
            "status": "aktif"
        }
        simpan_data()
        print("\n[V] Data barang berhasil diperbarui.")
    else:
        print("\n[!] ID barang tidak ditemukan atau barang sudah terhapus.")

def hapus_barang():
    if not data_barang:
        print("\n[!] Data barang masih kosong.")
        return
    active_items = [(nama, detail) for nama, detail in data_barang.items() if detail.get('status', 'aktif') == 'aktif']
    if not active_items:
        print("\n[!] Tidak ada barang aktif yang bisa dihapus.")
        return
    tampilkan_tabel_grouped(judul="PILIH BARANG UNTUK DIHAPUS")
    try:
        id_input = int(input("\nMasukkan ID barang yang ingin dihapus: "))
    except ValueError:
        print("\n[!] Error: Masukkan angka yang valid!")
        return
    nama_target = None
    for nama, detail in data_barang.items():
        if detail.get('status', 'aktif') == 'aktif' and detail['id'] == id_input:
            nama_target = nama
            break
    if nama_target is not None:
        data_barang[nama_target]['status'] = 'terhapus'
        simpan_data()
        with open(RIWAYAT_GUDANG_FILE, "a", encoding="utf-8") as r_file:
            r_file.write(f"[HAPUS] {nama_target} (ID: {id_input}) dipindahkan ke Recycle Bin\n")
        print(f"\n[V] Barang '{nama_target}' berhasil dipindahkan ke Recycle Bin.")
    else:
        print("\n[!] ID barang tidak ditemukan atau barang sudah terhapus.")

def tampilkan_barang_terhapus():
    deleted_items = [(nama, detail) for nama, detail in data_barang.items() if detail.get('status') == 'terhapus']
    if not deleted_items:
        print("\n[!] Tidak ada barang di Recycle Bin.")
        return
    print("\n==========================================================================")
    print("                         RECYCLE BIN (BARANG TERHAPUS)                    ")
    print("==========================================================================")
    print(f"{'ID':<6} {'Nama Barang':<30} {'Stok':<8} {'Harga':<12}")
    print("--------------------------------------------------------------------------")
    for nama, detail in deleted_items:
        harga_fmt = f"Rp{detail['harga']:,.0f}".replace(",", ".")
        print(f"{detail['id']:<6} {nama:<30} {detail['stok']:<8} {harga_fmt:<12}")
    print("==========================================================================")

def restore_barang():
    deleted_items = [(nama, detail) for nama, detail in data_barang.items() if detail.get('status') == 'terhapus']
    if not deleted_items:
        print("\n[!] Tidak ada barang di Recycle Bin.")
        return
    tampilkan_barang_terhapus()
    try:
        id_input = int(input("\nMasukkan ID barang yang ingin di-restore: "))
    except ValueError:
        print("\n[!] Error: Masukkan angka yang valid!")
        return
    nama_target = None
    for nama, detail in data_barang.items():
        if detail.get('status') == 'terhapus' and detail['id'] == id_input:
            nama_target = nama
            break
    if nama_target is not None:
        data_barang[nama_target]['status'] = 'aktif'
        simpan_data()
        with open(RIWAYAT_GUDANG_FILE, "a", encoding="utf-8") as r_file:
            r_file.write(f"[RESTORE] {nama_target} (ID: {id_input}) dikembalikan dari Recycle Bin\n")
        print(f"\n[V] Barang '{nama_target}' berhasil di-restore.")
    else:
        print("\n[!] ID barang tidak ditemukan di Recycle Bin.")

def hapus_permanen_barang():
    deleted_items = [(nama, detail) for nama, detail in data_barang.items() if detail.get('status') == 'terhapus']
    if not deleted_items:
        print("\n[!] Tidak ada barang di Recycle Bin.")
        return
    tampilkan_barang_terhapus()
    try:
        id_input = int(input("\nMasukkan ID barang yang ingin dihapus permanen: "))
    except ValueError:
        print("\n[!] Error: Masukkan angka yang valid!")
        return
    nama_target = None
    for nama, detail in data_barang.items():
        if detail.get('status') == 'terhapus' and detail['id'] == id_input:
            nama_target = nama
            break
    if nama_target is not None:
        konfirmasi = input(f"Apakah Anda yakin ingin menghapus permanen '{nama_target}'? (y/n): ").strip().lower()
        if konfirmasi == 'y':
            del data_barang[nama_target]
            simpan_data()
            with open(RIWAYAT_GUDANG_FILE, "a", encoding="utf-8") as r_file:
                r_file.write(f"[HAPUS PERMANEN] {nama_target} (ID: {id_input}) dihapus permanen\n")
            print(f"\n[V] Barang '{nama_target}' berhasil dihapus permanen.")
        else:
            print("\n[!] Penghapusan permanen dibatalkan.")
    else:
        print("\n[!] ID barang tidak ditemukan di Recycle Bin.")

def menu_recycle_bin():
    while True:
        print("\n==========================================================================")
        print("                               RECYCLE BIN                                ")
        print("==========================================================================")
        print("1. Lihat Barang Terhapus")
        print("2. Restore Barang")
        print("3. Hapus Permanen")
        print("0. Kembali")
        print("==========================================================================")
        pilihan = input("Masukkan pilihan (0-3): ").strip()
        if pilihan == "1":
            tampilkan_barang_terhapus()
        elif pilihan == "2":
            restore_barang()
        elif pilihan == "3":
            hapus_permanen_barang()
        elif pilihan == "0":
            break
        else:
            print("\n[!] Pilihan tidak valid.")

def checkout():
    if not keranjang:
        print("\n[!] Keranjang belanja kosong. Silakan tambah barang terlebih dahulu.")
        return
    waktu_transaksi = datetime.now()
    waktu_str = waktu_transaksi.strftime("%Y-%m-%d %H:%M")
    total_harga = 0
    print("\n==========================================================================")
    print("                             STRUK PEMBELIAN                              ")
    print("==========================================================================")
    print(f"Tanggal     : {waktu_str}")
    print(f"Kasir       : {current_user}")
    print(f"{'ID':<6} {'Nama Barang':<30} {'Jumlah':<8} {'Subtotal':<15}")
    print("==========================================================================")
    for item in keranjang:
        subtotal = item['jumlah'] * item['harga']
        total_harga += subtotal
        subtotal_fmt = f"Rp{subtotal:,.0f}".replace(",", ".")
        print(f"{item['id']:<6} {item['nama']:<30} {item['jumlah']:<8} {subtotal_fmt:<15}")
    total_fmt = f"Rp{total_harga:,.0f}".replace(",", ".")
    print("==========================================================================")
    print(f"TOTAL HARGA: {total_fmt}")
    print("==========================================================================")
    print("\nPilih Metode Pembayaran:")
    print("1. Cash")
    print("2. Debit")
    print("3. QRIS")
    metode_pilih = input("Masukkan pilihan (1-3): ").strip()
    if metode_pilih == "1":
        metode = "Cash"
    elif metode_pilih == "2":
        metode = "Debit"
    elif metode_pilih == "3":
        metode = "QRIS"
    else:
        print("\n[!] Metode pembayaran tidak valid.")
        return
    if metode == "Cash":
        try:
            uang_dibayarkan = int(input("\nMasukkan jumlah uang yang dibayarkan: Rp"))
            if uang_dibayarkan < total_harga:
                print("\n[!] Uang pembayaran kurang! Pembatalan checkout.")
                return
            kembalian = uang_dibayarkan - total_harga
        except ValueError:
            print("\n[!] Input nominal uang tidak valid!")
            return
    else:
        uang_dibayarkan = total_harga
        kembalian = 0
        print(f"\n[V] Pembayaran via {metode} sebesar {total_fmt}.")
    for item in keranjang:
        if item['nama'] in data_barang and data_barang[item['nama']].get('status', 'aktif') == 'aktif':
            data_barang[item['nama']]['stok'] -= item['jumlah']
    simpan_data()
    nomor_urut = hitung_transaksi_hari_ini() + 1
    kode_transaksi = f"SMK{nomor_urut:03d}"
    log_transaksi = "=== TRANSAKSI ===\n"
    log_transaksi += f"ID Transaksi: {kode_transaksi}{waktu_transaksi.strftime('%Y%m%d%H%M%S')}\n"
    log_transaksi += f"Tanggal : {waktu_str}\n"
    log_transaksi += f"Kasir   : {current_user}\n"
    log_transaksi += f"Metode  : {metode}\n"
    log_transaksi += "----------------------------------------\n"
    for item in keranjang:
        subtotal = item['jumlah'] * item['harga']
        subtotal_fmt = f"Rp{subtotal:,.0f}".replace(",", ".")
        log_transaksi += f"- [{item['id']}] {item['nama']} x{item['jumlah']} = {subtotal_fmt}\n"
    total_fmt_log = f"Rp{total_harga:,.0f}".replace(",", ".")
    dibayar_fmt = f"Rp{uang_dibayarkan:,.0f}".replace(",", ".")
    kembali_fmt = f"Rp{kembalian:,.0f}".replace(",", ".")
    log_transaksi += f"TOTAL: {total_fmt_log}\n"
    log_transaksi += f"Dibayar: {dibayar_fmt}\n"
    log_transaksi += f"Kembalian: {kembali_fmt}\n"
    log_transaksi += "----------------------------------------\n\n"
    with open(RIWAYAT_TRANSAKSI_FILE, "a", encoding="utf-8") as riwayat_file:
        riwayat_file.write(log_transaksi)
    keranjang.clear()
    print("\n[V] Pembayaran berhasil! Stok telah diperbarui dan riwayat disimpan.")
    print("\n==========================================================================")
    print("                             STRUK PEMBELIAN                              ")
    print("==========================================================================")
    print(f"ID Transaksi    : {kode_transaksi}{waktu_transaksi.strftime('%Y%m%d%H%M%S')}")
    print(f"Tanggal         : {waktu_str}")
    print(f"Kasir           : {current_user}")
    print(f"Metode          : {metode}")
    print(f"TOTAL HARGA     : {total_fmt}")
    print(f"UANG DIBAYARKAN : Rp{uang_dibayarkan:,.0f}".replace(",", "."))
    print(f"KEMBALIAN       : Rp{kembalian:,.0f}".replace(",", "."))
    print("==========================================================================")
    print("            Terima kasih telah berbelanja di SMKMART!                    ")
    print("==========================================================================")

while login:
    pengulangan = False
    kasir = False

    print("==========================================================================")
    print("              LOGIN SISTEM PENGELOLAAN BARANG SMKMART")
    print("==========================================================================")
    print("Masukkan username dan password untuk masuk ke sistem. (Default: admin/kasir)")
    print("(Keluar Aplikasi: 0)")
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    if username == "0" and password == "0":
        sys.exit()

    login_berhasil = False
    role_login = ""
    with open("User.txt", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                parts = [p.strip() for p in line.strip().split(",")]
                if len(parts) == 3:
                    user, pwd, role = parts
                    if user == username and pwd == password:
                        role_login = role
                        login_berhasil = True
                        break

    if not login_berhasil:
        print("\n[!] Username atau password salah!")
        continue

    current_user = username
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"\n[V] Login berhasil! Selamat datang, {username}")
    print(f"Peran Anda: {role_login}")

    if role_login.strip().lower() == "admin":
        pengulangan = True
    elif role_login.strip().lower() == "kasir":
        kasir = True

    muat_data()

    print("==========================================================================")
    print("             APLIKASI SISTEM PENGELOLAAN BARANG SMKMART                  ")
    print("==========================================================================")

    while pengulangan:
        print("\n==========================================================================")
        print("               MENU UTAMA SISTEM PENGELOLAAN BARANG SMKMART               ")
        print("==========================================================================")
        print("1. Tambah Barang")
        print("2. Lihat Stok Barang (per Kategori)")
        print("3. Restok Barang")
        print("4. Riwayat Gudang")
        print("5. Ubah Barang")
        print("6. Hapus Barang")
        print("7. Cari Barang")
        print("8. Summary Penjualan")
        print("9. Recycle Bin")
        print("10. Kembali ke halaman login")
        print("==========================================================================")

        pilihan = input("Masukkan pilihan menu (1-10): ").strip()

        if pilihan == "1":
            tambah_barang()
        elif pilihan == "2":
            if not data_barang:
                print("\n[!] Data barang masih kosong.")
                continue
            tampilkan_tabel_grouped()
        elif pilihan == "3":
            restok_barang()
        elif pilihan == "4":
            if not os.path.exists(RIWAYAT_GUDANG_FILE) or os.path.getsize(RIWAYAT_GUDANG_FILE) == 0:
                print("\n[!] Belum ada riwayat gudang.")
                continue
            print("\n==========================================================================")
            print("                               RIWAYAT GUDANG                             ")
            print("==========================================================================")
            with open(RIWAYAT_GUDANG_FILE, "r", encoding="utf-8") as file:
                print(file.read().strip())
            print("==========================================================================")
        elif pilihan == "5":
            ubah_barang()
        elif pilihan == "6":
            hapus_barang()
        elif pilihan == "7":
            cari_barang_linear(data_barang)
        elif pilihan == "8":
            summary_penjualan()
        elif pilihan == "9":
            menu_recycle_bin()
        elif pilihan == "10":
            print("\nKembali ke halaman login...")
            pengulangan = False
        else:
            print("\n[!] Pilihan tidak valid. Silakan masukkan pilihan angka 1-10.")

    while kasir:
        print("\n==========================================================================")
        print("                          SISTEM KASIR SMKMART                            ")
        print("==========================================================================")
        print("1. Tambah Barang ke Keranjang")
        print("2. Lihat Keranjang")
        print("3. Hapus Barang dari Keranjang")
        print("4. Checkout")
        print("5. Riwayat Transaksi")
        print("6. Cari Barang")
        print("7. Summary Penjualan")
        print("8. Kembali ke Halaman Login")
        print("==========================================================================")

        pilihan_kasir = input("Masukkan pilihan menu (1-8): ").strip()

        if pilihan_kasir == "1":
            if not data_barang:
                print("\n[!] Stok barang di data masih kosong.")
                continue
            active_items = [(nama, detail) for nama, detail in data_barang.items() if detail.get('status', 'aktif') == 'aktif']
            if not active_items:
                print("\n[!] Tidak ada barang aktif yang bisa dibeli.")
                continue
            tampilkan_tabel_grouped(judul="PILIH BARANG UNTUK DIBELI")
            try:
                id_input = int(input("Masukkan ID barang yang ingin dibeli: "))
            except ValueError:
                print("\n[!] Error: Masukkan angka yang valid!")
                continue
            target_nama = None
            for nama, detail in data_barang.items():
                if detail.get('status', 'aktif') == 'aktif' and detail['id'] == id_input:
                    target_nama = nama
                    break
            if target_nama is not None:
                stok_tersedia = data_barang[target_nama]["stok"]
                harga_satuan = data_barang[target_nama]["harga"]
                try:
                    jumlah_beli = int(input(f"Masukkan jumlah | {target_nama} | yang ingin dibeli: "))
                except ValueError:
                    print("\n[!] Error: Masukkan angka yang valid!")
                    continue
                if jumlah_beli <= 0:
                    print("\n[!] Jumlah pembelian harus lebih dari 0.")
                elif jumlah_beli <= stok_tersedia:
                    keranjang.append({
                        "id": data_barang[target_nama]["id"],
                        "nama": target_nama,
                        "jumlah": jumlah_beli,
                        "harga": harga_satuan
                    })
                    print(f"\n[V] {jumlah_beli} {target_nama} berhasil ditambahkan ke keranjang.")
                else:
                    print(f"\n[!] Stok {target_nama} tidak mencukupi (Tersisa: {stok_tersedia}).")
            else:
                print("\n[!] ID barang tidak ditemukan atau barang sudah terhapus.")
        elif pilihan_kasir == "2":
            if not keranjang:
                print("\n[!] Keranjang belanja masih kosong.")
                continue
            print("\n==========================================================================")
            print("                             KERANJANG BELANJA                            ")
            print("==========================================================================")
            print(f"{'ID':<6} {'Nama Barang':<30} {'Jumlah':<8} {'Harga Satuan':<15}")
            print("==========================================================================")
            for item in keranjang:
                harga_fmt = f"Rp{item['harga']:,.0f}".replace(",", ".")
                print(f"{item['id']:<6} {item['nama']:<30} {item['jumlah']:<8} {harga_fmt:<15}")
            print("==========================================================================")
        elif pilihan_kasir == "3":
            if not keranjang:
                print("\n[!] Keranjang belanja kosong, tidak ada yang bisa dihapus.")
                continue
            print("\n==========================================================================")
            print("                             KERANJANG BELANJA                            ")
            print("==========================================================================")
            print(f"{'ID':<6} {'Nama Barang':<30} {'Jumlah':<8} {'Harga Satuan':<15}")
            print("==========================================================================")
            for item in keranjang:
                harga_fmt = f"Rp{item['harga']:,.0f}".replace(",", ".")
                print(f"{item['id']:<6} {item['nama']:<30} {item['jumlah']:<8} {harga_fmt:<15}")
            print("==========================================================================")
            try:
                id_hapus = int(input("Masukkan ID barang yang ingin dihapus dari keranjang: "))
            except ValueError:
                print("\n[!] Error: Masukkan angka yang valid!")
                continue
            target_idx = -1
            for i, item in enumerate(keranjang):
                if item['id'] == id_hapus:
                    target_idx = i
                    break
            if target_idx != -1:
                removed = keranjang.pop(target_idx)
                print(f"\n[V] '{removed['nama']}' (ID: {removed['id']}) berhasil dihapus dari keranjang.")
            else:
                print("\n[!] ID barang tidak ditemukan di keranjang.")
        elif pilihan_kasir == "4":
            checkout()
        elif pilihan_kasir == "5":
            if not os.path.exists(RIWAYAT_TRANSAKSI_FILE) or os.path.getsize(RIWAYAT_TRANSAKSI_FILE) == 0:
                print("\n[!] Belum ada riwayat transaksi.")
                continue
            print("\n==========================================================================")
            print("                             RIWAYAT TRANSAKSI                            ")
            print("==========================================================================")
            with open(RIWAYAT_TRANSAKSI_FILE, "r", encoding="utf-8") as file:
                print(file.read().strip())
            print("==========================================================================")
        elif pilihan_kasir == "6":
            cari_barang_linear(data_barang)
        elif pilihan_kasir == "7":
            summary_penjualan()
        elif pilihan_kasir == "8":
            print("\nKembali ke halaman login...")
            kasir = False
        else:
            print("\n[!] Pilihan tidak valid. Silakan pilih 1-8.")
