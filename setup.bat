@echo off
chcp 65001 >nul
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "AUTO=0"
if /i "%~1"=="--auto" set "AUTO=1"
set "VENV_PY=.venv\Scripts\python.exe"
set "PY_EXE="

echo ============================================================
echo   SETUP SMKMART
echo ============================================================
echo.

call :cari_python
if not defined PY_EXE goto :tanpa_python

echo [i] Python ditemukan:
"%PY_EXE%" -c "import sys; print('    ' + sys.executable); print('    versi ' + sys.version.split()[0])"
if errorlevel 1 goto :tanpa_python

rem ---------------------------------------------------------------
rem 1. Virtual environment (buat ulang bila rusak)
rem ---------------------------------------------------------------
if exist "%VENV_PY%" (
    "%VENV_PY%" -c "import sys" >nul 2>nul
    if errorlevel 1 (
        echo [!] Virtual environment lama rusak. Membuat ulang...
        rmdir /s /q ".venv" >nul 2>nul
    )
)

if not exist "%VENV_PY%" (
    echo [1/4] Membuat virtual environment .venv ...
    "%PY_EXE%" -m venv ".venv"
    if errorlevel 1 (
        echo [!] Gagal membuat virtual environment.
        echo     Gunakan Python dari https://www.python.org/downloads/windows/
        goto :selesai_gagal
    )
) else (
    echo [1/4] Virtual environment .venv sudah siap.
)

rem ---------------------------------------------------------------
rem 2. Selaraskan requirements.txt dengan import di kode
rem ---------------------------------------------------------------
echo [2/4] Memperbarui requirements.txt dari import di kode ...
"%VENV_PY%" update_requirements.py
if errorlevel 1 (
    echo [!] Gagal memperbarui requirements.txt.
    goto :selesai_gagal
)

rem ---------------------------------------------------------------
rem 3. Pasang dependensi. Pip hanya mengunduh yang benar-benar
rem    belum ada, jadi proses ini cepat saat dijalankan ulang.
rem ---------------------------------------------------------------
echo [3/4] Memeriksa dan memasang dependensi ...
"%VENV_PY%" -m pip install --disable-pip-version-check --no-input -r requirements.txt
if errorlevel 1 (
    echo [!] Pemasangan gagal. Mencoba memperbarui pip lalu mengulang ...
    "%VENV_PY%" -m pip install --disable-pip-version-check --no-input --upgrade pip
    "%VENV_PY%" -m pip install --disable-pip-version-check --no-input -r requirements.txt
    if errorlevel 1 (
        echo [!] Dependensi tetap gagal dipasang. Periksa koneksi internet.
        goto :selesai_gagal
    )
)

rem ---------------------------------------------------------------
rem 4. Verifikasi nyata di dalam venv
rem ---------------------------------------------------------------
echo [4/4] Memverifikasi lingkungan ...
"%VENV_PY%" cek_lingkungan.py
if errorlevel 1 (
    echo.
    echo [!] Verifikasi menemukan masalah. Perbaiki sesuai saran di atas.
    goto :selesai_gagal
)

echo.
echo [V] Setup selesai dan terverifikasi.
echo     Jalankan aplikasi dengan: run.bat
if "%AUTO%"=="0" pause
exit /b 0

:tanpa_python
echo [!] Python 3 tidak ditemukan atau tidak bisa dijalankan.
echo.
echo     Cara memperbaiki:
echo     1. Unduh Python dari https://www.python.org/downloads/windows/
echo     2. Saat instalasi, centang "Add python.exe to PATH".
echo     3. Tutup jendela ini, lalu jalankan setup.bat lagi.
echo.
echo     Python dari Microsoft Store juga bisa dipakai asalkan sudah
echo     benar-benar terpasang. Buka Microsoft Store, pasang "Python 3",
echo     lalu jalankan perintah "python --version" di terminal untuk memastikan.
echo.
echo     Jika baru memasang Python, tutup semua jendela terminal agar PATH
echo     terbaru terbaca.
goto :selesai_gagal

:selesai_gagal
echo.
echo [!] Setup belum berhasil.
if "%AUTO%"=="0" pause
exit /b 1

rem =====================================================================
rem Deteksi interpreter: py launcher, PATH, Microsoft Store, dan lokasi
rem umum. Setiap kandidat diuji dengan menjalankannya, bukan hanya
rem dicek keberadaan filenya, agar alias Microsoft Store yang belum
rem terpasang tidak dianggap valid.
rem =====================================================================
:cari_python
if defined PY_EXE exit /b 0
call :probe py -3
if defined PY_EXE exit /b 0
call :probe python
if defined PY_EXE exit /b 0
call :probe python3
if defined PY_EXE exit /b 0

for /d %%D in ("%LocalAppData%\Programs\Python\Python3*") do (
    if not defined PY_EXE if exist "%%~fD\python.exe" call :probe "%%~fD\python.exe"
)
for /d %%D in ("%ProgramFiles%\Python3*") do (
    if not defined PY_EXE if exist "%%~fD\python.exe" call :probe "%%~fD\python.exe"
)
for /d %%D in ("C:\Python3*") do (
    if not defined PY_EXE if exist "%%~fD\python.exe" call :probe "%%~fD\python.exe"
)
exit /b 0

:probe
if defined PY_EXE exit /b 0
for /f "delims=" %%P in ('%* -c "import sys; print(sys.executable)" 2^>nul') do (
    if exist "%%P" set "PY_EXE=%%P"
)
exit /b 0
