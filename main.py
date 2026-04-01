#!/usr/bin/env python3
"""
MAIN AUTOMATION SCRIPT
Runs full pipeline:
1. Generate unique Krishna text
2. Create image
3. Render video
4. Upload to YouTube
"""

import os
import sys
import subprocess
from pathlib import Path

# -------------------------
# STEP 0: BASIC CHECKS
# -------------------------

def check_dependencies():
    # Check ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        raise SystemExit("❌ ffmpeg not installed. Install it first.")

    # Check API key
    if not os.getenv("GEMINI_API_KEY"):
        raise SystemExit("❌ GEMINI_API_KEY not set.")

    # Check client secret
    if not Path("client_secret.json").exists():
        raise SystemExit("❌ client_secret.json missing.")

    print("✅ All dependencies OK")


# -------------------------
# STEP 1: GENERATE TEXT
# -------------------------

def generate_text():
    from text_generator import get_krishna_line

    print("🧠 Generating Krishna text...")
    text = get_krishna_line()
    print("📜 Text:", text)
    return text


# -------------------------
# STEP 2: CREATE IMAGE
# -------------------------

def create_image(text):
    from PIL import Image, ImageDraw, ImageFont
    import random
    import textwrap

    IMAGE_FOLDER = "images"
    OUTPUT_PATH = "output/reel_frame.png"
    FONT_PATH = "fonts/NotoSansDevanagari-Regular.ttf"

    os.makedirs("output", exist_ok=True)

    images = [
        f for f in os.listdir(IMAGE_FOLDER)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    if not images:
        raise SystemExit("❌ No images found in images/")

    img_path = os.path.join(IMAGE_FOLDER, random.choice(images))

    print("🖼 Using image:", img_path)

    base = Image.open(img_path).convert("RGB").resize((1080, 1920))
    draw = ImageDraw.Draw(base)

    try:
        font = ImageFont.truetype(FONT_PATH, 64)
    except:
        font = ImageFont.load_default()

    lines = textwrap.wrap(text, width=18)

    y = 800
    for line in lines:
        w = draw.textlength(line, font=font)
        x = (1080 - w) // 2
        draw.text((x, y), line, font=font, fill="white", stroke_width=3, stroke_fill="black")
        y += 80

    base.save(OUTPUT_PATH)
    print("✅ Image created")
    return OUTPUT_PATH


# -------------------------
# STEP 3: CREATE VIDEO
# -------------------------

def create_video(image_path):
    import random

    BGM_DIR = Path("bgm")
    OUTPUT_VIDEO = Path("output/krishna_reel.mp4")

    tracks = list(BGM_DIR.glob("*.mp3")) + list(BGM_DIR.glob("*.wav"))

    if not tracks:
        raise SystemExit("❌ No BGM found")

    bgm = random.choice(tracks)

    print("🎵 Using BGM:", bgm.name)

    cmd = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", image_path,
        "-i", str(bgm),
        "-c:v", "libx264",
        "-t", "15",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
        str(OUTPUT_VIDEO),
    ]

    subprocess.run(cmd, check=True)

    print("✅ Video created")
    return OUTPUT_VIDEO


# -------------------------
# STEP 4: UPLOAD
# -------------------------

def upload_video(video_path):
    from youtube_upload import get_youtube_client, upload_video as up

    print("📤 Uploading to YouTube...")
    youtube = get_youtube_client()
    up(youtube, video_path)


# -------------------------
# MAIN PIPELINE
# -------------------------

def main():
    print("🚀 STARTING FULL AUTOMATION\n")

    check_dependencies()

    text = generate_text()
    image = create_image(text)
    video = create_video(image)

    upload_video(video)

    print("\n🎉 DONE! Full reel uploaded successfully")


if __name__ == "__main__":
    main()
