# Rebuild BrioCapture.exe using PyInstaller
# Usage: Run this from the project root in PowerShell.
# It will try to activate the local .venv if present, ensure PyInstaller is installed,
# clean prior artifacts, and build a single-file, no-console exe.

Set-StrictMode -Version Latest

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location $scriptRoot

# Prefer using the project's virtualenv python if present (avoid relying on activation)
$venvPython = Join-Path $scriptRoot ".venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    $pythonCmd = $venvPython
    Write-Output "Using venv python: $pythonCmd"
} else {
    $pythonCmd = "python"
    Write-Output "No venv python found; falling back to system 'python' ($pythonCmd)"
}

Write-Output "Ensuring PyInstaller is installed in the selected Python environment..."
& $pythonCmd -m pip install --upgrade pip
& $pythonCmd -m pip install pyinstaller

Write-Output "Cleaning previous build artifacts..."
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue "./build", "./dist"
Remove-Item -Force -ErrorAction SilentlyContinue "./BrioCapture.spec"

# Ensure icon exists (generate if necessary)
$iconScript = Join-Path $scriptRoot "tools\generate_icon.py"
$iconFile = Join-Path $scriptRoot "installer\brio_icon.ico"
if (-not (Test-Path $iconFile)) {
    if (Test-Path $iconScript) {
        Write-Output "Generating icon at $iconFile"
        python "$iconScript"
    } else {
        Write-Output "Icon generator script not found: $iconScript"
    }
}

Write-Output "Building BrioCapture.exe (onefile, no-console) with icon; including CustomTkinter..."
# Explicitly ask PyInstaller to include customtkinter and collect package data to avoid missing-module issues
& $pythonCmd -m PyInstaller --onefile --noconsole --name BrioCapture --icon "installer\brio_icon.ico" --hidden-import customtkinter --collect-all customtkinter app.py

if (Test-Path "./dist/BrioCapture.exe") {
    Write-Output "Build complete: ./dist/BrioCapture.exe"
} else {
    Write-Error "Build finished but executable not found. Check PyInstaller output for errors."
    exit 1
}

Pop-Location
