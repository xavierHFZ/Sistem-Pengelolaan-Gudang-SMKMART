import getpass
import os
import re
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.txt")
FIFO_FILE = os.path.join(BASE_DIR, "batch_stok.txt")
RIWAYAT_GUDANG_FILE = os.path.join(BASE_DIR, "riwayat_gudang.txt")
RIWAYAT_TRANSAKSI_FILE = os.path.join(BASE_DIR, "riwayat_transaksi.txt")
KATEGORI_FILE = os.path.join(BASE_DIR, "kategori.txt")
USER_FILE = os.path.join(BASE_DIR, "User.txt")
DATA_HARGA = os.path.join(BASE_DIR, "Harga asli.txt")

data_barang = {}
batch_stok = []
data_harga = {}
keranjang = []
kategori_by_id = {}
kategori_by_name = {}
next_kategori_id = 1
current_user = ""

admin_menu = False
Gudang = False  # untuk admin gudang
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
                        try:
                            kid = int(parts[0].strip())
                        except ValueError:
                            print(f"[!] Baris kategori dilewati karena ID tidak valid: {line.strip()}")
                            continue
                        nama = parts[1].strip()
                        if kid <= 0 or not nama:
                            print(f"[!] Baris kategori dilewati karena datanya kosong/tidak valid: {line.strip()}")
                            continue
                        kategori_by_id[kid] = nama
                        kategori_by_name[nama.lower()] = kid
                        max_id = max(max_id, kid)
    next_kategori_id = max_id + 1

def simpan_kategori():
    with open(KATEGORI_FILE, "w", encoding="utf-8") as f:
        f.writelines(
            f"{kid},{kategori_by_id[kid]}\n" for kid in sorted(kategori_by_id)
        )

def tambah_kategori(nama):
    global next_kategori_id
    nama = nama.strip()
    if not nama or "," in nama:
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
    data_harga.clear()
    muat_kategori()
    if os.path.exists(DATA_HARGA):
        with open(DATA_HARGA, "r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    parts = [p.strip() for p in line.strip().split(",")]
                    if len(parts) != 3:
                        print(f"[!] Baris riwayat harga dilewati karena formatnya salah: {line.strip()}")
                        continue
                    try:
                        id_barang, urutan, harga_asli = map(int, parts)
                    except ValueError:
                        print(f"[!] Baris riwayat harga dilewati karena berisi nilai bukan angka: {line.strip()}")
                        continue
                    if id_barang <= 0 or urutan <= 0 or harga_asli < 0:
                        print(f"[!] Baris riwayat harga dilewati karena nilainya tidak valid: {line.strip()}")
                        continue
                    data_harga.setdefault(id_barang, []).append({
                        "urutan": urutan,
                        "harga": harga_asli,
                    })

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(",")
                    if len(parts) == 8:
                        id_barang, nama, stok, harga, status, batas_restock, harga_beli, barcode = [p.strip() for p in parts]
                    elif len(parts) == 7:
                        id_barang, nama, stok, harga, status, batas_restock, kolom_tambahan = [p.strip() for p in parts]
                        if kolom_tambahan.isdigit() and len(kolom_tambahan) not in {8, 12, 13, 14}:
                            harga_beli = kolom_tambahan
                            barcode = ""
                        else:
                            harga_beli = ""
                            barcode = kolom_tambahan
                    elif len(parts) == 6:
                        id_barang, nama, stok, harga, status, batas_restock = [p.strip() for p in parts]
                        barcode = ""
                        harga_beli = ""
                    elif len(parts) == 5:
                        id_barang, nama, stok, harga, status = [p.strip() for p in parts]
                        batas_restock = 5
                        barcode = ""
                        harga_beli = ""
                    elif len(parts) == 4:
                        id_barang, nama, stok, harga = [p.strip() for p in parts]
                        status = "aktif"
                        batas_restock = 5
                        barcode = ""
                        harga_beli = ""
                    else:
                        continue
                    try:
                        data_barang[nama] = {
                            "id": int(id_barang),
                            "stok": int(stok),
                            "harga": int(harga),
                            "status": status,
                            "batas_restock": int(batas_restock),
                            "barcode": barcode,
                            "hargaBeli": int(harga_beli) if harga_beli else None,
                        }
                    except ValueError:
                        print(f"[!] Baris data barang dilewati karena format angka tidak valid: {line.strip()}")
    muat_batch_stok()

def simpan_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        for nama, detail in data_barang.items():
            harga_beli = detail.get("hargaBeli")
            f.write(
                f"{detail['id']},{nama},{detail['stok']},{detail['harga']},"
                f"{detail['status']},{detail.get('batas_restock', 5)},"
                f"{harga_beli if harga_beli is not None else ''},"
                f"{detail.get('barcode', '')}\n"
            )

def simpan_batch_stok():
    with open(FIFO_FILE, "w", encoding="utf-8") as file:
        for batch in batch_stok:
            modal = "" if batch["harga_modal"] is None else batch["harga_modal"]
            file.write(
                f"{batch['id_barang']},{batch['urutan']},{batch['tanggal']}"
                f",{batch['sisa']},{modal}\n"
            )

def muat_batch_stok():
    batch_stok.clear()
    if os.path.exists(FIFO_FILE):
        with open(FIFO_FILE, "r", encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue
                parts = [part.strip() for part in line.strip().split(",")]
                if len(parts) != 5:
                    print(f"[!] Baris batch FIFO dilewati karena formatnya salah: {line.strip()}")
                    continue
                try:
                    id_barang, urutan, tanggal, sisa = int(parts[0]), int(parts[1]), parts[2], int(parts[3])
                    harga_modal = int(parts[4]) if parts[4] else None
                except ValueError:
                    print(f"[!] Baris batch FIFO dilewati karena berisi nilai tidak valid: {line.strip()}")
                    continue
                if id_barang <= 0 or urutan <= 0 or sisa <= 0 or (harga_modal is not None and harga_modal < 0):
                    print(f"[!] Baris batch FIFO dilewati karena nilainya tidak valid: {line.strip()}")
                    continue
                batch_stok.append({
                    "id_barang": id_barang,
                    "urutan": urutan,
                    "tanggal": tanggal,
                    "sisa": sisa,
                    "harga_modal": harga_modal,
                })
        for detail in data_barang.values():
            stok_batch = jumlah_stok_batch(detail["id"])
            if stok_batch != detail["stok"]:
                print(
                    f"[!] Stok FIFO ID {detail['id']} ({stok_batch}) berbeda dari data barang "
                    f"({detail['stok']}). Periksa batch sebelum restok, ubah stok, atau checkout."
                )
        return

    for detail in data_barang.values():
        stok = detail["stok"]
        if stok <= 0:
            continue
        id_barang = detail["id"]
        riwayat = data_harga.get(id_barang, [])
        urutan = max((item["urutan"] for item in riwayat), default=0) + 1
        batch_stok.append({
            "id_barang": id_barang,
            "urutan": urutan,
            "tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sisa": stok,
            "harga_modal": detail.get("hargaBeli"),
        })
    simpan_batch_stok()

def jumlah_stok_batch(id_barang):
    return sum(batch["sisa"] for batch in batch_stok if batch["id_barang"] == id_barang)

def rencana_fifo(id_barang, jumlah):
    sisa_diminta = jumlah
    rencana = []
    modal = 0
    modal_lengkap = True
    batch_tertua = sorted(
        (
            (index, batch)
            for index, batch in enumerate(batch_stok)
            if batch["id_barang"] == id_barang
        ),
        key=lambda item: (item[1]["urutan"], item[1]["tanggal"]),
    )
    for index, batch in batch_tertua:
        ambil = min(sisa_diminta, batch["sisa"])
        if ambil <= 0:
            continue
        rencana.append((index, ambil))
        if batch["harga_modal"] is None:
            modal_lengkap = False
        elif modal_lengkap:
            modal += ambil * batch["harga_modal"]
        sisa_diminta -= ambil
        if sisa_diminta == 0:
            break
    if sisa_diminta:
        return None, None
    return rencana, modal if modal_lengkap else None

def terapkan_rencana_fifo(rencana):
    for index, jumlah in rencana:
        batch_stok[index]["sisa"] -= jumlah
    batch_stok[:] = [batch for batch in batch_stok if batch["sisa"] > 0]

def terapkan_banyak_rencana_fifo(daftar_rencana):
    for rencana in daftar_rencana:
        for index, jumlah in rencana:
            batch_stok[index]["sisa"] -= jumlah
    batch_stok[:] = [batch for batch in batch_stok if batch["sisa"] > 0]

def tambah_batch_stok(id_barang, jumlah, harga_modal):
    riwayat = data_harga.get(id_barang, [])
    urutan_riwayat = max((item["urutan"] for item in riwayat), default=0)
    urutan_batch = max(
        (batch["urutan"] for batch in batch_stok if batch["id_barang"] == id_barang),
        default=0,
    )
    urutan = max(urutan_riwayat, urutan_batch) + 1
    tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if jumlah > 0:
        batch_stok.append({
            "id_barang": id_barang,
            "urutan": urutan,
            "tanggal": tanggal,
            "sisa": jumlah,
            "harga_modal": harga_modal,
        })
    if harga_modal is not None:
        with open(DATA_HARGA, "a", encoding="utf-8") as file:
            file.write(f"{id_barang},{urutan},{harga_modal}\n")
        data_harga.setdefault(id_barang, []).append({"urutan": urutan, "harga": harga_modal})

def barcode_sudah_dipakai(barcode, kecuali_id=None):
    return bool(barcode) and any(
        detail.get("barcode", "") == barcode and detail["id"] != kecuali_id
        for detail in data_barang.values()
    )

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
        print(f"{'ID':<6} {'Nama Barang':<30} {'Stok':<8} {'Batas Restock':<14} {'Harga':<12}")
        print("--------------------------------------------------------------------------")
        for nama, detail in kat_items:
            harga_fmt = f"Rp{detail['harga']:,.0f}".replace(",", ".")
            batas_restock = detail.get('batas_restock', 5)
            print(f"{detail['id']:<6} {nama:<30} {detail['stok']:<8} {batas_restock:<14} {harga_fmt:<12}")
            if detail['stok'] < batas_restock:
                print(f"     --> [!] Peringatan: Stok {nama} tersisa {detail['stok']} (batas restock: {batas_restock}). Segera restock!")
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

def riwayat_transaksi():
    if not os.path.exists(RIWAYAT_TRANSAKSI_FILE) or os.path.getsize(RIWAYAT_TRANSAKSI_FILE) == 0:
        print("\n[!] Belum ada riwayat transaksi.")
        return

    with open(RIWAYAT_TRANSAKSI_FILE, "r", encoding="utf-8") as file:
        blok_transaksi = [blok.strip() for blok in file.read().split("=== TRANSAKSI ===") if blok.strip()]

    transaksi_terbaca = []
    for blok in blok_transaksi:
        match_tanggal = re.search(r"Tanggal\s*:\s*(\d{4}-\d{2}-\d{2})(?:\s+\d{2}:\d{2})?", blok)
        if not match_tanggal:
            continue
        try:
            tanggal = datetime.strptime(match_tanggal.group(1), "%Y-%m-%d").date()
        except ValueError:
            continue
        transaksi_terbaca.append((tanggal, blok))

    if not transaksi_terbaca:
        print("\n[!] Tidak ada data transaksi yang dapat dibaca.")
        return

    while True:
        print("\n==========================================================================")
        print("                         FILTER RIWAYAT TRANSAKSI                         ")
        print("==========================================================================")
        print("1. Tampilkan berdasarkan rentang tanggal")
        print("0. Kembali")
        pilihan = input("Pilih filter (0-1): ").strip()

        if pilihan == "0":
            return
        if pilihan == "1":
            try:
                mulai = datetime.strptime(input("Tanggal mulai (YYYY-MM-DD): ").strip(), "%Y-%m-%d").date()
                selesai = datetime.strptime(input("Tanggal selesai (YYYY-MM-DD): ").strip(), "%Y-%m-%d").date()
            except ValueError:
                print("\n[!] Format tanggal tidak valid. Gunakan YYYY-MM-DD.")
                continue
            if mulai > selesai:
                print("\n[!] Tanggal mulai tidak boleh setelah tanggal selesai.")
                continue
            hasil = [(tgl, blok) for tgl, blok in transaksi_terbaca if mulai <= tgl <= selesai]
            label = f"{mulai:%Y-%m-%d} s/d {selesai:%Y-%m-%d}"
        else:
            print("\n[!] Pilihan tidak valid.")
            continue

        print(f"\nRIWAYAT TRANSAKSI: {label}")
        print("==========================================================================")
        if not hasil:
            print("Tidak ada transaksi pada periode tersebut.")
        else:
            for _, blok in sorted(hasil, key=lambda data: data[0]):
                print(f"=== TRANSAKSI ===\n{blok}\n")
        print("==========================================================================")
        input("Tekan Enter untuk melanjutkan...")

def summary_penjualan():
    if not os.path.exists(RIWAYAT_TRANSAKSI_FILE) or os.path.getsize(RIWAYAT_TRANSAKSI_FILE) == 0:
        print("\n[!] Belum ada riwayat transaksi.")
        return

    with open(RIWAYAT_TRANSAKSI_FILE, "r", encoding="utf-8") as file:
        isi = file.read()

    transaksi = isi.split("=== TRANSAKSI ===")
    semua_transaksi = []

    for data in transaksi:
        if not data.strip():
            continue
        tanggal_match = re.search(r"Tanggal\s*:\s*(\d{4}-\d{2}-\d{2})", data)
        total_match = re.search(r"TOTAL:\s*Rp([\d.]+)", data)
        laba_match = re.search(r"^Laba:\s*Rp(-?[\d.]+)\s*$", data, re.MULTILINE)
        if tanggal_match and total_match:
            try:
                dt_obj = datetime.strptime(tanggal_match.group(1), "%Y-%m-%d")
                total = int(total_match.group(1).replace(".", ""))
            except ValueError:
                continue

            items_terjual = []
            baris_data = data.split("\n")
            for baris in baris_data:
                item_match = re.search(r"-\s*\[(\d+)\]\s*(.*?)\s*x(\d+)\s*=\s*Rp([\d.]+)", baris)
                if item_match:
                    id_brg = int(item_match.group(1))
                    nama_brg = item_match.group(2).strip()
                    qty = int(item_match.group(3))
                    subtotal = int(item_match.group(4).replace(".", ""))
                    items_terjual.append({
                        "id": id_brg,
                        "nama": nama_brg,
                        "qty": qty,
                        "subtotal": subtotal
                    })

            semua_transaksi.append({
                "tanggal": dt_obj,
                "total": total,
                "laba": int(laba_match.group(1).replace(".", "")) if laba_match else None,
                "items": items_terjual
            })

    if not semua_transaksi:
        print("\n[!] Tidak ada data transaksi yang dapat dibaca.")
        return

    while True:
        print("\n==========================================================================")
        print("                         SUMMARY PENJUALAN & ITEM TERJUAL                 ")
        print("==========================================================================")
        print("1. Lihat Summary Berdasarkan Rentang Tanggal")
        print("0. Kembali")
        print("==========================================================================")
        pilihan = input("Masukkan pilihan (0-1): ").strip()

        if pilihan == "0":
            return

        start_date = None
        end_date = datetime.now()

        if pilihan == "1":
            print("\nFormat tanggal: YYYY-MM-DD (Contoh: 2026-01-01)")
            tgl_mulai_str = input("Masukkan Tanggal Mulai: ").strip()
            tgl_selesai_str = input("Masukkan Tanggal Selesai: ").strip()
            try:
                start_date = datetime.strptime(tgl_mulai_str, "%Y-%m-%d")
                end_date = datetime.strptime(tgl_selesai_str, "%Y-%m-%d")
            except ValueError:
                print("\n[!] Format tanggal salah! Gunakan format YYYY-MM-DD.")
                continue
        else:
            print("\n[!] Pilihan tidak valid.")
            continue

        if start_date > end_date:
            print("\n[!] Tanggal mulai tidak boleh lebih besar dari tanggal selesai.")
            continue

        if start_date.date() == end_date.date():
            end_date = end_date.replace(hour=23, minute=59, second=59)

        rekap_harian = {}
        akumulasi_barang = {}
        grand_total = 0
        total_trx_count = 0
        laba_total = 0
        laba_count = 0

        for trx in semua_transaksi:
            dt_obj = trx["tanggal"]
            if start_date.date() <= dt_obj.date() <= end_date.date():
                tgl_key = dt_obj.strftime("%Y-%m-%d")

                if tgl_key not in rekap_harian:
                    rekap_harian[tgl_key] = {"total": 0, "count": 0, "laba": 0, "transaksi_bermodal": 0}
                rekap_harian[tgl_key]["total"] += trx["total"]
                rekap_harian[tgl_key]["count"] += 1
                if trx["laba"] is not None:
                    rekap_harian[tgl_key]["laba"] += trx["laba"]
                    rekap_harian[tgl_key]["transaksi_bermodal"] += 1
                    laba_total += trx["laba"]
                    laba_count += 1

                grand_total += trx["total"]
                total_trx_count += 1

                for item in trx["items"]:
                    nama = item["nama"]
                    if nama not in akumulasi_barang:
                        akumulasi_barang[nama] = {"id": item["id"], "qty": 0, "subtotal": 0}
                    akumulasi_barang[nama]["qty"] += item["qty"]
                    akumulasi_barang[nama]["subtotal"] += item["subtotal"]

        print("\n==========================================================================")
        print(f"       LAPORAN PENJUALAN: {start_date.strftime('%Y-%m-%d')} s/d {end_date.strftime('%Y-%m-%d')}")
        print("==========================================================================")
        print(f"{'Tanggal':<15} {'Jml Trx':<10} {'Penjualan':>18} {'Laba FIFO':>18}")
        print("----------------------------------------------------------------------------")

        if not rekap_harian:
            print("                Tidak ada transaksi pada rentang tanggal ini.             ")
        else:
            for tgl in sorted(rekap_harian.keys()):
                t_val = rekap_harian[tgl]["total"]
                c_val = rekap_harian[tgl]["count"]
                t_fmt = f"Rp{t_val:,.0f}".replace(",", ".")
                laba_harian = rekap_harian[tgl]["laba"]
                transaksi_bermodal = rekap_harian[tgl]["transaksi_bermodal"]
                laba_fmt_harian = (
                    f"Rp{laba_harian:,.0f}".replace(",", ".")
                    if transaksi_bermodal
                    else "Belum lengkap"
                )
                if 0 < transaksi_bermodal < c_val:
                    laba_fmt_harian += "*"
                print(f"{tgl:<15} {c_val:<10} {t_fmt:>18} {laba_fmt_harian:>18}")

            print("--------------------------------------------------------------------------")
            print("\n----------------- RINCIAN BARANG YANG TERJUAL ----------------------------")
            print(f"{'ID':<6} {'Nama Barang':<30} {'Terjual':<10} {'Total Pendapatan':<15}")
            print("--------------------------------------------------------------------------")

            sorted_items = sorted(akumulasi_barang.items(), key=lambda x: x[1]["qty"], reverse=True)
            for nama, detail in sorted_items:
                sub_fmt = f"Rp{detail['subtotal']:,.0f}".replace(",", ".")
                print(f"{detail['id']:<6} {nama:<30} {detail['qty']:<10} {sub_fmt:<15}")

        print("----------------------------------------------------------------------------")
        grand_fmt = f"Rp{grand_total:,.0f}".replace(",", ".")
        print(f"TOTAL KESELURUHAN ({total_trx_count} Transaksi): {grand_fmt:>24}")
        laba_total_fmt = f"Rp{laba_total:,.0f}".replace(",", ".")
        print(f"TOTAL LABA FIFO ({laba_count}/{total_trx_count} transaksi bermodal lengkap): {laba_total_fmt}")
        print("* Laba harian belum mencakup transaksi yang belum memiliki catatan modal FIFO.")
        print("==========================================================================")
        input("\nTekan Enter untuk melanjutkan...")

def tambah_barang():
    nama_barang = input("Masukkan nama barang: ").strip()
    if not nama_barang or "," in nama_barang:
        print("\n[!] Nama barang wajib diisi dan tidak boleh mengandung koma!")
        return
    nama_ada = next((nama for nama in data_barang if nama.casefold() == nama_barang.casefold()), None)
    if nama_ada is not None:
        status = data_barang[nama_ada].get('status', 'aktif')
        if status == 'aktif':
            print(f"\n[!] Barang '{nama_ada}' sudah ada. Gunakan menu Restok untuk menambah stok.")
        else:
            print(f"\n[!] Barang '{nama_ada}' sudah ada namun berstatus terhapus. Silakan cek Recycle Bin untuk restore atau hapus permanen.")
        return
    if not kategori_by_id:
        print("\n[!] Belum ada kategori. Silakan tambah kategori baru.")
        kat_baru = input("Masukkan nama kategori baru: ").strip()
        if not kat_baru or "," in kat_baru:
            print("\n[!] Nama kategori wajib diisi dan tidak boleh mengandung koma!")
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
            if not kat_baru or "," in kat_baru:
                print("\n[!] Nama kategori wajib diisi dan tidak boleh mengandung koma!")
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
        batas_restock = int(input("Masukkan batas minimum stok untuk peringatan restock: "))
    except ValueError:
        print("\n[!] Error: Jumlah, harga, dan batas restock harus berupa angka!")
        return
    if jumlah_barang < 0 or harga_barang < 0:
        print("\n[!] Stok dan harga tidak boleh negatif!")
        return
    if batas_restock < 0:
        print("\n[!] Batas restock tidak boleh negatif!")
        return
    harga_beli_input = input("Masukkan harga beli/modal per unit, angka tanpa titik (kosongkan jika stok 0): ").strip()
    try:
        harga_beli = int(harga_beli_input) if harga_beli_input else None
    except ValueError:
        print("\n[!] Harga beli harus berupa angka tanpa pemisah ribuan.")
        return
    if harga_beli is not None and harga_beli < 0:
        print("\n[!] Harga beli tidak boleh negatif.")
        return
    if jumlah_barang > 0 and harga_beli is None:
        print("\n[!] Harga beli wajib diisi jika stok awal lebih dari 0.")
        return
    barcode = input("Masukkan barcode produk (kosongkan jika belum ada): ").strip()
    if barcode_sudah_dipakai(barcode):
        print("\n[!] Barcode tersebut sudah digunakan oleh barang lain!")
        return
    id_barang = generate_id(id_kat)
    if id_barang is None:
        print(f"\n[!] Range ID kategori {kategori_by_id[id_kat]} sudah penuh (maks 99 barang per kategori).")
        return
    data_barang[nama_barang] = {
        "id": id_barang,
        "stok": jumlah_barang,
        "harga": harga_barang,
        "status": "aktif",
        "batas_restock": batas_restock,
        "hargaBeli": harga_beli,
        "barcode": barcode,
    }
    tambah_batch_stok(id_barang, jumlah_barang, harga_beli)
    simpan_batch_stok()
    simpan_data()
    with open(RIWAYAT_GUDANG_FILE, "a", encoding="utf-8") as r_file:
        modal_fmt = f"Rp{harga_beli:,.0f}".replace(",", ".") if harga_beli is not None else "belum ditetapkan"
        r_file.write(f"[TAMBAH] Barang Baru: {nama_barang} | ID: {id_barang} | Kategori: {kategori_by_id[id_kat]} (ID: {id_kat}) | Jumlah: {jumlah_barang} | Harga jual: Rp{harga_barang:,.0f} | Harga beli/unit: {modal_fmt}\n".replace(",", "."))
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
        detail = data_barang[nama_target]
        if jumlah_stok_batch(detail["id"]) != detail["stok"]:
            print("\n[!] Stok batch FIFO berbeda dari stok barang; restok dibatalkan.")
            return
        try:
            jumlah_restock = int(input(f"Masukkan jumlah stok tambahan untuk '{nama_target}': "))
            if jumlah_restock <= 0:
                print("\n[!] Jumlah restock harus lebih dari 0.")
                return
            harga_modal = int(input("Masukkan harga beli/modal per unit untuk restok ini (angka tanpa titik): ").strip())
            if harga_modal < 0:
                print("\n[!] Harga beli tidak boleh negatif.")
                return
            tambah_batch_stok(detail["id"], jumlah_restock, harga_modal)
            detail["hargaBeli"] = harga_modal
            detail["stok"] = jumlah_stok_batch(detail["id"])
            simpan_batch_stok()
            simpan_data()
            with open(RIWAYAT_GUDANG_FILE, "a", encoding="utf-8") as r_file:
                r_file.write(f"[RESTOK FIFO] {nama_target} +{jumlah_restock} @ Rp{harga_modal:,} (Total Stok: {detail['stok']})\n".replace(",", "."))
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
        if jumlah_stok_batch(detail_lama["id"]) != detail_lama["stok"]:
            print("\n[!] Stok batch FIFO berbeda dari data barang. Periksa batch sebelum mengubah stok.")
            return
        id_kat_lama = id_ke_kategori(detail_lama['id'])
        nama_baru = input(f"Masukkan nama barang baru (kosongkan jika tetap '{nama_lama}'): ").strip()
        if not nama_baru:
            nama_baru = nama_lama
        elif "," in nama_baru:
            print("\n[!] Nama barang tidak boleh mengandung koma!")
            return
        print("\nPilih Kategori:")
        for kid in sorted(kategori_by_id.keys()):
            print(f"{kid}. {kategori_by_id[kid]}")
        print("0. Tambah Kategori Baru")
        pilih_kat = input(f"Pilihan kategori (kosongkan jika tetap '{get_nama_kategori(id_kat_lama)}'): ").strip()
        if not pilih_kat:
            id_kat = id_kat_lama
        elif pilih_kat == "0":
            kat_baru = input("Masukkan nama kategori baru: ").strip()
            if not kat_baru or "," in kat_baru:
                print("\n[!] Nama kategori wajib diisi dan tidak boleh mengandung koma!")
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
            batas_restock_input = input(
                f"Masukkan batas minimum stok untuk peringatan restock "
                f"(kosongkan untuk tetap {detail_lama.get('batas_restock', 5)}): "
            ).strip()
            batas_restock = (
                int(batas_restock_input)
                if batas_restock_input
                else detail_lama.get('batas_restock', 5)
            )
        except ValueError:
            print("\n[!] Error: Masukkan input angka yang valid!")
            return
        if jumlah_baru < 0 or harga_baru < 0:
            print("\n[!] Stok dan harga tidak boleh negatif!")
            return
        if batas_restock < 0:
            print("\n[!] Batas restock tidak boleh negatif!")
            return
        barcode_lama = detail_lama.get("barcode", "")
        barcode_input = input(
            f"Masukkan barcode (kosongkan untuk tetap '{barcode_lama or 'kosong'}', ketik 0 untuk menghapus): "
        ).strip()
        barcode_baru = barcode_lama if not barcode_input else ("" if barcode_input == "0" else barcode_input)
        if barcode_sudah_dipakai(barcode_baru, kecuali_id=detail_lama["id"]):
            print("\n[!] Barcode tersebut sudah digunakan oleh barang lain!")
            return
        if nama_baru != nama_lama:
            nama_sudah_dipakai = any(
                nama.casefold() == nama_baru.casefold() and nama != nama_lama
                for nama in data_barang
            )
            if nama_sudah_dipakai:
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
        perubahan_stok = jumlah_baru - detail_lama["stok"]
        modal_batch_baru = None
        rencana_pengurangan = []
        if perubahan_stok > 0:
            try:
                modal_batch_baru = int(input("Modal per unit untuk tambahan stok ini (angka tanpa titik): ").strip())
            except ValueError:
                print("\n[!] Modal harus berupa angka.")
                if nama_baru != nama_lama:
                    data_barang[nama_lama] = detail_lama
                return
            if modal_batch_baru < 0:
                print("\n[!] Modal tidak boleh negatif.")
                if nama_baru != nama_lama:
                    data_barang[nama_lama] = detail_lama
                return
        elif perubahan_stok < 0:
            rencana_pengurangan, _ = rencana_fifo(detail_lama["id"], -perubahan_stok)
            if rencana_pengurangan is None:
                print("\n[!] Batch FIFO tidak cukup untuk menyesuaikan stok. Periksa data batch terlebih dahulu.")
                if nama_baru != nama_lama:
                    data_barang[nama_lama] = detail_lama
                return

        if rencana_pengurangan:
            terapkan_rencana_fifo(rencana_pengurangan)
        if id_barang_baru != detail_lama["id"]:
            for batch in batch_stok:
                if batch["id_barang"] == detail_lama["id"]:
                    batch["id_barang"] = id_barang_baru
        if perubahan_stok > 0:
            tambah_batch_stok(id_barang_baru, perubahan_stok, modal_batch_baru)
        data_barang[nama_baru] = {
            "id": id_barang_baru,
            "stok": jumlah_stok_batch(id_barang_baru),
            "harga": harga_baru,
            "status": "aktif",
            "batas_restock": batas_restock,
            "hargaBeli": modal_batch_baru if perubahan_stok > 0 else detail_lama.get("hargaBeli"),
            "barcode": barcode_baru,
        }
        simpan_batch_stok()
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
            id_barang = data_barang[nama_target]["id"]
            del data_barang[nama_target]
            batch_stok[:] = [batch for batch in batch_stok if batch["id_barang"] != id_barang]
            simpan_batch_stok()
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

def kelola_barcode():
    barang_aktif = [(nama, detail) for nama, detail in data_barang.items()
                    if detail.get("status", "aktif") == "aktif"]
    if not barang_aktif:
        print("\n[!] Belum ada barang aktif untuk dikelola.")
        return
    print("\nDAFTAR BARANG DAN BARCODE")
    for nama, detail in sorted(barang_aktif, key=lambda item: item[1]["id"]):
        print(f"ID {detail['id']}: {nama} | Barcode: {detail.get('barcode') or '(belum diatur)'}")
    try:
        id_barang = int(input("Masukkan ID barang: ").strip())
    except ValueError:
        print("\n[!] ID harus berupa angka.")
        return
    target = next(((nama, detail) for nama, detail in barang_aktif if detail["id"] == id_barang), None)
    if target is None:
        print("\n[!] Barang aktif dengan ID tersebut tidak ditemukan.")
        return
    nama, detail = target
    barcode = input("Barcode baru (ketik 0 untuk menghapus barcode): ").strip()
    barcode = "" if barcode == "0" else barcode
    if barcode_sudah_dipakai(barcode, kecuali_id=id_barang):
        print("\n[!] Barcode tersebut sudah digunakan oleh barang lain!")
        return
    detail["barcode"] = barcode
    simpan_data()
    print(f"\n[V] Barcode barang '{nama}' berhasil diperbarui.")

def kelola_pengguna():
    while True:
        print("\n==========================================================================")
        print("                             KELOLA PENGGUNA                              ")
        print("==========================================================================")
        print("1. Lihat Daftar Pengguna")
        print("2. Tambah Pengguna Baru")
        print("3. Ubah Status Akun ")
        print("4. Restore Akun (Aktifkan Kembali)")
        print("5. Hapus Permanen Pengguna")
        print("0. Kembali")
        print("==========================================================================")
        pilih = input("Pilih menu (0-3): ").strip()

        if pilih == "0":
            break
        elif pilih == "1":
            if not os.path.exists(USER_FILE):
                print("\n[!] File User.txt belum ada.")
                continue
            print("\n==========================================================================")
            print("                         DAFTAR PENGGUNA SISTEM                           ")
            print("==========================================================================")
            print(f"{'Username':<25} {'Role':<18} {'Status':<12}")
            print("--------------------------------------------------------------------------")
            with open(USER_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        parts = [p.strip() for p in line.strip().split(",")]
                        if len(parts) >= 3:
                            u = parts[0]
                            r = parts[2]
                            st = parts[3] if len(parts) > 3 else "aktif"
                            print(f"{u:<25} {r:<18} {st:<12}")
            print("==========================================================================")
        elif pilih == "2":
            new_user = input("Masukkan username baru: ").strip()
            new_pass = input("Masukkan password baru: ").strip()
            print("Pilih Role:")
            print("1. admin")
            print("2. admin gudang")
            print("3. kasir")
            r_pilih = input("Masukkan pilihan role (1-3): ").strip()
            if r_pilih == "1":
                new_role = "admin"
            elif r_pilih == "2":
                new_role = "admin gudang"
            elif r_pilih == "3":
                new_role = "kasir"
            else:
                print("\n[!] Role tidak valid.")
                continue

            if not new_user or not new_pass or "," in new_user or "," in new_pass:
                print("\n[!] Username/password wajib diisi dan tidak boleh mengandung koma.")
                continue

            users_list = []
            ada = False
            if os.path.exists(USER_FILE):
                with open(USER_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            p = [x.strip() for x in line.strip().split(",")]
                            if len(p) >= 3:
                                if p[0].casefold() == new_user.casefold():
                                    ada = True
                                st = p[3] if len(p) > 3 else "aktif"
                                users_list.append([p[0], p[1], p[2], st])
            if ada:
                print(f"\n[!] Username '{new_user}' sudah terdaftar!")
                continue

            users_list.append([new_user, new_pass, new_role])
            with open(USER_FILE, "w", encoding="utf-8") as f:
                for u, p, r, st in users_list:
                    f.write(f"{u},{p},{r},{st}\n")
            print(f"\n[V] Pengguna '{new_user}' berhasil ditambahkan!")
        elif pilih == "3":
            target_user = input("Masukkan username yang ingin dinonaktifkan (Soft Delete): ").strip()
            if target_user.casefold() == current_user.casefold():
                print("\n[!] Anda tidak dapat menonaktifkan akun yang sedang digunakan saat ini!")
                continue
            
            users_list = []
            ditemukan = False
            if os.path.exists(USER_FILE):
                with open(USER_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            p = [x.strip() for x in line.strip().split(",")]
                            if len(p) >= 3:
                                u, pw, r = p[0], p[1], p[2]
                                st = p[3] if len(p) > 3 else "aktif"
                                if u.casefold() == target_user.casefold():
                                    ditemukan = True
                                    st = "tidak_aktif"
                                users_list.append([u, pw, r, st])
                                
            if not ditemukan:
                print(f"\n[!] Pengguna '{target_user}' tidak ditemukan.")
                continue
                
            with open(USER_FILE, "w", encoding="utf-8") as f:
                for u, pw, r, st in users_list:
                    f.write(f"{u},{pw},{r},{st}\n")
            print(f"\n[V] Pengguna '{target_user}' berhasil diubah statusnya menjadi TIDAK AKTIF.")
        elif pilih == "4":
            target_user = input("Masukkan username yang ingin di-restore (diaktifkan kembali): ").strip()
            users_list = []
            ditemukan = False
            if os.path.exists(USER_FILE):
                with open(USER_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            p = [x.strip() for x in line.strip().split(",")]
                            if len(p) >= 3:
                                u, pw, r = p[0], p[1], p[2]
                                st = p[3] if len(p) > 3 else "aktif"
                                if u.casefold() == target_user.casefold():
                                    ditemukan = True
                                    st = "aktif"
                                users_list.append([u, pw, r, st])
                                
            if not ditemukan:
                print(f"\n[!] Pengguna '{target_user}' tidak ditemukan.")
                continue
                
            with open(USER_FILE, "w", encoding="utf-8") as f:
                for u, pw, r, st in users_list:
                    f.write(f"{u},{pw},{r},{st}\n")
            print(f"\n[V] Pengguna '{target_user}' berhasil di-restore (AKTIF).")
        elif pilih == "5":
            target_user = input("Masukkan username yang ingin dihapus PERMANEN: ").strip()
            if target_user.casefold() == current_user.casefold():
                print("\n[!] Anda tidak dapat menghapus akun yang sedang digunakan saat ini!")
                continue
                
            konfirmasi = input(f"Apakah Anda yakin ingin menghapus permanen akun '{target_user}'? (y/n): ").strip().lower()
            if konfirmasi != 'y':
                print("\n[!] Penghapusan permanen dibatalkan.")
                continue
                
            users_list = []
            ditemukan = False
            if os.path.exists(USER_FILE):
                with open(USER_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            p = [x.strip() for x in line.strip().split(",")]
                            if len(p) >= 3:
                                if p[0].casefold() == target_user.casefold():
                                    ditemukan = True
                                    continue
                                st = p[3] if len(p) > 3 else "aktif"
                                users_list.append([p[0], p[1], p[2], st])
                                
            if not ditemukan:
                print(f"\n[!] Pengguna '{target_user}' tidak ditemukan.")
                continue
                
            with open(USER_FILE, "w", encoding="utf-8") as f:
                for u, pw, r, st in users_list:
                    f.write(f"{u},{pw},{r},{st}\n")
            print(f"\n[V] Pengguna '{target_user}' berhasil dihapus secara permanen.")
        else:
            print("\n[!] Pilihan tidak valid.")

def ganti_password_sendiri():
    print("\n==========================================================================")
    print("                         GANTI PASSWORD SENDIRI                           ")
    print("==========================================================================")
    pass_lama = input("Masukkan password lama: ").strip()
    pass_baru = input("Masukkan password baru: ").strip()
    konfirmasi = input("Konfirmasi password baru: ").strip()

    if not pass_baru or "," in pass_baru:
        print("\n[!] Password baru wajib diisi dan tidak boleh mengandung koma!")
        return
    if pass_baru != konfirmasi:
        print("\n[!] Konfirmasi password baru tidak cocok!")
        return

    users_list = []
    berhasil = False
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    parts = [p.strip() for p in line.strip().split(",")]
                    if len(parts) >= 3:
                        u, p, r = parts[0], parts[1], parts[2]
                        st = parts[3] if len(parts) > 3 else "aktif"
                        if u == current_user:
                            if p == pass_lama:
                                p = pass_baru
                                berhasil = True
                            else:
                                print("\n[!] Password lama salah!")
                                return
                        users_list.append([u, p, r])

    if berhasil:
        with open(USER_FILE, "w", encoding="utf-8") as f:
            for u, p, r, st in users_list:
                f.write(f"{u},{p},{r},{st}\n")
        print("\n[V] Password berhasil diperbarui!")

def scanner_barang():
    print("\n==========================================================================")
    print("                         BARCODE SCANNER MODE                             ")
    print("==========================================================================")
    print("Scan barcode produk untuk menambah satu unit ke keranjang. Masukkan 0 untuk keluar.")
    while True:
        barcode_input = input("\nSCAN BARCODE: ").strip()
        if barcode_input == "0":
            print("\nKeluar dari Scanner Mode...")
            return
        if not barcode_input:
            continue
        target = next((
            (nama, detail) for nama, detail in data_barang.items()
            if detail.get("status", "aktif") == "aktif"
            and detail.get("barcode", "") == barcode_input
        ), None)
        if target is None:
            print("[!] Barcode tidak ditemukan atau barang tidak aktif.")
            continue
        nama, detail = target
        item_keranjang = next((item for item in keranjang if item["id"] == detail["id"]), None)
        jumlah_di_keranjang = item_keranjang["jumlah"] if item_keranjang else 0
        if jumlah_di_keranjang >= detail["stok"]:
            print(f"[!] Stok '{nama}' tidak mencukupi; stok tersedia {detail['stok']}.")
            continue
        if item_keranjang:
            item_keranjang["jumlah"] += 1
        else:
            keranjang.append({
                "id": detail["id"],
                "nama": nama,
                "jumlah": 1,
                "harga": detail["harga"],
            })
        print(f"[V] {nama} ditambahkan. Jumlah di keranjang: {jumlah_di_keranjang + 1}.")

def checkout():
    if not keranjang:
        print("\n[!] Keranjang belanja kosong. Silakan tambah barang terlebih dahulu.")
        return
    kebutuhan_fifo = {}
    item_per_id = {}
    for item in keranjang:
        detail = data_barang.get(item['nama'])
        if (detail is None or detail.get('status', 'aktif') != 'aktif'
                or detail['id'] != item['id']):
            print(f"\n[!] Barang '{item['nama']}' sudah tidak tersedia. Periksa keranjang.")
            return
        if item['jumlah'] > detail['stok']:
            print(f"\n[!] Stok '{item['nama']}' hanya {detail['stok']}; checkout dibatalkan.")
            return
        id_barang = detail["id"]
        if jumlah_stok_batch(id_barang) != detail["stok"]:
            print(f"\n[!] Stok batch FIFO '{item['nama']}' berbeda dari stok barang; checkout dibatalkan.")
            return
        kebutuhan_fifo[id_barang] = kebutuhan_fifo.get(id_barang, 0) + item["jumlah"]
        item_per_id[id_barang] = item["nama"]

    rencana_transaksi = []
    total_modal = 0
    modal_lengkap = True
    for id_barang, jumlah in kebutuhan_fifo.items():
        rencana, modal_barang = rencana_fifo(id_barang, jumlah)
        if rencana is None:
            nama = item_per_id[id_barang]
            stok_batch = jumlah_stok_batch(id_barang)
            print(f"\n[!] Batch FIFO '{nama}' hanya mencatat {stok_batch} unit; checkout dibatalkan agar stok tidak salah.")
            return
        rencana_transaksi.append((id_barang, rencana))
        if modal_barang is None:
            modal_lengkap = False
        elif modal_lengkap:
            total_modal += modal_barang
    rincian_modal_fifo = []
    for id_barang, rencana in rencana_transaksi:
        for index, jumlah_batch in rencana:
            batch = batch_stok[index]
            if batch["harga_modal"] is None:
                rincian_modal_fifo.append(
                    f"- ID {id_barang}, batch {batch['urutan']}: {jumlah_batch} unit, modal belum diketahui\n"
                )
            else:
                subtotal_modal = jumlah_batch * batch["harga_modal"]
                rincian_modal_fifo.append(
                    f"- ID {id_barang}, batch {batch['urutan']}: {jumlah_batch} x "
                    f"Rp{batch['harga_modal']:,.0f} = Rp{subtotal_modal:,.0f}\n".replace(",", ".")
                )
    total_modal = total_modal if modal_lengkap else None
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
    laba_val = total_harga - total_modal if total_modal is not None else None
    modal_fmt = (
        f"Rp{total_modal:,.0f}".replace(",", ".")
        if total_modal is not None
        else "Belum dihitung (modal batch belum lengkap)"
    )
    laba_fmt = (
        f"Rp{laba_val:,.0f}".replace(",", ".")
        if laba_val is not None
        else "Belum dihitung (modal batch belum lengkap)"
    )
    print("==========================================================================")
    print(f"TOTAL HARGA: {total_fmt}")
    print(f"MODAL FIFO : {modal_fmt}")
    print(f"LABA       : {laba_fmt}")
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

    terapkan_banyak_rencana_fifo([rencana for _, rencana in rencana_transaksi])
    for id_barang in kebutuhan_fifo:
        detail = next((item for item in data_barang.values() if item["id"] == id_barang), None)
        if detail is not None:
            detail["stok"] = jumlah_stok_batch(id_barang)

    simpan_batch_stok()
    simpan_data()

    nomor_urut = hitung_transaksi_hari_ini() + 1
    kode_transaksi = f"SMK{nomor_urut:03d}"

    log_transaksi = "=== TRANSAKSI ===\n"
    log_transaksi += f"ID Transaksi: {kode_transaksi}{waktu_transaksi.strftime('%Y%m%d%H%M%S')}\n"
    log_transaksi += f"Tanggal : {waktu_str}\n"
    log_transaksi += f"Kasir   : {current_user}\n"
    log_transaksi += f"Metode  : {metode}\n"
    log_transaksi += "----------------------------------------\n"
    log_transaksi += "Rincian modal FIFO:\n"
    log_transaksi += "".join(rincian_modal_fifo)
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
    log_transaksi += f"Modal FIFO: {modal_fmt}\n"
    log_transaksi += f"Laba: {laba_fmt}\n"
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
    print(f"MODAL FIFO      : {modal_fmt}")
    print(f"LABA            : {laba_fmt}")
    print(f"UANG DIBAYARKAN : Rp{uang_dibayarkan:,.0f}".replace(",", "."))
    print(f"KEMBALIAN       : Rp{kembalian:,.0f}".replace(",", "."))
    print("==========================================================================")
    print("            Terima kasih telah berbelanja di SMKMART!                    ")
    print("==========================================================================")

def main():
    global admin_menu, Gudang, kasir, current_user
    while login:
        admin_menu = False
        Gudang = False
        kasir = False

        print("==========================================================================")
        print("              LOGIN SISTEM PENGELOLAAN BARANG SMKMART")
        print("==========================================================================")
        print("Masukkan username dan password untuk masuk ke sistem.")
        print("(Keluar Aplikasi: 0)")
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")

        if username == "0" and password == "0":
            sys.exit()

        login_berhasil = False
        role_login = ""
        akun_nonaktif = False

        if os.path.exists(USER_FILE):
            with open(USER_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        parts = [p.strip() for p in line.strip().split(",")]
                        if len(parts) >= 3:
                            user, pwd, role = parts[0], parts[1], parts[2]
                            st = parts[3] if len(parts) > 3 else "aktif"
                            if user == username and pwd == password:
                                if st == "tidak_aktif":
                                    akun_nonaktif = True
                                else:
                                    role_login = role
                                    login_berhasil = True
                                break

        if not login_berhasil:
            if akun_nonaktif:
                print("\n[!] Akun Anda berstatus TIDAK AKTIF (dinonaktifkan). Hubungi Admin.")
            else:
                print("\n[!] Username atau password salah!")
            continue

        current_user = username
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n[V] Login berhasil! Selamat datang, {username}")
        print(f"Peran Anda: {role_login}")

        role_clean = role_login.strip().lower()
        is_admin_utama = (role_clean == "admin")
        
        if is_admin_utama:
            admin_menu = True
        elif role_clean == "admin gudang":
            Gudang = True
        elif role_clean == "kasir":
            kasir = True

        muat_data()

        print("==========================================================================")
        print("             APLIKASI SISTEM PENGELOLAAN BARANG SMKMART                  ")
        print("==========================================================================")

        while admin_menu:
            print("\n==========================================================================")
            print("               MENU ADMIN UTAMA - SMKMART                                 ")
            print("==========================================================================")
            print("1. Kelola Pengguna")
            print("2. Kelola Data Barang (Tambah, Ubah, Hapus)")
            print("3. Lihat dan Cari Barang")
            print("4. Daftar Stok Barang")
            print("5. Laporan Penjualan")
            print("6. Laporan Stok dan Aktivitas Gudang (Riwayat Gudang)")
            print("7. Log Aktivitas (Riwayat Transaksi)")
            print("8. Ganti Password Sendiri")
            print("9. Menu Kasir")
            print("10. Menu Gudang")
            print("0. Kembali ke halaman login")
            print("==========================================================================")

            pilihan_adm = input("Masukkan pilihan menu (0-10): ").strip()

            if pilihan_adm == "1":
                kelola_pengguna()
            elif pilihan_adm == "2":
                print("\n--- KELOLA DATA BARANG ---")
                print("1. Tambah Barang")
                print("2. Ubah Barang")
                print("3. Hapus Barang")
                print("0. Batal")
                sub = input("Pilih aksi (0-3): ").strip()
                if sub == "1":
                    tambah_barang()
                elif sub == "2":
                    ubah_barang()
                elif sub == "3":
                    hapus_barang()
            elif pilihan_adm == "3":
                cari_barang_linear(data_barang)
            elif pilihan_adm == "4":
                if not data_barang:
                    print("\n[!] Data barang masih kosong.")
                    continue
                tampilkan_tabel_grouped()
            elif pilihan_adm == "5":
                summary_penjualan()
            elif pilihan_adm == "6":
                if not os.path.exists(RIWAYAT_GUDANG_FILE) or os.path.getsize(RIWAYAT_GUDANG_FILE) == 0:
                    print("\n[!] Belum ada laporan stok/aktivitas gudang.")
                    continue
                print("\n==========================================================================")
                print("                       LAPORAN STOK & AKTIVITAS GUDANG                    ")
                print("==========================================================================")
                with open(RIWAYAT_GUDANG_FILE, "r", encoding="utf-8") as file:
                    print(file.read().strip())
                print("==========================================================================")
            elif pilihan_adm == "7":
                riwayat_transaksi()
            elif pilihan_adm == "8":
                ganti_password_sendiri()
            elif pilihan_adm == "9":
                kasir = True
            
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
                    print("8. Barcode Scanner")
                    print("0. Kembali ke Menu Utama Admin")
                    print("==========================================================================")

                    pilihan_kasir = input("Masukkan pilihan menu (0-8): ").strip()

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
                                item_keranjang = next(
                                    (item for item in keranjang if item["id"] == data_barang[target_nama]["id"]),
                                    None,
                                )
                                jumlah_di_keranjang = item_keranjang["jumlah"] if item_keranjang else 0
                                if jumlah_di_keranjang + jumlah_beli > stok_tersedia:
                                    print(f"\n[!] Total {target_nama} di keranjang akan melebihi stok ({stok_tersedia}).")
                                    continue
                                if item_keranjang:
                                    item_keranjang["jumlah"] += jumlah_beli
                                else:
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
                            item = keranjang[target_idx]
                            item["jumlah"] -= 1
                            if item["jumlah"] == 0:
                                keranjang.pop(target_idx)
                                print(f"\n[V] '{item['nama']}' (ID: {item['id']}) dihapus dari keranjang.")
                            else:
                                print(f"\n[V] Jumlah '{item['nama']}' dikurangi 1. Sisa: {item['jumlah']}.")
                        else:
                            print("\n[!] ID barang tidak ditemukan di keranjang.")
                    elif pilihan_kasir == "4":
                        checkout()
                    elif pilihan_kasir == "5":
                        riwayat_transaksi()
                    elif pilihan_kasir == "6":
                        cari_barang_linear(data_barang)
                    elif pilihan_kasir == "7":
                        summary_penjualan()
                    elif pilihan_kasir == "8":
                        scanner_barang()
                    elif pilihan_kasir == "0":
                        print("\nKembali ke Menu Utama Admin...")
                        if keranjang:
                            keranjang.clear()
                            print("[!] Keranjang dikosongkan saat sesi kasir berakhir.")
                        kasir = False
                    else:
                        print("\n[!] Pilihan tidak valid. Silakan pilih 0-8.")
            elif pilihan_adm == "10":
                Gudang = True
                while Gudang:
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
                    print("10. Kelola Barcode")
                    print("0. Kembali ke Menu Utama Admin")
                    print("==========================================================================")

                    pilihan = input("Masukkan pilihan menu (0-10): ").strip()

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
                        kelola_barcode()
                    elif pilihan == "0":
                        print("\nKembali ke Menu Utama Admin...")
                        Gudang = False
                    else:
                        print("\n[!] Pilihan tidak valid. Silakan masukkan pilihan angka 0-10.")
            elif pilihan_adm == "0":
                print("\nKembali ke halaman login...")
                admin_menu = False
            else:
                print("\n[!] Pilihan tidak valid.")

        while Gudang:
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
            print("10. Kelola Barcode")
            print("0. Kembali ke halaman login")
            print("==========================================================================")

            pilihan = input("Masukkan pilihan menu (0-10): ").strip()

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
                kelola_barcode()
            elif pilihan == "0":
                print("\nKembali ke halaman login...")
                Gudang = False
            else:
                print("\n[!] Pilihan tidak valid. Silakan masukkan pilihan angka 0-10.")

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
            print("8. Barcode Scanner")
            print("0. Kembali ke Halaman Login")
            print("==========================================================================")

            pilihan_kasir = input("Masukkan pilihan menu (0-8): ").strip()

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
                        item_keranjang = next(
                            (item for item in keranjang if item["id"] == data_barang[target_nama]["id"]),
                            None,
                        )
                        jumlah_di_keranjang = item_keranjang["jumlah"] if item_keranjang else 0
                        if jumlah_di_keranjang + jumlah_beli > stok_tersedia:
                            print(f"\n[!] Total {target_nama} di keranjang akan melebihi stok ({stok_tersedia}).")
                            continue
                        if item_keranjang:
                            item_keranjang["jumlah"] += jumlah_beli
                        else:
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
                    item = keranjang[target_idx]
                    item["jumlah"] -= 1
                    if item["jumlah"] == 0:
                        keranjang.pop(target_idx)
                        print(f"\n[V] '{item['nama']}' (ID: {item['id']}) dihapus dari keranjang.")
                    else:
                        print(f"\n[V] Jumlah '{item['nama']}' dikurangi 1. Sisa: {item['jumlah']}.")
                else:
                    print("\n[!] ID barang tidak ditemukan di keranjang.")
            elif pilihan_kasir == "4":
                checkout()
            elif pilihan_kasir == "5":
                riwayat_transaksi()
            elif pilihan_kasir == "6":
                cari_barang_linear(data_barang)
            elif pilihan_kasir == "7":
                summary_penjualan()
            elif pilihan_kasir == "8":
                scanner_barang()
            elif pilihan_kasir == "0":
                print("\nKembali ke halaman login...")
                if keranjang:
                    keranjang.clear()
                    print("[!] Keranjang dikosongkan saat sesi kasir berakhir.")
                kasir = False
            else:
                print("\n[!] Pilihan tidak valid. Silakan pilih 0-8.")

if __name__ == "__main__":
    main()