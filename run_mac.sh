#!/bin/bash
echo "Menjalankan Smart Scanner..."

VENV_DIR="venv"

# 1. Cek apakah Virtual Environment sudah ada
if [ ! -d "$VENV_DIR" ]; then
    echo "Pertama kali dijalankan: Membuat Virtual Environment..."
    python3 -m venv "$VENV_DIR"
    
    echo "Menginstal library yang dibutuhkan (ini hanya dilakukan sekali)..."
    "$VENV_DIR/bin/python" -m pip install --upgrade pip
    "$VENV_DIR/bin/python" -m pip install -r requirements.txt
fi

# 2. Jalankan aplikasi
echo "Membuka aplikasi..."
"$VENV_DIR/bin/python" main.py
