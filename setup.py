from setuptools import setup
import sys

# Script ini khusus untuk build di macOS menggunakan py2app
if sys.platform != 'darwin':
    print("Script setup.py ini dirancang khusus untuk macOS (py2app).")
    print("Gunakan PyInstaller untuk build di sistem operasi lain.")
    sys.exit(1)

APP = ['main.py']

# Menambahkan file pendukung yang dibutuhkan saat runtime
DATA_FILES = [
    'config.json',
    ('core', ['core/keywords.json'])
]

# Konfigurasi py2app
OPTIONS = {
    'argv_emulation': False, # Set False untuk menghindari beberapa isu kompatibilitas dengan GUI modern
    'packages': ['customtkinter', 'requests', 'pydantic', 'PyPDF2', 'docx'],
    # 'iconfile': 'assets/icon.icns', # Hilangkan komentar ini jika nanti punya file icon khusus Mac (.icns)
}

setup(
    name="SmartScanner",
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
