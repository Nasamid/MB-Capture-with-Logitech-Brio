# MB-Capture — Logitech Brio Capture Controller 📸

A lightweight desktop app for controlling Logitech Brio (and compatible) webcams with digital zoom, pan, manual focus, and reliable image capture workflows.

---

## Key Features ✅
- Modern UI built with CustomTkinter
- Real-time camera preview (4K capable)
- Digital zoom (1.0x–5.0x) with pan controls
- Manual focus (0–255)
- Serial Number (SN) tracking with SN history
- Orientation toggle: **TOP** / **BOTTOM** appended to filenames
- Per-SN capture folders (each contains at most one TOP and one BOTTOM image)

---

## Quick Start ⚙️
1. Create and activate a virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the app:

```powershell
python app.py
```

---

## Usage Overview 🖥️🎥
1. Launch the app. Camera detection runs automatically.
2. Select your camera from the dropdown.
3. Enter a Serial Number (SN) in the SN field and press Enter to save to history.
4. Choose orientation using the **TOP** / **BOTTOM** toggle next to the SN input (default: TOP).
5. Adjust zoom, pan, and focus as needed.
6. Capture an image with the Spacebar or the "📷 Capture" button.

---

## Capture & Storage Details 🔧
- Capture directory: `C:/brio_captures/captures` (created automatically)
- Per-SN subfolders: `C:/brio_captures/captures/<SN>/` (created automatically on first capture)
- File format: `SN_ORIENTATION_YYYYMMDD_HHMMSS.png` (spaces in SN replaced with `_`)
  - Example: `SN12345_TOP_20251216_143022.png`
- Each SN folder will contain at most two images — one TOP and one BOTTOM. If an image already exists for the chosen orientation, the app will prompt to overwrite.

---

## Troubleshooting & Notes ⚠️
- If the camera is not detected: check USB connection and close other apps using the camera. Try a different USB port (USB 3.0 recommended for 4K).
- If captures are not saved: ensure the app has write permissions and there's enough disk space.
- PowerShell activation blocked? Use Command Prompt activation (`.venv\Scripts\activate.bat`) or adjust execution policy if appropriate.

---

## Development & Contribution 🛠️
- Python 3.8+ recommended
- Dependencies are listed in `requirements.txt`
- Feel free to open issues or PRs for new features (hardware zoom, burst capture, etc.)

---

## Rebuilding the .exe (Windows) 🔁

Two helper scripts are included to rebuild a single-file, no-console executable using PyInstaller:

- `build_exe.ps1` — PowerShell script (recommended). Run from project root:
  - `.uild_exe.ps1`
- `build_exe.bat` — Batch file for Command Prompt (double-click or run `build_exe.bat`).

What the scripts do:
- Activate the local `.venv` if it exists (PowerShell script attempts activation).
- Ensure `pyinstaller` is installed.
- Clean previous `build/`, `dist/`, and the spec file.
- Run:
  - `python -m PyInstaller --onefile --noconsole --name BrioCapture app.py`
- Output exe location: `dist\BrioCapture.exe`.

Notes:
- The exe is built with `--noconsole` (GUI). Remove `--noconsole` in the script if you need a console for debugging.
- If the build fails due to missing hidden imports or data files, re-run PyInstaller with `--hidden-import` options or modify the `.spec` file — I can help automate that if needed.

---

## Building the Windows Installer (Inno Setup) 🛠️

I added an Inno Setup script and a PowerShell helper to build an installer:

Files:
- `installer/BrioCaptureInstaller.iss` — The Inno Setup script that packages the single-file exe and the README into Program Files, creates Start Menu and Desktop shortcuts, and offers a post-install launch.
- `build_installer.ps1` — PowerShell script that looks for the Inno Setup Compiler (`ISCC.exe`) in typical locations or uses the `INNO_ISCC` env var, then compiles the .iss and places the output in `dist\installer`.

How to build:
1. Install Inno Setup (https://jrsoftware.org) if you don't have it.
2. Ensure `dist\BrioCapture.exe` exists (build it with `.uild_exe.ps1`).
3. Run:
   - `.uild_installer.ps1`
   - Or pass a custom ISCC path: `.uild_installer.ps1 -ISCCPath "C:\Path\To\ISCC.exe"`

Notes:
- The script assumes the Inno Setup Compiler version 6 (typical install path: `C:\Program Files (x86)\Inno Setup 6\ISCC.exe`).
- A default icon generator is provided in `tools/generate_icon.py` and the build scripts will generate `installer/brio_icon.ico` automatically when needed.
- The Inno Setup script uses `installer\brio_icon.ico` for the installer icon and also installs the icon into the app folder.
- I can add code signing (signtool) in a follow-up if you have a signing certificate.

---

If you'd like, I can add a short changelog entry or a GitHub-friendly badge/metadata — tell me which you'd prefer next. ✨
