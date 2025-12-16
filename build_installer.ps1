# build_installer.ps1
# Build the Inno Setup installer for BrioCapture

Set-StrictMode -Version Latest

# Allow override via env var INNO_ISCC or CLI param
param(
    [string]$ISCCPath = $env:INNO_ISCC
)

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location $scriptRoot

# Default Inno Setup Compiler path(s) to check
$defaultPaths = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe"
)

if (-not $ISCCPath) {
    foreach ($p in $defaultPaths) {
        if (Test-Path $p) { $ISCCPath = $p; break }
    }
}

if (-not $ISCCPath -or -not (Test-Path $ISCCPath)) {
    Write-Error "Inno Setup Compiler not found. Install Inno Setup (https://jrsoftware.org/) or set INNO_ISCC to its path."
    Pop-Location
    exit 1
}

$issFile = Join-Path $scriptRoot "installer\BrioCaptureInstaller.iss"
if (-not (Test-Path $issFile)) {
    Write-Error "Installer script not found: $issFile"
    Pop-Location
    exit 1
}

# Ensure icon exists (generate if necessary)
$iconPath = Join-Path $scriptRoot "installer\brio_icon.ico"
$iconGenerator = Join-Path $scriptRoot "tools\generate_icon.py"
if (-not (Test-Path $iconPath)) {
    if (Test-Path $iconGenerator) {
        Write-Output "Generating icon for installer..."
        python "$iconGenerator"
    } else {
        Write-Warning "Icon not found and no generator available. The installer will be built without a custom icon."
    }
}

# Ensure output dir exists
$outDir = Join-Path $scriptRoot "dist\installer"
New-Item -ItemType "directory" -Force -Path $outDir | Out-Null

Write-Output "Compiling installer with ISCC: $ISCCPath"
# /O sets output directory; pass arguments as separate entries to avoid quoting issues
$argList = @("/O$outDir", "$issFile")
$psi = Start-Process -FilePath $ISCCPath -ArgumentList $argList -NoNewWindow -PassThru -Wait
if ($psi -eq $null) {
    Write-Error "Failed to start ISCC."
    Pop-Location
    exit 1
}
if ($psi.ExitCode -ne 0) {
    Write-Error "ISCC exited with code $($psi.ExitCode). Check the output for details."
    Pop-Location
    exit $psi.ExitCode
}

Write-Output "Installer built and placed in: $outDir"
Pop-Location
