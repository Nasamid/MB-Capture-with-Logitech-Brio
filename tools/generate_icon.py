"""Generate a simple .ico file used by the build scripts.

This script creates a 256x256 icon with a colored circle and the letter "B".
It writes `installer/brio_icon.ico` (and copies a PNG for convenience).
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

out_dir = Path(__file__).resolve().parents[1] / "installer"
out_dir.mkdir(parents=True, exist_ok=True)
icon_path = out_dir / "brio_icon.ico"
png_path = out_dir / "brio_icon.png"

# Create a 256x256 RGBA image
size = (256, 256)
img = Image.new("RGBA", size, (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw circle
circle_color = (0, 180, 255, 255)
draw.ellipse((16, 16, 240, 240), fill=circle_color)

# Draw letter B in white
try:
    # Try to get a built-in font
    font = ImageFont.truetype("arial.ttf", 140)
except Exception:
    font = ImageFont.load_default()

text = "B"
# Compute text bounding box for centering (compatible across Pillow versions)
try:
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
except Exception:
    try:
        text_w, text_h = font.getsize(text)
    except Exception:
        text_w, text_h = (100, 100)

text_x = (size[0] - text_w) / 2
text_y = (size[1] - text_h) / 2 - 10

draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255, 255))

# Save as PNG and ICO (ICO can contain multiple sizes; Pillow will handle resizing)
img.save(png_path, format="PNG")
img.save(icon_path, format="ICO")

print(f"Generated icon: {icon_path}")