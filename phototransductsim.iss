[Setup]
AppName=PhototransductSim
AppVersion=0.1.0
DefaultDirName={pf}\PhototransductSim
DefaultGroupName=PhototransductSim
OutputDir=dist
OutputBaseFilename=PhototransductSimInstaller
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
