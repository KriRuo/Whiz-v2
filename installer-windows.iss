; installer-windows.iss
; Inno Setup script for Windows installer
; Creates a professional Windows installer for Whiz

[Setup]
; Basic Information
AppName=Whiz Voice-to-Text
AppVersion=1.0.0
AppPublisher=Whiz Development Team
AppPublisherURL=https://github.com/KriRuo/Whiz
AppSupportURL=https://github.com/KriRuo/Whiz/issues
AppUpdatesURL=https://github.com/KriRuo/Whiz/releases
AppCopyright=Copyright (C) 2025 Whiz Development Team

; Installation Directory
DefaultDirName={autopf}\Whiz
DefaultGroupName=Whiz
AllowNoIcons=yes

; Output
OutputDir=installers
OutputBaseFilename=Whiz-Setup-Windows
SetupIconFile=app_icon_transparent.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

; Prerequisites
PrivilegesRequired=lowest
MinVersion=10.0.17763

; Appearance
WizardImageFile=app_icon_transparent.bmp
WizardSmallImageFile=app_icon_transparent.bmp

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
; Main executable
Source: "dist\Whiz.exe"; DestDir: "{app}"; Flags: ignoreversion

; Assets folder
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

; Icons
Source: "app_icon_transparent.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "speech_to_text_icon_transparent_middle_white.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "Icon_Listening.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "Icon_Transcribing.png"; DestDir: "{app}"; Flags: ignoreversion

; Documentation
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "QUICK_START.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu
Name: "{group}\Whiz Voice-to-Text"; Filename: "{app}\Whiz.exe"; IconFilename: "{app}\app_icon_transparent.ico"
Name: "{group}\{cm:UninstallProgram,Whiz Voice-to-Text}"; Filename: "{uninstallexe}"

; Desktop (optional)
Name: "{autodesktop}\Whiz Voice-to-Text"; Filename: "{app}\Whiz.exe"; IconFilename: "{app}\app_icon_transparent.ico"; Tasks: desktopicon

; Quick Launch (optional)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Whiz Voice-to-Text"; Filename: "{app}\Whiz.exe"; IconFilename: "{app}\app_icon_transparent.ico"; Tasks: quicklaunchicon

[Run]
; Launch after installation
Filename: "{app}\Whiz.exe"; Description: "{cm:LaunchProgram,Whiz Voice-to-Text}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up user data
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\temp"

[Code]
// Custom code for installer behavior
function InitializeSetup(): Boolean;
begin
  Result := True;
  
  // Check if Whiz is already running
  if CheckForMutexes('WhizMutex') then
  begin
    if MsgBox('Whiz is currently running. Please close it before continuing.', mbError, MB_OKCANCEL) = IDCANCEL then
      Result := False;
  end;
end;

function InitializeUninstall(): Boolean;
begin
  Result := True;
  
  // Check if Whiz is running during uninstall
  if CheckForMutexes('WhizMutex') then
  begin
    if MsgBox('Whiz is currently running. Please close it before uninstalling.', mbError, MB_OKCANCEL) = IDCANCEL then
      Result := False;
  end;
end;
