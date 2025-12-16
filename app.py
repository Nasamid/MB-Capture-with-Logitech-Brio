import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import cv2
import glob
import threading
from PIL import Image, ImageTk
import subprocess
import os
import platform

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class CameraZoomController:
    def __init__(self, root):
        self.root = root
        self.root.title("Logitech Brio Capture Controller")
        
        # Set default geometry - will update after window is realized
        self.root.geometry("960x1050+0+0")
        self.root.resizable(False, False)
        
        self.camera = None
        self.cap = None
        self.digital_zoom_level = 1.0
        self.focus_level = 0
        self.is_running = False
        self.camera_thread = None
        self.init_thread = None
        self.is_loading = False
        self.selected_camera_index = 0
        self.available_cameras = {}
        self.camera_width = 0
        self.camera_height = 0
        self.sn_history = []
        self.sn_history_index = -1
        # Orientation appended to filename: either 'TOP' or 'BOTTOM'
        self.orientation = "TOP"
        self.frame_skip_counter = 0
        self.capture_flicker_counter = 0  # For white flicker on capture
        self.show_white_flicker = False  # Flag to show white flicker
        self.pan_x = 0  # Pan offset X (0 = center)
        self.pan_y = 0  # Pan offset Y (0 = center)
        
        # Create UI
        self.create_ui()
        
        # Bind window realization to set proper geometry
        self.root.after(100, self.setup_window_geometry)
        
        # Bind keyboard arrows for panning
        self.root.bind("<Up>", self.pan_up_key)
        self.root.bind("<Down>", self.pan_down_key)
        self.root.bind("<Left>", self.pan_left_key)
        self.root.bind("<Right>", self.pan_right_key)
        
        # Defer camera detection to avoid blocking UI (run in background thread)
        # Only detect cameras, don't initialize yet - wait for user selection
        self.root.after(100, lambda: threading.Thread(target=self.detect_cameras, daemon=True).start())
    
    def setup_window_geometry(self):
        """Set window geometry after it's realized"""
        try:
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Only update if screen dimensions are valid (> 100)
            if screen_width > 100 and screen_height > 100:
                window_width = screen_width // 2
                window_height = screen_height - 50
                self.root.geometry(f"{window_width}x{window_height}+0+0")
        except:
            pass
    
    def show_loading_overlay(self, message="🎥 Initializing Camera..."):
        """Show loading overlay with message"""
        self.overlay_label.configure(text=message)
        self.loading_overlay.place(x=0, y=0, relwidth=1, relheight=1)
        self.root.update()
    
    def hide_loading_overlay(self):
        """Hide loading overlay"""
        self.loading_overlay.place_forget()
        self.root.update()
    
    def create_ui(self):
        """Create the modern UI layout"""
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Store main_frame reference for overlay
        self.main_frame = main_frame
        
        # Create loading overlay (initially hidden) - Frame with semi-transparent effect
        self.loading_overlay = ctk.CTkFrame(self.root, fg_color="gray25")  # Dark semi-transparent look
        
        self.overlay_label = ctk.CTkLabel(
            self.loading_overlay,
            text="🎥 Initializing Camera...",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        self.overlay_label.pack(expand=True)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Logitech Brio Camera Zoom Control",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#00B4FF"
        )
        title_label.pack(pady=(0, 15))
        
        # Camera selection frame
        camera_select_frame = ctk.CTkFrame(main_frame, fg_color="#1a1a1a", corner_radius=10)
        camera_select_frame.pack(fill="x", pady=(0, 15))
        
        camera_label = ctk.CTkLabel(
            camera_select_frame,
            text="Select Camera:",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        camera_label.pack(side="left", padx=15, pady=10)
        
        self.camera_combo = ctk.CTkComboBox(
            camera_select_frame,
            values=["Scanning..."],
            command=self.on_camera_selected,
            font=ctk.CTkFont(size=11),
            dropdown_font=ctk.CTkFont(size=10),
            state="disabled"
        )
        self.camera_combo.pack(side="left", padx=5, fill="x", expand=True)
        self.camera_combo.set("Scanning...")
        
        # Loading indicator
        self.loading_label = ctk.CTkLabel(
            camera_select_frame,
            text="",
            font=ctk.CTkFont(size=10),
            text_color="#FFA500"
        )
        self.loading_label.pack(side="right", padx=5)
        
        refresh_btn = ctk.CTkButton(
            camera_select_frame,
            text="Refresh",
            width=80,
            command=self.detect_cameras,
            fg_color="#00B4FF",
            hover_color="#0090CC",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        refresh_btn.pack(side="right", padx=5)
        
        # Serial Number input frame
        sn_frame = ctk.CTkFrame(main_frame, fg_color="#1a1a1a", corner_radius=10)
        sn_frame.pack(fill="x", pady=(0, 15))
        
        sn_label = ctk.CTkLabel(
            sn_frame,
            text="Serial Number (SN):",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        sn_label.pack(side="left", padx=15, pady=10)
        
        self.sn_entry = ctk.CTkEntry(
            sn_frame,
            placeholder_text="Enter camera SN",
            font=ctk.CTkFont(size=11),
            width=300
        )
        self.sn_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.sn_entry.bind("<Up>", self.on_sn_up_arrow)
        self.sn_entry.bind("<Down>", self.on_sn_down_arrow)
        self.sn_entry.bind("<Return>", self.on_sn_enter)
        
        sn_info_label = ctk.CTkLabel(
            sn_frame,
            text="↑↓ to browse",
            font=ctk.CTkFont(size=10),
            text_color="#666666"
        )
        sn_info_label.pack(side="right", padx=15, pady=10)

        # Orientation toggle buttons (TOP / BOTTOM)
        orientation_frame = ctk.CTkFrame(sn_frame, fg_color="transparent")
        orientation_frame.pack(side="right", padx=5)

        self.top_btn = ctk.CTkButton(
            orientation_frame,
            text="TOP",
            width=70,
            command=lambda: self.set_orientation("TOP"),
            fg_color="#00B4FF",
            hover_color="#0090CC",
            font=ctk.CTkFont(size=10, weight="bold")
        )
        self.top_btn.pack(side="left", padx=(0, 5))

        self.bottom_btn = ctk.CTkButton(
            orientation_frame,
            text="BOTTOM",
            width=70,
            command=lambda: self.set_orientation("BOTTOM"),
            fg_color="#666666",
            hover_color="#888888",
            font=ctk.CTkFont(size=10, weight="bold")
        )
        self.bottom_btn.pack(side="left")

        # Initialize button styles/status
        self.set_orientation(self.orientation)
        
        # Camera preview frame
        preview_frame = ctk.CTkFrame(main_frame, fg_color="#1a1a1a", corner_radius=15)
        preview_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        self.preview_label = ctk.CTkLabel(
            preview_frame,
            text="Camera Preview",
            font=ctk.CTkFont(size=14),
            fg_color="#262626",
            text_color="#888888",
            corner_radius=10
        )
        self.preview_label.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Control panel
        control_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        control_frame.pack(fill="x")
        
        # Zoom level display
        info_frame = ctk.CTkFrame(control_frame, fg_color="#1a1a1a", corner_radius=10)
        info_frame.pack(fill="x", pady=(0, 15))
        
        zoom_info_label = ctk.CTkLabel(
            info_frame,
            text="Zoom Level:",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        zoom_info_label.pack(side="left", padx=15, pady=10)
        
        self.zoom_display = ctk.CTkLabel(
            info_frame,
            text="Zoom: 1.0x",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#00B4FF"
        )
        self.zoom_display.pack(side="right", padx=15, pady=10)
        
        # Resolution display
        self.resolution_display = ctk.CTkLabel(
            info_frame,
            text="Resolution: — ",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.resolution_display.pack(side="left", padx=15, pady=10)
        
        # Digital Zoom Slider
        zoom_slider_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        zoom_slider_frame.pack(fill="x", pady=(0, 15))
        
        zoom_slider_label = ctk.CTkLabel(
            zoom_slider_frame,
            text="Digital Zoom:",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        zoom_slider_label.pack(side="left", padx=(0, 15))
        
        self.zoom_slider = ctk.CTkSlider(
            zoom_slider_frame,
            from_=1.0,
            to=5.0,
            number_of_steps=40,
            command=self.update_digital_zoom,
            progress_color="#00B4FF",
            button_color="#00B4FF",
            button_hover_color="#0090CC"
        )
        self.zoom_slider.pack(side="left", fill="x", expand=True)
        self.zoom_slider.set(1.0)
        
        # Focus Control Slider
        focus_slider_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        focus_slider_frame.pack(fill="x", pady=(0, 20))
        
        focus_slider_label = ctk.CTkLabel(
            focus_slider_frame,
            text="Camera Focus:",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        focus_slider_label.pack(side="left", padx=(0, 15))
        
        self.focus_slider = ctk.CTkSlider(
            focus_slider_frame,
            from_=0,
            to=255,
            number_of_steps=255,
            command=self.update_focus,
            progress_color="#FFA500",
            button_color="#FFA500",
            button_hover_color="#FF8C00"
        )
        self.focus_slider.pack(side="left", fill="x", expand=True)
        self.focus_slider.set(0)
        
        # Button frame
        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=15)
        
        # Pan arrow buttons
        pan_up_btn = ctk.CTkButton(
            button_frame,
            text="⬆ Up",
            width=60,
            command=self.pan_up,
            fg_color="#0099FF",
            hover_color="#0077CC",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        pan_up_btn.pack(side="left", padx=5)
        
        pan_down_btn = ctk.CTkButton(
            button_frame,
            text="⬇ Down",
            width=60,
            command=self.pan_down,
            fg_color="#0099FF",
            hover_color="#0077CC",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        pan_down_btn.pack(side="left", padx=5)
        
        pan_left_btn = ctk.CTkButton(
            button_frame,
            text="⬅ Left",
            width=60,
            command=self.pan_left,
            fg_color="#0099FF",
            hover_color="#0077CC",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        pan_left_btn.pack(side="left", padx=5)
        
        pan_right_btn = ctk.CTkButton(
            button_frame,
            text="➡ Right",
            width=60,
            command=self.pan_right,
            fg_color="#0099FF",
            hover_color="#0077CC",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        pan_right_btn.pack(side="left", padx=5)
        
        # Reset pan button
        reset_pan_btn = ctk.CTkButton(
            button_frame,
            text="⊕ Center",
            width=60,
            command=self.reset_pan,
            fg_color="#666666",
            hover_color="#888888",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        reset_pan_btn.pack(side="left", padx=5)
        
        # Capture button
        capture_btn = ctk.CTkButton(
            button_frame,
            text="📷 Capture (Space)",
            command=self.capture_image,
            fg_color="#9B0E0E",
            hover_color="#0B7809",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        capture_btn.pack(side="left", padx=15)
        
        # Open folder button
        open_folder_btn = ctk.CTkButton(
            button_frame,
            text="📁 Open Captures",
            command=self.open_captures_folder,
            fg_color="#FF9500",
            hover_color="#FF7700",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        open_folder_btn.pack(side="left", padx=5)
        
        # Status frame
        status_frame = ctk.CTkFrame(control_frame, fg_color="#1a1a1a", corner_radius=10)
        status_frame.pack(fill="x", pady=15)
        
        status_label = ctk.CTkLabel(
            status_frame,
            text="Status:",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        status_label.pack(side="left", padx=15, pady=10)
        
        self.status_display = ctk.CTkLabel(
            status_frame,
            text="Initializing...",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#FFA500"
        )
        self.status_display.pack(side="right", padx=15, pady=10)
    
    def on_sn_enter(self, event):
        """Save SN to history when Enter is pressed"""
        sn_value = self.sn_entry.get().strip()
        if sn_value:
            # Add to history if not already the last entry
            if not self.sn_history or self.sn_history[-1] != sn_value:
                self.sn_history.append(sn_value)
            self.sn_history_index = -1  # Reset index after entering new SN
    
    def on_sn_up_arrow(self, event):
        """Browse up through SN history"""
        if not self.sn_history:
            return
        
        # Move to previous entry
        if self.sn_history_index < len(self.sn_history) - 1:
            self.sn_history_index += 1
            self.sn_entry.delete(0, "end")
            self.sn_entry.insert(0, self.sn_history[-(self.sn_history_index + 1)])
        
        return "break"  # Prevent default Up arrow behavior
    
    def on_sn_down_arrow(self, event):
        """Browse down through SN history"""
        if not self.sn_history or self.sn_history_index <= 0:
            self.sn_entry.delete(0, "end")
            self.sn_history_index = -1
            return
        
        # Move to next entry
        self.sn_history_index -= 1
        self.sn_entry.delete(0, "end")
        if self.sn_history_index >= 0:
            self.sn_entry.insert(0, self.sn_history[-(self.sn_history_index + 1)])
        
        return "break"  # Prevent default Down arrow behavior

    def set_orientation(self, value: str):
        """Set orientation for filenames and update button styles"""
        value = value.upper()
        if value not in ("TOP", "BOTTOM"):
            return

        self.orientation = value

        # Update visual state of buttons
        if self.orientation == "TOP":
            self.top_btn.configure(fg_color="#00B4FF", hover_color="#0090CC")
            self.bottom_btn.configure(fg_color="#666666", hover_color="#888888")
        else:
            self.bottom_btn.configure(fg_color="#00B4FF", hover_color="#0090CC")
            self.top_btn.configure(fg_color="#666666", hover_color="#888888")

        # Brief status feedback
        try:
            self.status_display.configure(text=f"Orientation: {self.orientation}", text_color="#00B4FF")
        except Exception:
            pass
    
    def detect_cameras(self):
        """Detect all available cameras and identify Brio (runs in background thread)"""
        self.available_cameras = {}
        detected = []
        import time

        # Scan for cameras (optimized range with timeout per camera)
        for index in range(3):  # Reduced range to 0-2 for faster detection
            try:
                # Set a timeout for opening each camera
                start_time = time.time()
                cap = cv2.VideoCapture(index)
                
                # Give it max 1 second to open
                open_timeout = 1.0
                while not cap.isOpened() and (time.time() - start_time) < open_timeout:
                    import time as t
                    t.sleep(0.05)

                if cap.isOpened():
                    # Get camera resolution only (fastest properties)
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                    # Try to identify camera name
                    camera_name = f"Camera {index}"

                    # Check if it's a Brio (typically higher resolution like 4K capable)
                    if width >= 1920 and height >= 1080:
                        camera_name = f"🎥 Brio (Index {index})"
                        self.selected_camera_index = index  # Auto-select Brio if found

                    self.available_cameras[camera_name] = index
                    detected.append(camera_name)
                    print(f"Found: {camera_name}")
                
                cap.release()
            except Exception as e:
                print(f"Error detecting camera at index {index}: {e}")

        # Update UI on main thread
        def update_ui():
            if detected:
                self.camera_combo.configure(values=detected, state="readonly")
                # Select Brio if found, otherwise first camera
                brio_found = any("Brio" in cam for cam in detected)
                if brio_found:
                    brio_cam = next(cam for cam in detected if "Brio" in cam)
                    self.camera_combo.set(brio_cam)
                else:
                    self.camera_combo.set(detected[0])
                    self.selected_camera_index = self.available_cameras[detected[0]]
                
                # Auto-initialize when cameras are found
                print("Cameras detected, initializing...")
                self.initialize_camera()
            else:
                self.camera_combo.configure(values=["No cameras found"], state="disabled")
                self.camera_combo.set("No cameras found")

        self.root.after(0, update_ui)
    
    def on_camera_selected(self, choice):
        """Handle camera selection change - runs in background thread"""
        if choice in self.available_cameras:
            self.selected_camera_index = self.available_cameras[choice]
            self.is_loading = True
            self.camera_combo.configure(state="disabled")
            self.show_loading_overlay("🎥 Switching Camera...")
            
            # Initialize camera in background thread
            self.init_thread = threading.Thread(target=self._initialize_camera_background, daemon=True)
            self.init_thread.start()
    
    def initialize_camera(self):
        """Initialize the camera in background thread"""
        self.is_loading = True
        self.init_thread = threading.Thread(target=self._initialize_camera_background, daemon=True)
        self.init_thread.start()
    
    def _initialize_camera_background(self):
        """Initialize the camera (runs in background)"""
        try:
            self.cap = cv2.VideoCapture(self.selected_camera_index)
            
            # Fast timeout for camera to be ready (reduced from 5s to 1s)
            timeout = 0
            while not self.cap.isOpened() and timeout < 10:  # 1 second timeout
                timeout += 1
                threading.Event().wait(0.1)
            
            if self.cap.isOpened():
                # Set camera buffer size to 1 (grab latest frame immediately)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                # Request 4K resolution for Brio (3840x2160)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
                
                # Get actual camera resolution (may be negotiated lower if 4K not available)
                self.camera_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                self.camera_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                print(f"Camera opened: {self.camera_width}×{self.camera_height}")
                
                # Update resolution display
                self.resolution_display.configure(
                    text=f"Resolution: {self.camera_width}×{self.camera_height}",
                    text_color="#00B4FF"
                )
                
                # Minimal warm-up: discard only 5 frames quickly
                print("Warming up camera...")
                frame_count = 0
                for i in range(5):  # Reduced to 5 frames for fast startup
                    ret, frame = self.cap.read()
                    if ret:
                        frame_count += 1
                    # No delay - read as fast as possible
                
                print(f"Warm-up complete: read {frame_count}/5 frames")
                
                self.status_display.configure(text="Camera Connected ✓", text_color="#00FF00")
                self.is_running = True
                self.camera_thread = threading.Thread(target=self.update_preview, daemon=True)
                self.camera_thread.start()
            else:
                self.status_display.configure(text="Camera Not Found", text_color="#FF0000")
        except Exception as e:
            self.status_display.configure(text=f"Error: {str(e)}", text_color="#FF0000")
        
        finally:
            self.is_loading = False
            self.loading_label.configure(text="")
            self.hide_loading_overlay()  # Hide overlay when initialization completes
    
    def update_preview(self):
        """Update camera preview with digital zoom"""
        retry_count = 0
        max_retries = 10
        frame_display_count = 0
        
        while self.is_running and self.cap:
            try:
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    retry_count += 1
                    if retry_count > max_retries:
                        print(f"Preview: No valid frames received after {max_retries} retries")
                        self.status_display.configure(text="Preview Error: No frames", text_color="#FF0000")
                        break
                    threading.Event().wait(0.1)
                    continue
                
                retry_count = 0  # Reset retry counter on successful read
                
                # Check if we should show white flicker (capture feedback)
                if self.show_white_flicker:
                    self.capture_flicker_counter += 1
                    if self.capture_flicker_counter < 3:  # Show white for ~3 frames
                        # Create white frame
                        white_frame = cv2.resize(frame, (960, 540))
                        white_frame[:] = (255, 255, 255)  # White in BGR
                        white_frame = cv2.cvtColor(white_frame, cv2.COLOR_BGR2RGB)
                        
                        image = Image.fromarray(white_frame)
                        photo = ImageTk.PhotoImage(image)
                        
                        self.preview_label.configure(image=photo, text="")
                        self.preview_label.image = photo
                        continue
                    else:
                        # Flicker done, reset flag
                        self.show_white_flicker = False
                
                # Skip frames for performance (only update UI every 2nd frame for faster preview)
                self.frame_skip_counter += 1
                if self.frame_skip_counter < 2:
                    continue
                self.frame_skip_counter = 0
                frame_display_count += 1
                
                if frame_display_count == 1:
                    print(f"First preview frame rendered: {frame.shape}")
                
                # Apply digital zoom with pan offset
                if self.digital_zoom_level > 1.0:
                    h, w = frame.shape[:2]
                    crop_w = int(w / self.digital_zoom_level)
                    crop_h = int(h / self.digital_zoom_level)
                    
                    # Calculate center with pan offset
                    center_x = (w - crop_w) // 2 + self.pan_x
                    center_y = (h - crop_h) // 2 + self.pan_y
                    
                    # Clamp to valid bounds
                    center_x = max(0, min(center_x, w - crop_w))
                    center_y = max(0, min(center_y, h - crop_h))
                    
                    x = center_x
                    y = center_y
                    frame = frame[y:y+crop_h, x:x+crop_w]
                
                # Resize frame for preview (optimize: use smaller preview size)
                frame = cv2.resize(frame, (960, 540))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to PhotoImage
                image = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image)
                
                # Update label
                self.preview_label.configure(image=photo, text="")
                self.preview_label.image = photo
            except Exception as e:
                print(f"Preview exception: {str(e)}")
                self.status_display.configure(text=f"Preview Error: {str(e)[:30]}", text_color="#FF0000")
                threading.Event().wait(0.5)
                continue
    
    def update_digital_zoom(self, value):
        """Update digital zoom level from slider"""
        self.digital_zoom_level = float(value)
        self.zoom_display.configure(text=f"Zoom: {self.digital_zoom_level:.1f}x")
    
    def set_digital_zoom(self, zoom_value):
        """Set preset digital zoom level"""
        self.digital_zoom_level = zoom_value
        self.zoom_slider.set(zoom_value)
        self.zoom_display.configure(text=f"Zoom: {self.digital_zoom_level:.1f}x")
    
    def pan_up(self):
        """Pan preview up"""
        self.pan_y = max(self.pan_y - 30, -500)
    
    def pan_down(self):
        """Pan preview down"""
        self.pan_y = min(self.pan_y + 30, 500)
    
    def pan_left(self):
        """Pan preview left"""
        self.pan_x = max(self.pan_x - 30, -500)
    
    def pan_right(self):
        """Pan preview right"""
        self.pan_x = min(self.pan_x + 30, 500)
    
    def reset_pan(self):
        """Reset pan to center"""
        self.pan_x = 0
        self.pan_y = 0
    
    def pan_up_key(self, event):
        """Keyboard event for pan up"""
        self.pan_up()
    
    def pan_down_key(self, event):
        """Keyboard event for pan down"""
        self.pan_down()
    
    def pan_left_key(self, event):
        """Keyboard event for pan left"""
        self.pan_left()
    
    def pan_right_key(self, event):
        """Keyboard event for pan right"""
        self.pan_right()
    
    def update_focus(self, value):
        """Update camera focus"""
        self.focus_level = int(float(value))
        try:
            if self.cap and self.cap.isOpened():
                # Try to set focus property
                self.cap.set(28, self.focus_level)
                self.status_display.configure(text=f"Focus: {self.focus_level}", text_color="#FFA500")
        except Exception as e:
            pass
    
    def apply_zoom(self):
        """Apply zoom to Logitech Brio camera"""
        if not self.cap or not self.cap.isOpened():
            self.status_display.configure(text="Camera not connected", text_color="#FF0000")
            return
        
        try:
            # Logitech Brio zoom control using v4l2-ctl (works on Windows with WSL or direct)
            zoom_value = int(self.digital_zoom_level * 128)  # Scale to 0-1280 (1x=128, 10x=1280)
            
            if platform.system() == "Windows":
                # Try multiple approaches for Windows
                try:
                    # Approach 1: Direct property set
                    self.cap.set(28, zoom_value)  # Try setting through OpenCV
                    self.status_display.configure(text=f"Zoom: {self.digital_zoom_level:.1f}x ✓", text_color="#00FF00")
                    return
                except:
                    pass
                
                try:
                    # Approach 2: Use PowerShell with WinRT or Win32 API
                    # This is for Logitech camera control
                    cmd = f'powershell -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait(\\"{{+}}{{+}}{int(self.digital_zoom_level * 5)}\\")"'
                    subprocess.run(cmd, shell=True, capture_output=True, timeout=1)
                    self.status_display.configure(text=f"Zoom: {self.digital_zoom_level:.1f}x", text_color="#00B4FF")
                    return
                except:
                    pass
                
            else:  # Linux/WSL
                try:
                    cmd = f"v4l2-ctl -d /dev/video{self.selected_camera_index} -c zoom_absolute={zoom_value}"
                    subprocess.run(cmd, shell=True, capture_output=True, timeout=1)
                    self.status_display.configure(text=f"Zoom: {self.digital_zoom_level:.1f}x ✓", text_color="#00FF00")
                    return
                except:
                    pass
            
            self.status_display.configure(text=f"Zoom: {self.digital_zoom_level:.1f}x (Set)", text_color="#00B4FF")
            
        except Exception as e:
            self.status_display.configure(text=f"Zoom pending...", text_color="#FFA500")
    
    def on_closing(self):
        """Clean up resources on close"""
        self.is_running = False
        if self.init_thread and self.init_thread.is_alive():
            self.init_thread.join(timeout=1)
        if self.camera_thread and self.camera_thread.is_alive():
            self.camera_thread.join(timeout=1)
        if self.cap:
            self.cap.release()
        self.root.destroy()
    
    def capture_image(self):
        """Capture and save full resolution image with zoom and focus applied"""
        if not self.cap or not self.cap.isOpened():
            self.status_display.configure(text="Camera not connected", text_color="#FF0000")
            return
        
        try:
            # Get SN from entry field
            sn = self.sn_entry.get().strip()
            if not sn:
                self.status_display.configure(text="Enter SN before capturing", text_color="#FF0000")
                return
            
            # Create captures directory if it doesn't exist
            capture_dir = ("C:/brio_captures/captures")
            os.makedirs(capture_dir, exist_ok=True)

            # Prepare SN folder
            orientation = (getattr(self, "orientation", "TOP") or "TOP").upper()
            safe_sn = sn.replace(" ", "_")
            sn_dir = os.path.join(capture_dir, safe_sn)

            # If SN folder exists and contains files for this orientation, ask to overwrite
            try:
                if os.path.exists(sn_dir):
                    # Check for existing files for this orientation
                    existing = glob.glob(os.path.join(sn_dir, f"{safe_sn}_{orientation}_*.png"))
                    if existing:
                        answer = messagebox.askyesno(
                            title="Overwrite image?",
                            message=(f"An existing {orientation} image for SN '{sn}' was found.\n"
                                     "Do you want to overwrite it?")
                        )
                        if not answer:
                            self.status_display.configure(text="Capture cancelled (overwrite declined)", text_color="#FFA500")
                            return
                        else:
                            # Remove all existing files for this orientation
                            for f in existing:
                                try:
                                    os.remove(f)
                                except Exception:
                                    pass
                else:
                    os.makedirs(sn_dir, exist_ok=True)
            except Exception as e:
                # If anything goes wrong during folder checks, abort
                self.status_display.configure(text=f"Folder error: {str(e)[:30]}", text_color="#FF0000")
                return

            # Read frame from camera
            ret, frame = self.cap.read()
            if not ret:
                self.status_display.configure(text="Failed to capture frame", text_color="#FF0000")
                return

            # Apply digital zoom with pan offset to full resolution frame
            if self.digital_zoom_level > 1.0:
                h, w = frame.shape[:2]
                crop_w = int(w / self.digital_zoom_level)
                crop_h = int(h / self.digital_zoom_level)

                # Calculate center with pan offset
                center_x = (w - crop_w) // 2 + self.pan_x
                center_y = (h - crop_h) // 2 + self.pan_y

                # Clamp to valid bounds
                center_x = max(0, min(center_x, w - crop_w))
                center_y = max(0, min(center_y, h - crop_h))

                x = center_x
                y = center_y
                frame = frame[y:y+crop_h, x:x+crop_w]
                # Upscale back to original resolution if zoomed
                frame = cv2.resize(frame, (w, h))

            # Create filename with SN, orientation and timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_sn}_{orientation}_{timestamp}.png"
            filepath = os.path.join(sn_dir, filename)

            # Save the image
            cv2.imwrite(filepath, frame)

            # Ensure SN folder contains strictly only one TOP and one BOTTOM image each
            try:
                for ori in ("TOP", "BOTTOM"):
                    matches = glob.glob(os.path.join(sn_dir, f"{safe_sn}_{ori}_*.png"))
                    if len(matches) > 1:
                        # Keep newest, remove older
                        newest = max(matches, key=os.path.getmtime)
                        for m in matches:
                            if m != newest:
                                try:
                                    os.remove(m)
                                except Exception:
                                    pass
                # Remove any stray files that don't match the expected patterns
                for f in os.listdir(sn_dir):
                    full = os.path.join(sn_dir, f)
                    if os.path.isfile(full) and not (
                        f.startswith(f"{safe_sn}_TOP_") or f.startswith(f"{safe_sn}_BOTTOM_")):
                        try:
                            os.remove(full)
                        except Exception:
                            pass
            except Exception:
                pass

            # Trigger white flicker effect
            self.show_white_flicker = True
            self.capture_flicker_counter = 0

            self.status_display.configure(
                text=f"✓ Captured: {filename}",
                text_color="#00FF00"
            )
        
        except Exception as e:
            self.status_display.configure(
                text=f"Capture error: {str(e)[:30]}",
                text_color="#FF0000"
            )
    
    def open_captures_folder(self):
        """Open captures folder in Explorer"""
        try:
            capture_dir = ("C:/brio_captures/captures")
            os.makedirs(capture_dir, exist_ok=True)
            
            if platform.system() == "Windows":
                os.startfile(capture_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", capture_dir])
            else:  # Linux
                subprocess.Popen(["xdg-open", capture_dir])
            
            self.status_display.configure(
                text="Opening captures folder...",
                text_color="#00B4FF"
            )
        except Exception as e:
            self.status_display.configure(
                text=f"Error: {str(e)[:30]}",
                text_color="#FF0000"
            )


def main():
    root = ctk.CTk()
    app = CameraZoomController(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    # Bind space key globally
    root.bind("<space>", lambda e: app.capture_image())
    root.mainloop()


if __name__ == "__main__":
    main()
