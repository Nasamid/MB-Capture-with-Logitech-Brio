# Oba_capture - Logitech Brio Camera Capture Controller

## Project Overview
This is a desktop application for controlling Logitech Brio webcams with advanced digital zoom, pan, and capture capabilities. Built with Python, it provides a modern dark-themed UI for professional camera control and image capture.

## Purpose
- Control Logitech Brio cameras (4K support)
- Digital zoom (1x - 5x) with smooth controls
- Manual focus adjustment (0-255)
- Pan controls (Up/Down/Left/Right) with keyboard shortcuts
- Image capture with serial number tracking
- Multi-camera support with automatic detection
- Real-time camera preview

## Tech Stack
- **Python 3.x**
- **CustomTkinter** (5.2.2) - Modern UI framework
- **OpenCV** (4.10.0.84) - Camera capture and image processing
- **Pillow** (11.0.0) - Image handling

## Project Structure
```
Oba_capture/
├── app.py              # Main application code
├── requirements.txt    # Python dependencies
├── captures/           # Directory for captured images
└── .venv/             # Virtual environment (not in repo)
```

## Key Features

### Camera Control
- **Multi-camera support**: Automatically detects available cameras
- **4K resolution**: Requests 3840x2160 from Brio cameras
- **Digital zoom**: 1.0x to 5.0x with 40-step slider
- **Manual focus**: 0-255 range control
- **Pan controls**: Navigate the zoomed image (keyboard arrows or buttons)

### User Interface
- Dark theme with blue accents
- Real-time camera preview
- Loading overlay during initialization
- Status indicators for camera state
- Resolution display

### Image Capture
- **Serial Number (SN) tracking**: Enter SN for each capture session
- **SN history**: Navigate previous SNs with Up/Down arrows
- **Orientation toggle**: Choose **TOP** or **BOTTOM**; the selected orientation is appended to capture filenames (default: TOP).
- **Per-SN folder**: Captures are stored in a subdirectory named after the SN inside the main captures folder (`C:/brio_captures/captures/<SN>/`). Each SN folder will contain strictly two images at most — one TOP and one BOTTOM.
- **Overwrite behavior**: If an image for the selected orientation already exists in the SN folder, the app will prompt to overwrite; if you decline, the capture is canceled. If the SN folder does not exist, it will be created automatically on first capture.
- **Filename format**: `SN_ORIENTATION_YYYYMMDD_HHMMSS.png` (spaces in SN are replaced with `_`)
- **Visual feedback**: White flicker on capture
- **Keyboard shortcut**: Spacebar to capture

### Pan Feature
- Move the viewport within zoomed images
- Keyboard arrows for fine control
- Reset button to center view
- Works in conjunction with digital zoom

## Code Architecture

### Main Class: `CameraZoomController`
```python
class CameraZoomController:
    - __init__: Initialize UI and camera variables
    - create_ui: Build CustomTkinter interface
    - detect_cameras: Scan for available cameras
    - initialize_camera: Setup selected camera
    - update_preview: Real-time camera feed with zoom/pan
    - capture_image: Save current frame to disk
    - update_digital_zoom: Handle zoom slider changes
    - update_focus: Adjust camera focus
    - pan_up/down/left/right: Navigate viewport
```

### Threading Model
- **Camera detection**: Background thread to avoid UI blocking
- **Camera initialization**: Separate thread with loading overlay
- **Preview update**: Continuous background thread for live feed
- **Frame skipping**: Every 2nd frame for better performance

### Image Processing Pipeline
1. Capture frame from OpenCV
2. Apply digital zoom (crop center)
3. Apply pan offset (shift viewport)
4. Resize to display resolution (960x540)
5. Convert BGR to RGB
6. Display in UI via PIL/ImageTk

## Configuration

### Camera Settings
- Default resolution request: 3840x2160 (4K)
- Buffer size: 1 (latest frame only)
- Warm-up frames: 5 (fast startup)

### UI Settings
- Window size: Half screen width × (screen height - 50)
- Position: Top-left corner (0, 0)
- Non-resizable window

### Capture Settings
- Format: PNG
- Filename: Includes date, time, serial number and orientation
- Location: `C:/brio_captures/captures` (per‑SN subfolders created automatically)
- White flicker duration: 3 frames

## Dependencies

### Core Libraries
```
customtkinter==5.2.2    # Modern Tkinter replacement
opencv-python==4.10.0.84  # Camera access and CV
Pillow==11.0.0          # Image handling
```

### System Requirements
- Windows (PowerShell support)
- Logitech Brio camera (or compatible USB camera)
- Python 3.7+

## Setup Instructions

1. **Create virtual environment**:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

2. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Run application**:
   ```powershell
   python app.py
   ```

## Usage Workflow

1. **Launch app** - Camera detection runs automatically
2. **Select camera** - Choose from dropdown (if multiple cameras)
3. **Enter SN** - Type serial number for the capture session
4. **Adjust view**:
   - Drag zoom slider for magnification
   - Use arrow keys or buttons to pan
   - Adjust focus slider if needed
5. **Capture** - Press Spacebar or click "📷 Capture" button
6. **Open folder** - Click "📁 Open Captures" to view saved images

## Keyboard Shortcuts
- **Arrow Keys**: Pan the viewport (Up/Down/Left/Right)
- **Spacebar**: Capture image
- **Up/Down** (in SN field): Browse SN history
- **Enter** (in SN field): Save SN to history

## Key Variables

### Camera State
- `self.cap`: OpenCV VideoCapture object
- `self.camera_width/height`: Actual camera resolution
- `self.selected_camera_index`: Currently selected camera
- `self.available_cameras`: Dict of detected cameras

### UI State
- `self.digital_zoom_level`: Current zoom (1.0 - 5.0)
- `self.focus_level`: Manual focus value (0-255)
- `self.pan_x/pan_y`: Pan offset from center
- `self.is_running`: Camera thread active flag

### Capture State
- `self.sn_entry`: Serial number input widget
- `self.sn_history`: List of previous SNs
- `self.show_white_flicker`: Capture feedback flag

## Error Handling
- Camera detection failures: Show empty list, allow refresh
- Camera initialization timeout: 1 second with loading overlay
- Frame read failures: Retry up to 10 times before error
- Invalid camera index: Graceful error message

## Performance Optimizations
- Frame skipping: Update UI every 2nd frame
- Buffer size: 1 (latest frame only, no lag)
- Fast warm-up: Only 5 frames
- Background threads: Non-blocking UI

## Platform Support
- **Windows**: Full support with PowerShell
- **macOS/Linux**: Should work with path adjustments (not tested)

## Future Enhancement Ideas
- Hardware zoom control (if supported by camera)
- Video recording capability
- Multi-shot burst mode
- Export settings profile
- Camera settings persistence
- Auto-focus toggle

## Troubleshooting

### Camera not detected
- Check USB connection
- Try different USB port
- Refresh camera list
- Restart application

### Preview lag
- Reduce zoom level
- Close other camera applications
- Check system resources

### Capture folder not opening
- Verify `captures/` directory exists
- Check file system permissions

## File Naming Convention
```
SN_ORIENTATION_YYYYMMDD_HHMMSS.png

Example:
SN12345_TOP_20251216_143022.png
```

## Code Style Notes
- CustomTkinter widgets prefixed with `ctk.`
- Threading for async operations
- Dark theme color palette: #1a1a1a, #00B4FF, #FFA500
- Emoji icons in buttons for visual clarity
- Type annotations not used (Python 3.x compatible)
