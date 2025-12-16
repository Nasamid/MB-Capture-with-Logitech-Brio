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

If you'd like, I can add a short changelog entry or a GitHub-friendly badge/metadata — tell me which you'd prefer next. ✨
