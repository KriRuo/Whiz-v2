# generate-checksums.ps1
# Generate SHA256 checksums for distribution files

Write-Host "Generating SHA256 checksums for Whiz distribution files..." -ForegroundColor Green

$files = @(
    "dist\Whiz.exe",
    "installers\Whiz.exe"
)

$checksums = @()

foreach ($file in $files) {
    if (Test-Path $file) {
        $hash = Get-FileHash -Path $file -Algorithm SHA256
        $size = (Get-Item $file).Length
        $sizeMB = [math]::Round($size / 1MB, 2)
        
        $checksums += [PSCustomObject]@{
            File = $file
            SHA256 = $hash.Hash
            Size = $sizeMB
        }
        Write-Host "✓ $($file): $($hash.Hash)" -ForegroundColor Yellow
    } else {
        Write-Host "✗ $($file): File not found" -ForegroundColor Red
    }
}

# Save checksums to file
$checksums | Format-Table -AutoSize | Out-File -FilePath "checksums.txt" -Encoding UTF8

Write-Host "`nChecksums saved to checksums.txt" -ForegroundColor Green
Write-Host "Files processed: $($checksums.Count)" -ForegroundColor Cyan

# Display summary
Write-Host "`n=== DISTRIBUTION SUMMARY ===" -ForegroundColor Magenta
Write-Host "Windows Executable: dist\Whiz.exe ($([math]::Round((Get-Item 'dist\Whiz.exe').Length / 1MB, 2)) MB)" -ForegroundColor White
Write-Host "Installer Package: installers\ directory" -ForegroundColor White
Write-Host "Checksums: checksums.txt" -ForegroundColor White
Write-Host "`nReady for distribution!" -ForegroundColor Green