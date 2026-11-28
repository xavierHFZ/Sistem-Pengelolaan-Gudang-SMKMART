@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [i] Virtual environment belum ada. Menyiapkan dulu...
    echo.
    call setup.bat --auto
) else (
    ".venv\Scripts\python.exe" cek_lingkungan.py
)

set "KODE=%ERRORLEVEL%"
echo.
if not "%KODE%"=="0" (
    echo [!] Lingkungan belum siap. Jalankan setup.bat untuk memperbaiki.
) else (
    echo [V] Lingkungan siap. Jalankan run.bat untuk membuka aplikasi.
)
pause
exit /b %KODE%
