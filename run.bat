@echo off
chcp 65001 >nul
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" "sistem gudang.py"
) else (
    python "sistem gudang.py"
)

pause
