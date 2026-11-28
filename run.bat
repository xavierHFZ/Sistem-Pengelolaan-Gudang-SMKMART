@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [i] Menyiapkan aplikasi untuk pertama kali...
    echo.
    call setup.bat --auto
    if errorlevel 1 (
        echo.
        echo [!] Persiapan gagal. Jalankan setup.bat secara manual untuk detail.
        pause
        exit /b 1
    )
)

".venv\Scripts\python.exe" cek_lingkungan.py --ringkas >nul 2>nul
if errorlevel 1 (
    echo [i] Lingkungan belum lengkap, memperbaiki otomatis...
    echo.
    call setup.bat --auto
    if errorlevel 1 (
        echo.
        echo [!] Perbaikan gagal. Jalankan cek.bat untuk melihat diagnosa.
        pause
        exit /b 1
    )
)

".venv\Scripts\python.exe" "sistem gudang.py"
set "KODE=%ERRORLEVEL%"
if not "%KODE%"=="0" (
    echo.
    echo [!] Aplikasi berhenti dengan kode %KODE%.
    echo     Jalankan cek.bat untuk melihat diagnosa lingkungan.
    pause
)
exit /b %KODE%
