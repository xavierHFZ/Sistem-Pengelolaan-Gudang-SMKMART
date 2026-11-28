@echo off
chcp 65001 >nul
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "AUTO=0"
if /i "%~1"=="--auto" set "AUTO=1"
set "VENV_PY=.venv\Scripts\python.exe"
set "PY_EXE="

echo ============================================================
echo   SETUP SMKMART (ALL IN ONE)
echo ============================================================
echo.

call :cari_python
if defined PY_EXE goto :python_siap
call :tawarkan_pasang_python

:python_siap
if not defined PY_EXE goto :petunjuk_python

echo [i] Python ditemukan:
"%PY_EXE%" -c "import sys; print('    ' + sys.executable); print('    versi ' + sys.version.split()[0])"
if errorlevel 1 (
    set "PY_EXE="
    call :cari_python
    if not defined PY_EXE goto :petunjuk_python
)

rem ---------------------------------------------------------------
rem 1. Virtual environment (buat ulang bila rusak)
rem ---------------------------------------------------------------
if exist "%VENV_PY%" (
    "%VENV_PY%" -c "import sys" >nul 2>nul
    if errorlevel 1 (
        echo [X] Virtual environment lama rusak. Membuat ulang...
        rmdir /s /q ".venv" >nul 2>nul
    )
)

if not exist "%VENV_PY%" (
    echo [1/5] Membuat virtual environment .venv ...
    "%PY_EXE%" -m venv ".venv"
    if errorlevel 1 (
        echo [X] Gagal membuat virtual environment.
        echo     Gunakan Python dari https://www.python.org/downloads/windows/
        goto :selesai_gagal
    )
) else (
    echo [1/5] Virtual environment .venv sudah siap.
)

rem ---------------------------------------------------------------
rem 2. Pastikan pip tersedia di dalam venv
rem ---------------------------------------------------------------
echo [2/5] Memastikan pip tersedia di .venv ...
call :pastikan_pip
if errorlevel 1 goto :selesai_gagal

rem ---------------------------------------------------------------
rem 3. Selaraskan requirements.txt dengan import di kode
rem ---------------------------------------------------------------
echo [3/5] Memperbarui requirements.txt dari import di kode ...
"%VENV_PY%" update_requirements.py
if errorlevel 1 (
    echo [X] Gagal memperbarui requirements.txt.
    goto :selesai_gagal
)

rem ---------------------------------------------------------------
rem 4. Pasang dependensi. Pip hanya mengunduh yang benar-benar
rem    belum ada, jadi proses ini cepat saat dijalankan ulang.
rem ---------------------------------------------------------------
echo [4/5] Memeriksa dan memasang dependensi ...
"%VENV_PY%" -m pip install --disable-pip-version-check --no-input -r requirements.txt
if errorlevel 1 (
    echo [X] Pemasangan gagal. Memperbarui pip lalu mengulang ...
    "%VENV_PY%" -m pip install --disable-pip-version-check --no-input --upgrade pip
    "%VENV_PY%" -m pip install --disable-pip-version-check --no-input -r requirements.txt
    if errorlevel 1 (
        echo [X] Dependensi tetap gagal dipasang. Periksa koneksi internet.
        goto :selesai_gagal
    )
)

rem ---------------------------------------------------------------
rem 5. Verifikasi nyata di dalam venv
rem ---------------------------------------------------------------
echo [5/5] Memverifikasi lingkungan ...
"%VENV_PY%" cek_lingkungan.py
if errorlevel 1 (
    echo.
    echo [X] Verifikasi menemukan masalah. Perbaiki sesuai saran di atas.
    goto :selesai_gagal
)

echo.
echo [V] Setup selesai dan terverifikasi.
echo     Jalankan aplikasi dengan: run.bat
if "%AUTO%"=="0" pause
exit /b 0

rem =====================================================================
rem pip: cek, lalu pasang lewat ensurepip atau get-pip.py
rem =====================================================================
:pastikan_pip
"%VENV_PY%" -m pip --version >nul 2>nul
if not errorlevel 1 (
    echo [V] pip sudah tersedia.
    exit /b 0
)

echo [X] pip belum ada di .venv. Memasang lewat ensurepip ...
"%VENV_PY%" -m ensurepip --upgrade >nul 2>nul
"%VENV_PY%" -m pip --version >nul 2>nul
if not errorlevel 1 (
    echo [V] pip berhasil dipasang lewat ensurepip.
    exit /b 0
)

echo [i] ensurepip tidak tersedia. Mengunduh get-pip.py ...
set "GET_PIP=%TEMP%\smkmart-get-pip.py"
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -UseBasicParsing 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%GET_PIP%' } catch { exit 1 }"
if errorlevel 1 (
    echo [X] Gagal mengunduh get-pip.py. Periksa koneksi internet.
    exit /b 1
)
"%VENV_PY%" "%GET_PIP%" --no-warn-script-location
set "HASIL_PIP=%ERRORLEVEL%"
del "%GET_PIP%" >nul 2>nul
if not "%HASIL_PIP%"=="0" (
    echo [X] Gagal memasang pip lewat get-pip.py.
    exit /b 1
)

"%VENV_PY%" -m pip --version >nul 2>nul
if errorlevel 1 (
    echo [X] pip masih belum bisa dijalankan.
    exit /b 1
)
echo [V] pip berhasil dipasang lewat get-pip.py.
exit /b 0

rem =====================================================================
rem Tawarkan pemasangan Python otomatis (hanya saat interaktif)
rem =====================================================================
:tawarkan_pasang_python
if defined PY_EXE exit /b 0
echo.
echo [X] Python 3 belum terdeteksi di komputer ini.
if "%AUTO%"=="1" (
    echo     Mode otomatis tidak memasang Python tanpa persetujuan.
    echo     Jalankan setup.bat secara manual lalu pilih Y.
    exit /b 0
)
choice /c YN /n /m "Pasang Python otomatis sekarang? [Y/N]: "
if errorlevel 2 exit /b 0
call :pasang_python
exit /b 0

:pasang_python
echo.
echo [i] Mencoba memasang Python otomatis (butuh koneksi internet) ...
where winget >nul 2>nul
if not errorlevel 1 (
    echo [i] Memasang Python 3.13 lewat winget ...
    winget install --exact --id Python.Python.3.13 --source winget --silent --accept-package-agreements --accept-source-agreements
    call :cari_python
    if defined PY_EXE (
        echo [V] Python berhasil dipasang lewat winget.
        exit /b 0
    )
    echo [i] Percobaan pertama belum berhasil. Mencoba Python 3.12 ...
    winget install --exact --id Python.Python.3.12 --source winget --silent --accept-package-agreements --accept-source-agreements
    call :cari_python
    if defined PY_EXE (
        echo [V] Python berhasil dipasang lewat winget.
        exit /b 0
    )
)

echo [i] Mengunduh installer resmi dari python.org ...
set "INSTALLER=%TEMP%\smkmart-python-installer.exe"
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -UseBasicParsing 'https://www.python.org/ftp/python/3.13.5/python-3.13.5-amd64.exe' -OutFile '%INSTALLER%' } catch { exit 1 }"
if errorlevel 1 (
    echo [X] Gagal mengunduh installer Python.
    exit /b 1
)
echo [i] Memasang Python untuk pengguna saat ini (tanpa admin) ...
"%INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_launcher=1
del "%INSTALLER%" >nul 2>nul
call :cari_python
if defined PY_EXE (
    echo [V] Python berhasil dipasang.
) else (
    echo [X] Pemasangan selesai tetapi Python belum terdeteksi.
    echo     Tutup jendela ini, buka lagi, lalu jalankan setup.bat.
)
exit /b 0

:petunjuk_python
echo.
echo [X] Python 3 belum tersedia sehingga setup tidak bisa dilanjutkan.
echo.
echo     Pilihan:
echo     1. Jalankan setup.bat lagi lalu jawab Y saat ditawari pemasangan otomatis.
echo     2. Pasang manual dari https://www.python.org/downloads/windows/
echo        Centang "Add python.exe to PATH" saat instalasi.
echo     3. Bila memakai Microsoft Store: pasang "Python 3" dari Store,
echo        lalu tutup dan buka kembali terminal.
echo.
echo     Setelah Python terpasang, jalankan setup.bat lagi.
goto :selesai_gagal

:selesai_gagal
echo.
echo [X] Setup belum berhasil.
if "%AUTO%"=="0" pause
exit /b 1

rem =====================================================================
rem Deteksi interpreter: py launcher, PATH, Microsoft Store, dan lokasi
rem umum. Setiap kandidat diuji dengan benar-benar menjalankannya, bukan
rem hanya dicek keberadaan filenya, agar alias Microsoft Store yang
rem belum terpasang tidak dianggap valid.
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
