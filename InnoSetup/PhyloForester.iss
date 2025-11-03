; PhyloForester Inno Setup Script
; Version is read from environment variable or defaults to current version

#ifndef AppVersion
  #define AppVersion GetEnv("PHYLOFORESTER_VERSION")
  #if AppVersion == ""
    #define AppVersion "0.1.0"
  #endif
#endif

#define AppName "PhyloForester"
#define AppPublisher "PaleoBytes"
#define AppURL "https://github.com/jikhanjung/PhyloForester"
#define AppExeName "PhyloForester.exe"

[Setup]
; Basic application info
AppId={{8F9C7D6E-5B4A-3C2D-1E0F-9A8B7C6D5E4F}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}

; Installation directories
DefaultDirName={autopf}\{#AppPublisher}\{#AppName}
DefaultGroupName={#AppPublisher}\{#AppName}
DisableProgramGroupPage=yes

; Output configuration
OutputDir=Output
OutputBaseFilename=PhyloForester-Setup-v{#AppVersion}

; Compression
Compression=lzma2
SolidCompression=yes

; Modern UI
WizardStyle=modern

; Privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Architecture
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; Uninstaller
UninstallDisplayIcon={app}\{#AppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Main executable
Source: "..\dist\PhyloForester\PhyloForester.exe"; DestDir: "{app}"; Flags: ignoreversion

; All other files and directories
Source: "..\dist\PhyloForester\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu icons
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"

; Desktop icon (optional)
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
; Option to launch application after installation
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up any files created by the application
Type: filesandordirs; Name: "{localappdata}\{#AppPublisher}\{#AppName}"
