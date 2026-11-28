"""Trouble detector dan verifikasi lingkungan SMKMART.

Skrip ini memeriksa interpreter Python, pip, virtual environment, seluruh
dependensi di requirements.txt, kemampuan membuat berkas Excel, akses tulis,
akun pengguna, serta integritas berkas data.

Jalankan dari venv:
    .venv\\Scripts\\python.exe cek_lingkungan.py

Atau cukup klik cek.bat. Gunakan --ringkas untuk keluaran satu baris
(dipakai run.bat untuk pemeriksaan cepat).
"""

import importlib.metadata
import os
import re
import subprocess
import sys
import tempfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS_FILE = os.path.join(BASE_DIR, "requirements.txt")
MIN_PYTHON = (3, 9)
RINGKAS = "--ringkas" in sys.argv

hasil = []


def catat(nama, ok, detail="", saran="", peringatan=False):
    hasil.append({
        "nama": nama,
        "ok": ok,
        "detail": detail,
        "saran": saran,
        "peringatan": peringatan,
    })


def cek_python():
    versi = sys.version_info
    ok = versi >= MIN_PYTHON
    catat(
        "Python",
        ok,
        f"versi {versi.major}.{versi.minor}.{versi.micro}",
        f"Butuh Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} atau lebih baru.",
    )
    catat("Lokasi Python", True, sys.executable)
    catat("Arsitektur", True, "64-bit" if sys.maxsize > 2**32 else "32-bit")
    if "windowsapps" in sys.executable.lower():
        catat(
            "Sumber Python",
            True,
            "Microsoft Store",
            "Bila muncul masalah, pasang Python dari python.org lalu jalankan setup.bat.",
            peringatan=True,
        )


def cek_venv():
    di_venv = sys.prefix != sys.base_prefix
    catat(
        "Virtual environment",
        di_venv,
        os.path.basename(sys.prefix or ".venv") if di_venv else "memakai Python global",
        "Jalankan setup.bat agar aplikasi memakai .venv, bukan Python global.",
    )


def cek_pip():
    try:
        proses = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        ok = proses.returncode == 0
        keluaran = (proses.stdout or proses.stderr or "").strip()
        detail = keluaran.splitlines()[0] if keluaran else "tidak merespons"
    except (OSError, subprocess.SubprocessError) as error:
        ok = False
        detail = str(error)
    catat(
        "pip",
        ok,
        detail,
        "Jalankan setup.bat; pip akan dipasang otomatis memakai ensurepip/get-pip.",
    )
    return ok


def daftar_paket_requirements():
    if not os.path.exists(REQUIREMENTS_FILE):
        return []
    paket = []
    with open(REQUIREMENTS_FILE, "r", encoding="utf-8-sig") as file:
        for baris in file:
            baris = baris.strip()
            if not baris or baris.startswith("#"):
                continue
            nama = re.split(r"[<>=!~\[\]; ]", baris, maxsplit=1)[0].strip()
            if nama:
                paket.append(nama)
    return paket


def cek_dependensi():
    paket = daftar_paket_requirements()
    if not paket:
        catat("Dependensi requirements", True, "requirements.txt kosong atau tidak ada")
        return True
    hilang = []
    for nama in paket:
        try:
            importlib.metadata.version(nama)
        except importlib.metadata.PackageNotFoundError:
            hilang.append(nama)
    ok = not hilang
    detail = f"{len(paket) - len(hilang)}/{len(paket)} terpasang"
    if hilang:
        detail += f" | belum: {', '.join(hilang)}"
    catat(
        "Dependensi requirements",
        ok,
        detail,
        "Jalankan setup.bat untuk memasang paket yang belum ada.",
    )
    return ok


def cek_openpyxl():
    try:
        import openpyxl
    except ImportError:
        catat("openpyxl", False, "belum terpasang", "Jalankan setup.bat.")
        return False
    catat("openpyxl", True, f"versi {getattr(openpyxl, '__version__', '?')}")

    try:
        from openpyxl import Workbook, load_workbook
        from openpyxl.chart import PieChart, Reference

        wb = Workbook()
        ws = wb.active
        ws.append(["Kategori", "Nilai"])
        ws.append(["Uji A", 10])
        ws.append(["Uji B", 20])
        chart = PieChart()
        chart.add_data(Reference(ws, min_col=2, min_row=1, max_row=3), titles_from_data=True)
        chart.set_categories(Reference(ws, min_col=1, min_row=2, max_row=3))
        ws.add_chart(chart, "D2")
        with tempfile.TemporaryDirectory() as folder:
            uji = os.path.join(folder, "uji.xlsx")
            wb.save(uji)
            load_workbook(uji)
        catat("Mesin Excel (.xlsx + chart)", True, "membuat dan membaca berkas uji berhasil")
    except Exception as error:
        catat("Mesin Excel (.xlsx + chart)", False, str(error), "Pasang ulang openpyxl lewat setup.bat.")
        return False
    return True


def cek_akses_tulis():
    try:
        os.makedirs(os.path.join(BASE_DIR, "exports"), exist_ok=True)
        uji = os.path.join(BASE_DIR, ".uji_tulis.tmp")
        with open(uji, "w", encoding="utf-8") as file:
            file.write("uji")
        os.remove(uji)
        catat("Akses tulis folder", True, BASE_DIR)
    except OSError as error:
        catat(
            "Akses tulis folder",
            False,
            str(error),
            "Pindahkan aplikasi ke folder yang bisa ditulis, misalnya Documents.",
        )


def hitung_baris_rusak(nama, panjang_valid):
    lokasi = os.path.join(BASE_DIR, nama)
    if not os.path.exists(lokasi):
        return None, None
    rusak = 0
    total = 0
    try:
        with open(lokasi, "r", encoding="utf-8-sig") as file:
            for baris in file:
                if not baris.strip():
                    continue
                total += 1
                if len(baris.strip().split(",")) not in panjang_valid:
                    rusak += 1
    except OSError:
        return -1, 0
    return rusak, total


def cek_integritas_data():
    aturan = {
        "data.txt": {4, 5, 6, 7, 8},
        "kategori.txt": {2},
        "batch_stok.txt": {5},
    }
    for nama, panjang_valid in aturan.items():
        rusak, total = hitung_baris_rusak(nama, panjang_valid)
        if rusak is None:
            continue
        if rusak == -1:
            catat("Berkas " + nama, False, "tidak bisa dibaca", "Periksa izin akses berkas.")
        elif rusak:
            catat(
                "Berkas " + nama,
                True,
                f"{rusak} dari {total} baris perlu dicek",
                "Cadangkan berkas lalu perbaiki baris tersebut; aplikasi akan melewati baris rusak.",
                peringatan=True,
            )
        else:
            catat("Berkas " + nama, True, f"{total} baris valid")


def cek_akun():
    lokasi = os.path.join(BASE_DIR, "User.txt")
    if not os.path.exists(lokasi):
        catat(
            "Berkas akun",
            False,
            "User.txt tidak ditemukan",
            "Pastikan User.txt berada di folder aplikasi.",
        )
        return
    jumlah = 0
    try:
        with open(lokasi, "r", encoding="utf-8-sig") as file:
            for baris in file:
                baris = baris.strip()
                if not baris or baris.lower().startswith("kunci="):
                    continue
                bagian = [bagian.strip() for bagian in baris.split(",")]
                if len(bagian) >= 3 and bagian[0]:
                    jumlah += 1
    except OSError as error:
        catat("Akun pengguna", False, str(error), "Periksa izin akses User.txt.")
        return
    catat(
        "Akun pengguna",
        jumlah > 0,
        f"{jumlah} akun terbaca" if jumlah else "tidak ada akun valid",
        "Tambahkan akun dengan format Username,Password,Peran,Status di User.txt.",
    )


def cek_berkas_data():
    opsional = ["data.txt", "kategori.txt", "batch_stok.txt", "riwayat_transaksi.txt"]
    ada = sum(1 for nama in opsional if os.path.exists(os.path.join(BASE_DIR, nama)))
    catat("Berkas data", True, f"{ada}/{len(opsional)} tersedia (dibuat otomatis bila kosong)")


def main():
    cek_python()
    cek_venv()
    cek_pip()
    cek_dependensi()
    cek_openpyxl()
    cek_akses_tulis()
    cek_akun()
    cek_berkas_data()
    cek_integritas_data()

    gagal = [item for item in hasil if not item["ok"]]
    peringatan = [item for item in hasil if item["ok"] and item["peringatan"]]

    if RINGKAS:
        if gagal:
            print("Lingkungan belum siap: " + ", ".join(item["nama"] for item in gagal))
            return 1
        if peringatan:
            print(f"Lingkungan siap dengan {len(peringatan)} peringatan.")
        else:
            print("Lingkungan siap.")
        return 0

    print("==========================================================================")
    print("                 TROUBLE DETECTOR LINGKUNGAN SMKMART                      ")
    print("==========================================================================")
    for item in hasil:
        if item["ok"] and item["peringatan"]:
            tanda = "[!!]"
        elif item["ok"]:
            tanda = "[OK]"
        else:
            tanda = "[!] "
        print(f"{tanda} {item['nama']:<28} {item['detail']}")
        if item["saran"] and (not item["ok"] or item["peringatan"]):
            print(f"      -> {item['saran']}")
    print("--------------------------------------------------------------------------")

    if gagal:
        print(f"HASIL: {len(gagal)} masalah ditemukan. Ikuti saran di atas.")
        print("Jalankan setup.bat, lalu ulangi cek.bat.")
        return 1
    if peringatan:
        print(f"HASIL: siap dijalankan, dengan {len(peringatan)} peringatan yang sebaiknya dicek.")
        return 0
    print("HASIL: semua pemeriksaan lulus. Aplikasi siap dijalankan dengan run.bat.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
