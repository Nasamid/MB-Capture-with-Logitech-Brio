# Oba_capture — User Operating Procedure (SOP) ✅

## Purpose
This SOP explains how to set up, run, and use the Oba_capture application (Logitech Brio Camera Controller). It also covers troubleshooting, common issues, and recommended best practices.

---

## Pre‑requisites ✅
- Windows 10/11 (recommended) or another OS with Python support
- Python 3.8+ installed and available on PATH
- USB camera compatible with OpenCV (Logitech Brio recommended)
- Sufficient disk space for image captures (PNG files)

---

## Quick Setup (Windows) ⚙️
1. Open PowerShell or Command Prompt in the project folder (e.g., `C:\Users\p\Downloads\Oba_capture`).

2. Create a virtual environment (only if not already created):

   ```powershell
   python -m venv .venv
   ```

3. Activate the virtual environment:

   - PowerShell (recommended):
     - If activation is blocked, see "PowerShell activation blocked" in Troubleshooting.
     ```powershell
     & C:\Users\p\Downloads\Oba_capture\.venv\Scripts\python.exe .venv\Scripts\Activate.ps1
     ```

   - Command Prompt (works without changing execution policy):
     ```cmd
     & C:\Users\p\Downloads\Oba_capture\.venv\Scripts\python.exe .venv\Scripts\activate.bat
     ```

4. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

5. Run the application:

   ```powershell
    & C:\Users\p\Downloads\Oba_capture\.venv\Scripts\python.exe c:/Users/p/Downloads/Oba_capture/app.py
   ```

   Or run with the venv Python explicitly:

   ```powershell
   & C:\Users\p\Downloads\Oba_capture\.venv\Scripts\python.exe .venv\Scripts\python.exe app.py
   ```

---

## Using the Application — User Workflow 🖥️🎥
1. Launch app. Camera detection runs automatically; wait a few seconds for the camera list to populate.
2. Select your camera from the "Select Camera" dropdown.
3. Enter a Serial Number (SN) in the SN field for the session.
   - Press Enter to save SN to history.
   - Use the Up/Down arrows (inside the SN field) to browse previous SNs.
4. Select orientation: Click **TOP** or **BOTTOM** next to the SN field to choose which orientation will be appended to captured filenames (default: TOP).
5. Adjust digital zoom (1.0x–5.0x) using the slider.
5. Adjust focus with the focus slider (0–255) if required.
6. Pan the viewport with arrow buttons or keyboard arrows.
7. To capture an image:
   - Click the "📷 Capture" button or press Spacebar.
   - Captures are saved under `C:/brio_captures/captures/<SN>/`. Each SN folder contains at most two images — one `*_TOP_*.png` and one `*_BOTTOM_*.png`.
   - If an image already exists for the selected orientation, you will be prompted to overwrite (Yes to replace, No to cancel).
   - Filenames follow: `SN_ORIENTATION_YYYYMMDD_HHMMSS.png` (e.g., `SN12345_TOP_20251216_143022.png`).
8. To open saved images, click "📁 Open Captures".

---

## Keyboard Shortcuts ⌨️
- Arrow keys: Pan viewport (Up/Down/Left/Right)
- Spacebar: Capture image
- Enter (in SN field): Save SN to history
- Up/Down (in SN field): Browse SN history

---

## Troubleshooting & Common Issues ⚠️

### PowerShell activation blocked
- Symptom: `Activate.ps1` cannot run due to execution policy.
- Quick fixes:
  - Use Command Prompt with `activate.bat`:
    ```cmd
    .venv\Scripts\activate.bat
    ```
  - Or set a less restrictive policy (requires admin and security awareness):
    ```powershell
    Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
    ```
  - If you change policy, consider resetting it later.

### Camera not detected
- Check USB connection and try a different USB port (prefer USB 3.0 for 4K cameras).
- Close other apps that may be using the camera.
- Click "Refresh" in the app to re-scan.
- Reboot the PC if required.

### No preview or preview lag
- Ensure camera isn't used by another app.
- Reduce zoom or close other heavy apps.
- Ensure your system meets CPU/memory requirements for 4K preview.

### Captures not saved or folder not found
- Ensure `captures/` folder exists and app has write permissions.
- Check disk space and file permissions for the user running the app.

### App fails to start / dependency errors
- Confirm you activated the venv and ran `pip install -r requirements.txt`.
- If a specific module error appears, install it manually: `pip install <package>`.

---

## Recommended Best Practices ✅
- Use a USB 3.0 port for 4K cameras to reduce bandwidth issues.
- Run the app from a dedicated virtual environment to avoid dependency conflicts.
- Keep `requirements.txt` up to date and recreate the venv when major changes are made.
- Use a stable SN format (alphanumeric) for consistent filenames.

---

## File Naming & Storage Policy
- Files are named: `SN_ORIENTATION_YYYYMMDD_HHMMSS.png` (e.g., `SN12345_TOP_20251216_143022.png`).
- Storage: Files are stored in `C:/brio_captures/captures/<SN>/`. Each SN folder is limited to at most one TOP and one BOTTOM image; older duplicates are removed when a new image is saved.
- Default orientation: **TOP** unless changed via the toggle next to the SN field.
- Keep captures organized by session or date. Consider offloading older captures to cloud or archival storage.

---

## Support & Feedback
- For bugs or feature requests, open an issue in the repository or contact the project owner.
- When reporting issues, include: OS, Python version, app logs (if available), camera model, steps to reproduce.

---

## Versioning & Change Log
- Update this SOP when the app introduces breaking changes to setup, dependencies, or features.

---

If you'd like, I can (choose one):
- Add this SOP to `README.md` or link it from `CLAUDE.md`,
- Create a short Quick Start one‑pager, or
- Add troubleshooting scripts for the common problems above.

