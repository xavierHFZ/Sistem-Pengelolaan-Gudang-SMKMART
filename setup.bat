@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo ============================================================
echo   SETUP SMKMART
echo ============================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [!] Python tidak ditemukan.
    echo     Pasang Python 3 dari https://www.python.org/downloads/
    echo     Saat memasang, centang "Add Python to PATH".
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo [1/4] Membuat virtual environment .venv ...
    python -m venv .venv
    if errorlevel 1 (
        echo [!] Gagal membuat virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [1/4] Virtual environment .venv sudah ada.
)

echo [2/4] Memperbarui requirements.txt dari import di kode ...
".venv\Scripts\python.exe" update_requirements.py

echo [3/4] Memperbarui pip ...
".venv\Scripts\python.exe" -m pip install --upgrade pip

echo [4/4] Memasang dependensi dari requirements.txt ...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [!] Gagal memasang dependensi.
    pause
    exit /b 1
)

echo.
echo [V] Setup selesai.
echo     Jalankan aplikasi dengan: run.bat
echo.
pause
