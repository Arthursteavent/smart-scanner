#!/bin/bash
echo "Building Smart Scanner for macOS..."

# Install requirements
echo "Installing requirements..."
python3 -m pip install -r requirements.txt

# Check if pyinstaller is installed
if ! python3 -m pip show pyinstaller > /dev/null 2>&1; then
    echo "PyInstaller not found. Installing..."
    python3 -m pip install pyinstaller
fi

# Run PyInstaller
echo "Running PyInstaller..."
# Perhatikan penggunaan titik dua (:) pada --add-data khusus untuk macOS/Linux
python3 -m PyInstaller --noconfirm --onedir --windowed --name "SmartScanner" --add-data "config.json:." --add-data "core/keywords.json:core" main.py

echo ""
echo "Build complete! The application is located in the 'dist' folder."
echo "You can find 'SmartScanner.app' inside which can be run natively on macOS."
