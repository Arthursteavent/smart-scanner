import os
import sys
import subprocess
import platform

def run_cmd(cmd):
    print(f"Running: {cmd}")
    subprocess.check_call(cmd, shell=True)

def main():
    print("=== Smart Scanner Installer Builder ===")
    
    # Determine the correct python command (python for Windows, python3 for Mac/Linux)
    python_cmd = "python" if platform.system() == "Windows" else "python3"

    # 1. Install Requirements
    print("\n[1/3] Installing requirements...")
    run_cmd(f"{python_cmd} -m pip install -r requirements.txt")
    
    # 2. Check & Install PyInstaller
    print("\n[2/3] Checking PyInstaller...")
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        run_cmd(f"{python_cmd} -m pip install pyinstaller")

    # 3. Build the Application
    print("\n[3/3] Building the application executable...")
    
    # Windows uses ';' to separate paths, Mac/Linux uses ':'
    separator = ";" if platform.system() == "Windows" else ":"
    
    # We use --onefile on Windows for a single .exe, 
    # but on Mac we use --onedir to properly generate the .app folder format
    if platform.system() == "Windows":
        cmd = f'{python_cmd} -m PyInstaller --noconfirm --onefile --windowed --name "SmartScanner" --add-data "config.json{separator}." --add-data "core/keywords.json{separator}core" main.py'
    else:
        cmd = f'{python_cmd} -m PyInstaller --noconfirm --onedir --windowed --name "SmartScanner" --add-data "config.json{separator}." --add-data "core/keywords.json{separator}core" main.py'

    run_cmd(cmd)

    print("\n=== Build Complete! ===")
    if platform.system() == "Windows":
        print("Sukses! Anda bisa menemukan file 'SmartScanner.exe' di dalam folder 'dist'.")
        print("Satu file tersebut siap untuk langsung dibagikan dan digunakan.")
    else:
        print("Sukses! Anda bisa menemukan aplikasi 'SmartScanner.app' di dalam folder 'dist'.")
        print("File tersebut siap untuk langsung digunakan di Mac Anda.")

if __name__ == "__main__":
    main()
