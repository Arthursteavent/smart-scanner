@echo off
echo Menjalankan Smart Scanner...

set VENV_DIR=venv

:: 1. Cek apakah Virtual Environment sudah ada
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Pertama kali dijalankan: Membuat Virtual Environment...
    python -m venv "%VENV_DIR%"
    
    echo Menginstal library yang dibutuhkan (ini hanya dilakukan sekali)...
    "%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip
    "%VENV_DIR%\Scripts\python.exe" -m pip install -r requirements.txt
)

:: 2. Jalankan aplikasi
echo Membuka aplikasi...
"%VENV_DIR%\Scripts\python.exe" main.py
