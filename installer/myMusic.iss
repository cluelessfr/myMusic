#define MyAppName "myMusic"
#define MyAppVersion "2.0.0"
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
Compression=lzma2/normal
SolidCompression=no
LZMANumBlockThreads=4
LZMAUseSeparateProcess=yes
CloseApplications=yes
CloseApplicationsFilter=*.exe,*.dll
WizardStyle=modern
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\{#MyAppExeName}
InfoBeforeFile=spicetify-prerequisite.txt
InfoAfterFile=..\THIRD_PARTY_NOTICES.md

[Files]
Source: "..\dist\myMusic\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\THIRD_PARTY_NOTICES.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\licenses\Spicetify-LGPL-2.1.txt"; DestDir: "{app}\licenses"; Flags: ignoreversion

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
Type: filesandordirs; Name: "{localappdata}\{#MyAppName}"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked
Name: "startup"; Description: "Start myMusic with Windows"; GroupDescription: "Startup:"

[Icons]
Name: "{group}\myMusic"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall myMusic"; Filename: "{uninstallexe}"
Name: "{autodesktop}\myMusic"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: Software\Classes\mymusic; ValueType: string; ValueName: ""; ValueData: "URL: myMusic Protocol"; Flags: uninsdeletekey
Root: HKCU; Subkey: Software\Classes\mymusic; ValueType: string; ValueName: "URL Protocol"; ValueData: ""
Root: HKCU; Subkey: Software\Classes\mymusic\DefaultIcon; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKCU; Subkey: Software\Classes\mymusic\shell\open\command; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKCU; Subkey: Software\Microsoft\Windows\CurrentVersion\Run; ValueType: string; ValueName: "myMusic"; ValueData: """{app}\{#MyAppExeName}"" --background"; Flags: uninsdeletevalue; Tasks: startup
Root: HKCU; Subkey: Software\Microsoft\Windows\CurrentVersion\Run; ValueType: none; ValueName: "myMusic"; Flags: deletevalue; Tasks: not startup

[Run]
Filename: "{app}\{#MyAppExeName}"; Parameters: "--install-spicetify";  StatusMsg: "Installing Spotify integration..."; Flags: runhidden waituntilterminated runasoriginaluser
Filename: "{app}\{#MyAppExeName}"; Parameters: "--background"; Flags: nowait runasoriginaluser skipifnotsilent
Filename: "{app}\{#MyAppExeName}"; Description: "Launch myMusic"; Flags: nowait postinstall runasoriginaluser skipifsilent

[UninstallRun]
Filename: "{app}\{#MyAppExeName}"; Parameters: "--uninstall-spicetify"; Flags: runhidden waituntilterminated skipifdoesntexist; RunOnceId: "RemoveMyMusicSpicetifyIntegration"
