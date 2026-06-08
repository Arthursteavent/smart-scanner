[Setup]
AppName=Smart Scanner
AppVersion=1.0
DefaultDirName={pf}\Smart Scanner
DefaultGroupName=Smart Scanner
UninstallDisplayIcon={app}\SmartScanner.exe
Compression=lzma2
SolidCompression=yes
OutputDir=userdocs:Inno Setup Examples Output
OutputBaseFilename=SmartScanner_Installer

[Files]
Source: "dist\SmartScanner\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Smart Scanner"; Filename: "{app}\SmartScanner.exe"
Name: "{commondesktop}\Smart Scanner"; Filename: "{app}\SmartScanner.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked
