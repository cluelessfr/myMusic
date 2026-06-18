#define MyAppName "myMusic"
#define MyAppVersion "1.0.0"
#define MyAppExeName "myMusic.exe"

[Setup]
AppId={{7B2B7C81-09A8-4F43-A8A3-9E7F9E0C6A91}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\release
OutputBaseFilename=myMusic-v{#MyAppVersion}-windows-setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\{#MyAppExeName}

[Files]
Source: "..\dist\myMusic\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Icons]
Name: "{group}\myMusic"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall myMusic"; Filename: "{uninstallexe}"
Name: "{autodesktop}\myMusic"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch myMusic"; Flags: nowait postinstall skipifsilent
