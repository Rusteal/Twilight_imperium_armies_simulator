[Setup]
AppId={{23A67D65-1A2B-43E1-9005-5C5EC1D3C78B}}  ; Random GUID
AppName=Twilight Imperium Simulator
AppVersion=1.0
AppPublisher=YourName
DefaultDirName={pf}\TI_Simulator
DefaultGroupName=TI Simulator
OutputBaseFilename=TI_Installer
OutputDir=dist
Compression=lzma
SolidCompression=yes
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\ui.exe
UninstallDisplayName=Twilight Imperium Simulator
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "ukrainian"; MessagesFile: "compiler:Languages\Ukrainian.isl"

[Files]
Source: "dist\ui.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Twilight Imperium Simulator"; Filename: "{app}\ui.exe"
Name: "{autodesktop}\Twilight Imperium Simulator"; Filename: "{app}\ui.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\ui.exe"; Description: "Launch Twilight Imperium Simulator"; Flags: nowait postinstall skipifsilent
