#define AppVersion "0.0.1"
#define CurrentDate GetDateTimeString('yyyy-mm-dd', '-', ':')

[Setup]
AppName=PhyloForester
AppVersion={#AppVersion}
DefaultDirName={commonpf}\PaleoBytes\PhyloForester
OutputDir=Output

OutputBaseFilename=PhyloForester_v{#AppVersion}_Installer

[Files]
; Include main executable
Source: "..\dist\PhyloForester\PhyloForester.exe"; DestDir: "{app}"

; Include all other files and directories
Source: "..\dist\PhyloForester\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Run]
Filename: "{app}\PhyloForester.exe"; Flags: postinstall shellexec

[Code]
function InitializeSetup(): Boolean;
begin
  // Create a specific Start Menu group
  if not DirExists(ExpandConstant('{userprograms}\PaleoBytes\PhyloForester')) then
    CreateDir(ExpandConstant('{userprograms}\PaleoBytes\PhyloForester'));
  
  Result := True;
end;

[Icons]
Name: "{userprograms}\PaleoBytes\PhyloForester"; Filename: "{app}\PhyloForester.exe"
