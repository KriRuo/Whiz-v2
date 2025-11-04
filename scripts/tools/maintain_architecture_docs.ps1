# Architecture Diagram Maintenance Script
# This script helps keep architecture diagrams up-to-date

Write-Host "Whiz Architecture Diagram Maintenance" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "
Checklist for updating ARCHITECTURE.md:" -ForegroundColor Yellow
Write-Host "1. Architecture changes (new components, major refactoring)" -ForegroundColor Green
Write-Host "2. UI modifications (new tabs, significant layout changes)" -ForegroundColor Green
Write-Host "3. Settings system changes (new categories, validation rules)" -ForegroundColor Green
Write-Host "4. Audio pipeline changes (recording, processing logic)" -ForegroundColor Green
Write-Host "5. Threading model changes (new processes, signal patterns)" -ForegroundColor Green

Write-Host "
Tools for diagram maintenance:" -ForegroundColor Yellow
Write-Host "â€¢ Mermaid Live Editor: https://mermaid.live/" -ForegroundColor Blue
Write-Host "â€¢ VS Code Mermaid Extension: 'Mermaid Preview'" -ForegroundColor Blue
Write-Host "â€¢ GitHub: Automatic rendering in markdown files" -ForegroundColor Blue

Write-Host "
How to update diagrams:" -ForegroundColor Yellow
Write-Host "1. Edit ARCHITECTURE.md with your changes" -ForegroundColor White
Write-Host "2. Test diagrams at https://mermaid.live/" -ForegroundColor White
Write-Host "3. Commit with message: 'docs: update architecture diagrams'" -ForegroundColor White

Write-Host "
Current architecture file status:" -ForegroundColor Yellow
if (Test-Path "ARCHITECTURE.md") {
    $fileInfo = Get-Item "ARCHITECTURE.md"
    Write-Host "ARCHITECTURE.md exists" -ForegroundColor Green
    Write-Host "Last modified: $($fileInfo.LastWriteTime)" -ForegroundColor Cyan
    Write-Host "File size: $([math]::Round($fileInfo.Length / 1KB, 2)) KB" -ForegroundColor Cyan
} else {
    Write-Host "ARCHITECTURE.md not found" -ForegroundColor Red
}

Write-Host "
Ready to maintain your architecture documentation!" -ForegroundColor Green
