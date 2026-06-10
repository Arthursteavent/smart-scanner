@echo off
echo Building Smart Scanner Executable...

:: Install requirements
echo Installing requirements...
python -m pip install -r requirements.txt

:: Check if pyinstaller is installed
python -m pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
)

:: Run PyInstaller
echo Running PyInstaller...
python -m PyInstaller --noconfirm --onefile --windowed --name "SmartScanner" --add-data "config.json;." --add-data "core/keywords.json;core" --add-data "web;web" main.py

echo.
echo Build complete! The executable is located in the "dist\SmartScanner" folder.
echo To create an installer, you can use Inno Setup with the provided setup.iss file.
