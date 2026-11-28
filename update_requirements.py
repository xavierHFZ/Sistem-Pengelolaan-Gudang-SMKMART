"""Perbarui requirements.txt otomatis dari import di seluruh berkas .py.

Jalankan setiap kali menambah modul pihak ketiga:

    python update_requirements.py

Skrip ini:
- memindai semua berkas .py di folder proyek (mengabaikan .venv, venv,
  __pycache__, exports, dan folder tersembunyi),
- mengabaikan modul pustaka standar Python dan modul lokal proyek,
- memetakan nama import ke nama paket PyPI yang benar,
- mempertahankan versi yang sudah dipin di requirements.txt (misalnya
  openpyxl>=3.1.5,<4.0 tetap dipertahankan),
- menulis ulang requirements.txt secara rapi dan terurut.
"""

import ast
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS_FILE = os.path.join(BASE_DIR, "requirements.txt")
DILEWATI = {".venv", "venv", "env", "__pycache__", "exports", ".git", ".idea", ".vscode"}

# Nama import -> nama paket di PyPI (untuk kasus yang berbeda).
ALIAS_PAKET = {
    "PIL": "Pillow",
    "cv2": "opencv-python",
    "sklearn": "scikit-learn",
    "yaml": "PyYAML",
    "bs4": "beautifulsoup4",
    "dotenv": "python-dotenv",
    "Crypto": "pycryptodome",
    "OpenSSL": "pyOpenSSL",
    "dateutil": "python-dateutil",
    "fitz": "PyMuPDF",
    "docx": "python-docx",
    "pptx": "python-pptx",
    "serial": "pyserial",
    "win32com": "pywin32",
    "win32api": "pywin32",
    "mysql": "mysql-connector-python",
    "psycopg2": "psycopg2-binary",
    "jwt": "PyJWT",
    "magic": "python-magic",
    "reportlab": "reportlab",
    "qrcode": "qrcode",
    "barcode": "python-barcode",
    "pyzbar": "pyzbar",
}


def nama_modul_lokal():
    """Kumpulkan nama berkas .py lokal agar tidak dianggap paket eksternal."""
    lokal = set()
    for nama in os.listdir(BASE_DIR):
        if nama.endswith(".py"):
            lokal.add(nama[:-3].lower())
    return lokal


def kumpulkan_import():
    """Ambil semua nama modul tingkat atas yang diimpor di berkas .py."""
    ditemukan = set()
    lokal = nama_modul_lokal()
    for akar, folder, berkas in os.walk(BASE_DIR):
        folder[:] = [
            f for f in folder
            if f not in DILEWATI and not f.startswith(".")
        ]
        for nama in berkas:
            if not nama.endswith(".py"):
                continue
            lokasi = os.path.join(akar, nama)
            try:
                with open(lokasi, "r", encoding="utf-8-sig") as file:
                    pohon = ast.parse(file.read(), filename=lokasi)
            except (SyntaxError, OSError) as error:
                print(f"[!] Lewati {nama}: {error}")
                continue

            for simpul in ast.walk(pohon):
                if isinstance(simpul, ast.Import):
                    for alias in simpul.names:
                        ditemukan.add(alias.name.split(".")[0])
                elif isinstance(simpul, ast.ImportFrom):
                    if simpul.level == 0 and simpul.module:
                        ditemukan.add(simpul.module.split(".")[0])

    standar = set(getattr(sys, "stdlib_module_names", set()))
    if not standar:
        # Cadangan untuk Python < 3.10 yang belum punya sys.stdlib_module_names.
        standar = {
            "abc", "argparse", "array", "ast", "asyncio", "base64", "binascii",
            "bisect", "bz2", "calendar", "cgi", "codecs", "collections", "contextlib",
            "copy", "csv", "ctypes", "dataclasses", "datetime", "dbm", "decimal",
            "difflib", "dis", "email", "enum", "errno", "filecmp", "fnmatch",
            "fractions", "functools", "gc", "getpass", "gettext", "glob", "gzip",
            "hashlib", "heapq", "hmac", "html", "http", "importlib", "inspect", "io",
            "itertools", "json", "keyword", "locale", "logging", "lzma", "marshal",
            "math", "mmap", "msvcrt", "multiprocessing", "nt", "ntpath", "operator",
            "os", "pathlib", "pickle", "pkgutil", "platform", "plistlib", "pprint",
            "queue", "random", "re", "sched", "secrets", "select", "selectors",
            "shelve", "shlex", "shutil", "signal", "site", "socket", "sqlite3",
            "ssl", "stat", "statistics", "string", "struct", "subprocess", "sys",
            "tarfile", "tempfile", "textwrap", "threading", "time", "tokenize",
            "traceback", "types", "typing", "unicodedata", "unittest", "urllib",
            "uuid", "venv", "warnings", "weakref", "webbrowser", "winreg",
            "winsound", "xml", "zipfile", "zlib",
        }
    hasil = set()
    for nama in ditemukan:
        if not nama or nama in standar or nama.lower() in lokal:
            continue
        hasil.add(ALIAS_PAKET.get(nama, nama))
    return hasil


def baca_versi_tersimpan():
    """Baca baris paket yang sudah ada agar versi/pin-nya tidak hilang."""
    tersimpan = {}
    if not os.path.exists(REQUIREMENTS_FILE):
        return tersimpan
    with open(REQUIREMENTS_FILE, "r", encoding="utf-8") as file:
        for baris in file:
            baris = baris.strip()
            if not baris or baris.startswith("#"):
                continue
            nama = baris
            for pemisah in ("==", ">=", "<=", "~=", ">", "<", "!=", "["):
                if pemisah in nama:
                    nama = nama.split(pemisah, 1)[0]
                    break
            tersimpan[nama.strip().lower()] = baris
    return tersimpan


def tulis_requirements(daftar_paket):
    versi_tersimpan = baca_versi_tersimpan()
    baris_paket = []
    for paket in sorted(daftar_paket, key=str.lower):
        baris_paket.append(versi_tersimpan.get(paket.lower(), paket))

    dengan_header = [
        "# ===========================================================================",
        "# Dependensi pihak ketiga SMKMART (dibuat otomatis oleh update_requirements.py)",
        "# ---------------------------------------------------------------------------",
        "# Pasang semua dependensi sekaligus:",
        "#     pip install -r requirements.txt",
        "#",
        "# Setelah menambah modul baru di kode, perbarui daftar ini dengan:",
        "#     python update_requirements.py",
        "#",
        "# Modul pustaka standar Python tidak perlu dicantumkan di sini.",
        "# ===========================================================================",
        "",
    ]
    isi = "\n".join(dengan_header + baris_paket).rstrip() + "\n"
    with open(REQUIREMENTS_FILE, "w", encoding="utf-8") as file:
        file.write(isi)


def main():
    paket = kumpulkan_import()
    if not paket:
        print("[i] Tidak ada dependensi pihak ketiga yang terdeteksi.")
    tulis_requirements(paket)
    print(f"[V] requirements.txt diperbarui ({len(paket)} paket):")
    for baris in sorted(paket, key=str.lower):
        print(f"    - {baris}")


if __name__ == "__main__":
    main()
