#!/bin/bash
echo "=========================================="
echo " Building Smart Scanner for macOS..."
echo "=========================================="

# Pastikan script dijalankan di macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: Script ini hanya bisa dijalankan di sistem operasi macOS."
    exit 1
fi

VENV_DIR="build_env_mac_314"

# 1. Create Virtual Environment to avoid PEP 668 (externally-managed-environment) errors
if [ ! -d "$VENV_DIR" ]; then
    echo "[1/4] Creating Virtual Environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "[1/4] Virtual Environment already exists."
fi

PYTHON_CMD="$VENV_DIR/bin/python"

# 2. Install Requirements
echo "[2/4] Installing requirements..."
"$PYTHON_CMD" -m pip install -r requirements.txt

# 3. Check & Install PyInstaller
echo "[3/4] Installing PyInstaller..."
"$PYTHON_CMD" -m pip install pyinstaller

# 4. Build the Application
echo "[4/4] Building the application executable..."
rm -rf build dist
"$PYTHON_CMD" -m PyInstaller --noconfirm --onedir --windowed --name "SmartScanner" --add-data "config.json:." --add-data "core/keywords.json:core" main.py

# 5. Packaging into .dmg
echo "Packaging dist/SmartScanner.dmg..."
STAGE="$(mktemp -d)/dmg"
mkdir -p "$STAGE"
cp -R "dist/SmartScanner.app" "$STAGE/"
ln -s /Applications "$STAGE/Applications"
rm -f "dist/SmartScanner.dmg"
hdiutil create -volname "SmartScanner" -srcfolder "$STAGE" -ov -format UDZO "dist/SmartScanner.dmg" >/dev/null
rm -rf "$STAGE"

echo ""
echo "=========================================="
echo " Build Complete!"
echo "=========================================="
echo "Aplikasi Anda berada di folder 'dist'."
echo "Silakan cek file bernama:"
echo "  - dist/SmartScanner.app (Aplikasi langsung)"
echo "  - dist/SmartScanner.dmg (Disk image untuk didistribusikan)"
echo ""
echo "Anda bisa membagikan berkas 'SmartScanner.dmg' kepada pengguna Mac lain."


