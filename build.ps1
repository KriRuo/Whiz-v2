# build.ps1 — Build Whiz as a standalone Windows application
#
# Usage:
#   .\build.ps1
#
# Output:
#   dist\Whiz\Whiz.exe   — standalone app folder (no Python required)
#
# After this succeeds, run Inno Setup to produce the installer:
#   iscc installer-windows.iss

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Locate .venv — check current dir first, then walk up (handles git worktrees)
$VenvPath = $null
$SearchDir = $PSScriptRoot
for ($i = 0; $i -lt 5; $i++) {
    $candidate = Join-Path $SearchDir ".venv\Scripts\Activate.ps1"
    if (Test-Path $candidate) { $VenvPath = $candidate; break }
    $SearchDir = Split-Path $SearchDir -Parent
}

if ($VenvPath) {
    Write-Host "Activating virtual environment: $VenvPath" -ForegroundColor Cyan
    & $VenvPath
} else {
    Write-Warning "No .venv found — using system Python (run: python -m venv .venv first)"
}

# Install dependencies (torch is not in requirements.txt)
Write-Host "Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

# Install PyInstaller if not already present
if (-not (pip show pyinstaller 2>$null)) {
    Write-Host "Installing PyInstaller..." -ForegroundColor Cyan
    pip install pyinstaller
}

# Clean previous build artifacts
if (Test-Path "dist\Whiz") {
    Write-Host "Removing previous dist\Whiz..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "dist\Whiz"
}
if (Test-Path "build\Whiz") {
    Remove-Item -Recurse -Force "build\Whiz"
}

# Run PyInstaller
Write-Host "Running PyInstaller..." -ForegroundColor Cyan
pyinstaller whiz.spec --clean --noconfirm

if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Build complete: dist\Whiz\Whiz.exe" -ForegroundColor Green
Write-Host "To build the installer, run:" -ForegroundColor Green
Write-Host "  iscc installer-windows.iss" -ForegroundColor White
