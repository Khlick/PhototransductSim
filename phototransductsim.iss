#define AppVersion "0.1.2"

[Setup]
AppName=PhototransductSim
AppVersion={#AppVersion}
DefaultDirName={commonpf64}\PhototransductSim
DefaultGroupName=PhototransductSim
OutputDir=dist
OutputBaseFilename=PhototransductSimInstaller
ArchitecturesInstallIn64BitMode=x64
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\phototransductsim\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\PhototransductSim"; Filename: "{app}\phototransductsim.exe"

[Run]
Filename: "{app}\phototransductsim.exe"; Description: "Launch PhototransductSim"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  AppDataPath: string;
  RemoveSettings: boolean;
begin
  if CurUninstallStep = usUninstall then
  begin
    AppDataPath := ExpandConstant('{localappdata}\DrG\phototransductsim\' + '{#AppVersion}');
    if DirExists(AppDataPath) then
    begin
      RemoveSettings := MsgBox('Do you want to remove the application settings stored in ' + AppDataPath + '?', mbConfirmation, MB_YESNO) = IDYES;
      if RemoveSettings then
        DelTree(AppDataPath, True, True, True);
    end;
  end;
end;
