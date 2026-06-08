import os
import sys
import subprocess
import platform

def run_cmd(cmd):
    print(f"Running: {cmd}")
    subprocess.check_call(cmd, shell=True)

def main():
    print("=== Smart Scanner Installer Builder ===")
    
    base_python = sys.executable

    # 1. Create Virtual Environment to avoid PEP 668 (externally-managed-environment) errors
    print("\n[1/4] Creating Virtual Environment...")
    venv_dir = "build_env"
    if not os.path.exists(venv_dir):
        run_cmd(f'"{base_python}" -m venv {venv_dir}')
    
    # Get the python executable from inside the virtual environment
    if platform.system() == "Windows":
        python_cmd = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        python_cmd = os.path.join(venv_dir, "bin", "python")

    # 2. Install Requirements
    print("\n[2/4] Installing requirements...")
    run_cmd(f'"{python_cmd}" -m pip install -r requirements.txt')
    
    # 3. Check & Install PyInstaller
    print("\n[3/4] Checking & Installing PyInstaller...")
    run_cmd(f'"{python_cmd}" -m pip install pyinstaller')

    # 4. Build the Application
    print("\n[4/4] Building the application executable...")
    separator = ";" if platform.system() == "Windows" else ":"
    
    if platform.system() == "Windows":
        cmd = f'"{python_cmd}" -m PyInstaller --noconfirm --onefile --windowed --name "SmartScanner" --add-data "config.json{separator}." --add-data "core/keywords.json{separator}core" main.py'
    else:
        cmd = f'"{python_cmd}" -m PyInstaller --noconfirm --onedir --windowed --name "SmartScanner" --add-data "config.json{separator}." --add-data "core/keywords.json{separator}core" main.py'

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
