# Install FFmpeg for Windows
# This script downloads and installs ffmpeg to a local directory and adds it to PATH

param(
    [string]$InstallDir = "$PSScriptRoot\..\..\ffmpeg"
)

Write-Host "=== FFmpeg Installer for Whiz ===" -ForegroundColor Cyan
Write-Host ""

# Create installation directory
$InstallDir = [System.IO.Path]::GetFullPath($InstallDir)
Write-Host "Installation directory: $InstallDir" -ForegroundColor Yellow

if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    Write-Host "Created installation directory" -ForegroundColor Green
}

# Check if ffmpeg already exists
$ffmpegExe = Join-Path $InstallDir "bin\ffmpeg.exe"
if (Test-Path $ffmpegExe) {
    Write-Host "FFmpeg is already installed at: $ffmpegExe" -ForegroundColor Green
    
    # Test if it works
    try {
        $version = & $ffmpegExe -version 2>&1 | Select-Object -First 1
        Write-Host "Version: $version" -ForegroundColor Green
        Write-Host ""
        Write-Host "FFmpeg is ready to use!" -ForegroundColor Green
        exit 0
    }
    catch {
        Write-Host "Existing installation appears corrupted. Reinstalling..." -ForegroundColor Yellow
        Remove-Item -Path $InstallDir -Recurse -Force
        New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    }
}

# Download ffmpeg
Write-Host ""
Write-Host "Downloading FFmpeg..." -ForegroundColor Yellow

$ffmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
$downloadPath = Join-Path $env:TEMP "ffmpeg.zip"

try {
    # Use Invoke-WebRequest with TLS 1.2 support
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $ProgressPreference = 'SilentlyContinue'  # Faster downloads
    Invoke-WebRequest -Uri $ffmpegUrl -OutFile $downloadPath -UseBasicParsing
    $ProgressPreference = 'Continue'
    Write-Host "Download complete!" -ForegroundColor Green
}
catch {
    Write-Host "Error downloading FFmpeg: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please download FFmpeg manually from:" -ForegroundColor Yellow
    Write-Host "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip" -ForegroundColor Cyan
    exit 1
}

# Extract ffmpeg
Write-Host ""
Write-Host "Extracting FFmpeg..." -ForegroundColor Yellow

try {
    # Extract to temp location
    $extractPath = Join-Path $env:TEMP "ffmpeg_extract"
    if (Test-Path $extractPath) {
        Remove-Item -Path $extractPath -Recurse -Force
    }
    
    Expand-Archive -Path $downloadPath -DestinationPath $extractPath -Force
    
    # Find the ffmpeg folder (it's nested in the archive)
    $ffmpegFolder = Get-ChildItem -Path $extractPath -Directory | Select-Object -First 1
    
    # Copy to installation directory
    Copy-Item -Path "$($ffmpegFolder.FullName)\*" -Destination $InstallDir -Recurse -Force
    
    Write-Host "Extraction complete!" -ForegroundColor Green
    
    # Cleanup
    Remove-Item -Path $downloadPath -Force
    Remove-Item -Path $extractPath -Recurse -Force
}
catch {
    Write-Host "Error extracting FFmpeg: $_" -ForegroundColor Red
    exit 1
}

# Verify installation
Write-Host ""
Write-Host "Verifying installation..." -ForegroundColor Yellow

if (Test-Path $ffmpegExe) {
    try {
        $version = & $ffmpegExe -version 2>&1 | Select-Object -First 1
        Write-Host "FFmpeg installed successfully!" -ForegroundColor Green
        Write-Host "Version: $version" -ForegroundColor Cyan
        Write-Host "Location: $ffmpegExe" -ForegroundColor Cyan
    }
    catch {
        Write-Host "Installation verification failed: $_" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "Installation failed: ffmpeg.exe not found" -ForegroundColor Red
    exit 1
}

# Add to PATH for current session
$binPath = Join-Path $InstallDir "bin"
$env:PATH = "$binPath;$env:PATH"
Write-Host ""
Write-Host "FFmpeg added to PATH for current session" -ForegroundColor Green

# Create a batch file to add ffmpeg to PATH
$batchFile = Join-Path $PSScriptRoot "set_ffmpeg_path.bat"
@"
@echo off
REM Add FFmpeg to PATH
set "PATH=$binPath;%PATH%"
"@ | Out-File -FilePath $batchFile -Encoding ASCII -Force

Write-Host ""
Write-Host "=== Installation Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: To use FFmpeg with Whiz, you have two options:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Option 1 (Recommended): Update launch script" -ForegroundColor Cyan
Write-Host "  - The launch scripts will be updated to include FFmpeg in PATH automatically" -ForegroundColor White
Write-Host ""
Write-Host "Option 2: Manual PATH update" -ForegroundColor Cyan
Write-Host "  - Add to User PATH: $binPath" -ForegroundColor White
Write-Host "  - Then restart your terminal/application" -ForegroundColor White
Write-Host ""
Write-Host "For this session, FFmpeg is already available!" -ForegroundColor Green

