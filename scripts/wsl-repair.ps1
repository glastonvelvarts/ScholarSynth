# Run in PowerShell AS ADMINISTRATOR:
#   Set-ExecutionPolicy -Scope Process Bypass -Force
#   & "C:\Users\glast\OneDrive\Desktop\PaperContext\scripts\wsl-repair.ps1"
#
# Then reboot, install WSL MSI (see script output), reboot again.

$ErrorActionPreference = "Stop"

Write-Host "==> Enabling Windows features for WSL2..." -ForegroundColor Cyan
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
dism.exe /online /enable-feature /featurename:HypervisorPlatform /all /norestart

Write-Host ""
Write-Host "==> Removing broken WSL app package (if present)..." -ForegroundColor Cyan
$wslPackages = Get-AppxPackage -Name "*WindowsSubsystemForLinux*" -ErrorAction SilentlyContinue
foreach ($pkg in $wslPackages) {
    Write-Host "    Removing $($pkg.Name) $($pkg.Version)"
    Remove-AppxPackage -Package $pkg.PackageFullName -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "==> Optional: winget uninstall (may fail if not installed via winget)" -ForegroundColor Cyan
winget uninstall --id Microsoft.WSL -e --accept-source-agreements 2>$null

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "NEXT STEPS (manual):" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "1. REBOOT Windows now."
Write-Host ""
Write-Host "2. Temporarily disable third-party antivirus (Kaspersky, etc.)."
Write-Host ""
Write-Host "3. Download and run AS ADMIN the latest x64 MSI:"
Write-Host "   https://github.com/microsoft/WSL/releases/latest"
Write-Host "   (file: wsl-*-x64.msi)"
Write-Host ""
Write-Host "4. If MSI warns about registry keys, click through or fix permissions"
Write-Host "   on HKLM\SOFTWARE\Classes\Directory\Background\shell\WSL (SYSTEM = Full)."
Write-Host ""
Write-Host "5. REBOOT again, then test:"
Write-Host "   wsl --version"
Write-Host "   wsl --install -d Ubuntu"
Write-Host ""
Write-Host "6. In Ubuntu: nvidia-smi && bash scripts/wsl-setup.sh"
