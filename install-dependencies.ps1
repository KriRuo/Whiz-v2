# PowerShell script to install all required dependencies
# Usage: .\install-dependencies.ps1

Write-Host "Installing Speech-to-Text Tool dependencies..." -ForegroundColor Green

# Upgrade pip first
Write-Host "Upgrading pip..." -ForegroundColor Yellow
pip install --upgrade pip

# Install all dependencies from requirements.txt
Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Yellow
pip install -r requirements.txt

# Test PyQt5 installation
Write-Host "Testing PyQt5 installation..." -ForegroundColor Yellow
try {
    python -c "import PyQt5; print('PyQt5 imported successfully')"
    Write-Host "PyQt5 installation successful!" -ForegroundColor Green
} catch {
    Write-Host "PyQt5 installation failed. Trying alternative installation..." -ForegroundColor Red
    pip install PyQt5==5.15.9 --force-reinstall
}

# Test all imports
Write-Host "Testing all imports..." -ForegroundColor Yellow
try {
    python -c "import main; print('All imports successful!')"
    Write-Host "All dependencies installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Some dependencies may need manual installation." -ForegroundColor Red
    Write-Host "Please check the error messages above." -ForegroundColor Red
}

Write-Host "Installation completed!" -ForegroundColor Green
