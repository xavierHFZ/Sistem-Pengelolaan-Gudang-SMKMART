"""Verifikasi lingkungan SMKMART.

Skrip ini memeriksa interpreter Python, virtual environment, seluruh
dependensi di requirements.txt, kemampuan membuat berkas Excel, akses tulis,
dan berkas data yang diperlukan.

Jalankan dari venv:
    .venv\\Scripts\\python.exe cek_lingkungan.py

Atau cukup klik cek.bat. Gunakan --ringkas untuk keluaran satu baris
(dipakai run.bat untuk pemeriksaan cepat).
"""

import importlib.metadata
import os
import re
import sys
import tempfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS_FILE = os.path.join(BASE_DIR, "requirements.txt")
MIN_PYTHON = (3, 9)
RINGKAS = "--ringkas" in sys.argv

hasil = []


def catat(nama, ok, detail="", saran=""):
    hasil.append({"nama": nama, "ok": ok, "detail": detail, "saran": saran})


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


def cek_venv():
    di_venv = sys.prefix != sys.base_prefix
    catat(
        "Virtual environment",
        di_venv,
        os.path.basename(sys.prefix) if di_venv else "memakai Python global",
        "Jalankan setup.bat agar aplikasi memakai .venv, bukan Python global.",
    )


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
        catat("Dependensi", True, "requirements.txt kosong atau tidak ada")
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
        catat("Mesin Excel (.xlsx + chart)", False, str(error), "Pasang ulang openpyxl.")
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


def cek_berkas():
    user_file = os.path.join(BASE_DIR, "User.txt")
    catat(
        "Berkas akun",
        os.path.exists(user_file),
        "User.txt tersedia" if os.path.exists(user_file) else "User.txt tidak ditemukan",
        "Pastikan User.txt berada di folder aplikasi.",
    )
    opsional = ["data.txt", "kategori.txt", "batch_stok.txt", "riwayat_transaksi.txt"]
    ada = sum(1 for nama in opsional if os.path.exists(os.path.join(BASE_DIR, nama)))
    catat("Berkas data", True, f"{ada}/{len(opsional)} tersedia (dibuat otomatis bila kosong)")


def main():
    cek_python()
    cek_venv()
    cek_dependensi()
    cek_openpyxl()
    cek_akses_tulis()
    cek_berkas()

    gagal = [item for item in hasil if not item["ok"]]

    if RINGKAS:
        if gagal:
            print("Lingkungan belum siap: " + ", ".join(item["nama"] for item in gagal))
            return 1
        print("Lingkungan siap.")
        return 0

    print("==========================================================================")
    print("                    VERIFIKASI LINGKUNGAN SMKMART                         ")
    print("==========================================================================")
    for item in hasil:
        tanda = "[OK]" if item["ok"] else "[!] "
        print(f"{tanda} {item['nama']:<28} {item['detail']}")
        if not item["ok"] and item["saran"]:
            print(f"      -> {item['saran']}")
    print("--------------------------------------------------------------------------")
    if gagal:
        print(f"HASIL: {len(gagal)} masalah ditemukan. Ikuti saran di atas.")
        print("Jika masih gagal, jalankan setup.bat lalu ulangi cek.bat.")
        return 1
    print("HASIL: semua pemeriksaan lulus. Aplikasi siap dijalankan dengan run.bat.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
