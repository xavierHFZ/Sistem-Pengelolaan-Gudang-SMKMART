@echo off
chcp 65001 >nul
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "PERBAIKI=0"
if /i "%~1"=="--auto-repair" set "PERBAIKI=1"

if not exist ".venv\Scripts\python.exe" (
    echo [i] Virtual environment belum ada. Menyiapkan dulu...
    echo.
    call setup.bat --auto
    set "KODE=!ERRORLEVEL!"
) else (
    ".venv\Scripts\python.exe" cek_lingkungan.py
    set "KODE=!ERRORLEVEL!"
)

if not "!KODE!"=="0" (
    echo.
    if "!PERBAIKI!"=="1" (
        echo [i] Menjalankan perbaikan otomatis...
        call setup.bat --auto
        set "KODE=!ERRORLEVEL!"
    ) else (
        choice /c YN /n /m "Jalankan perbaikan otomatis sekarang? [Y/N]: "
        if !ERRORLEVEL! LSS 2 (
            echo.
            echo [i] Menjalankan perbaikan otomatis...
            call setup.bat --auto
            set "KODE=!ERRORLEVEL!"
        )
    )
)

echo.
if not "!KODE!"=="0" (
    echo [!] Lingkungan belum siap. Jalankan setup.bat secara manual.
) else (
    echo [V] Lingkungan siap. Jalankan run.bat untuk membuka aplikasi.
)
pause
exit /b !KODE!
