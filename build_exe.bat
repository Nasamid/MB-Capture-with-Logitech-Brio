@echo off
REM Quick rebuild script for Windows (uses .venv if available)
SETLOCAL
IF EXIST ".venv\Scripts\python.exe" (
  SET "PYTHON=.venv\Scripts\python.exe"
  echo Using venv python: %PYTHON%
) ELSE (
  SET "PYTHON=python"
  echo No venv python found, falling back to system python: %PYTHON%
)

echo Ensuring PyInstaller in selected Python...
%PYTHON% -m pip install --upgrade pip
%PYTHON% -m pip install pyinstaller

echo Cleaning previous artifacts...
rd /s /q build 2>nul
rd /s /q dist 2>nul
del /q BrioCapture.spec 2>nul

REM Generate icon if not present
if not exist "installer\brio_icon.ico" (
  if exist "tools\generate_icon.py" (
    echo Generating icon...
    python tools\generate_icon.py
  ) else (
    echo Icon generator not found at tools\generate_icon.py
  )
)

echo Building BrioCapture.exe (onefile, no-console) with icon...
%PYTHON% -m PyInstaller --onefile --noconsole --icon installer\brio_icon.ico --hidden-import customtkinter --collect-all customtkinter --name BrioCapture app.py
echo Build finished. See dist\BrioCapture.exe if successful.
pause
ENDLOCAL
