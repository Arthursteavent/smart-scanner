#!/bin/bash
echo "=========================================="
echo " Building Smart Scanner for macOS (py2app)"
echo "=========================================="

# Pastikan script dijalankan di macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: Script ini hanya bisa dijalankan di sistem operasi macOS."
    exit 1
fi

echo "[1/4] Menginstall dependencies dari requirements.txt..."
python3 -m pip install -r requirements.txt

echo "[2/4] Menginstall py2app..."
python3 -m pip install py2app

echo "[3/4] Membersihkan folder build sebelumnya (jika ada)..."
rm -rf build dist

echo "[4/4] Memulai proses build dengan py2app..."
python3 setup.py py2app

echo ""
echo "=========================================="
echo " Build Selesai!"
echo "=========================================="
echo "Aplikasi Anda berada di folder 'dist'."
echo "Silakan cek file bernama 'SmartScanner.app'."
