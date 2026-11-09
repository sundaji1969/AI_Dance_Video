
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

from moviepy import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips
)

# ==========================================
# 1. PROJECT CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. INPUT FILES
# ==========================================

GROUP_IMAGE = INPUT_DIR / "group_men.jpg"
COUPLE_IMAGE = INPUT_DIR / "couple.jpg"
FEMALE_IMAGE = INPUT_DIR / "female.jpg"

MUSIC_FILE = INPUT_DIR / "AUDIO-2026-11-08-22-23-19.mp3"

OUTPUT_VIDEO = OUTPUT_DIR / "DANCE_VIDEO_TEST.mp4"

# ==========================================
# 3. VIDEO SETTINGS
# ==========================================

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080

FPS = 24
TOTAL_DURATION = 30

CLIP_DURATIONS = [10, 10, 10]


# ==========================================
# 4. VERIFY INPUT FILES
# ==========================================

def check_files():

    print("\nChecking input files...")

    files = [
        GROUP_IMAGE,
        COUPLE_IMAGE,
        FEMALE_IMAGE,
        MUSIC_FILE
    ]

    for file in files:

        if not file.exists():

            raise FileNotFoundError(
                f"File not found: {file}"
            )

        print(f"FOUND: {file.name}")

    print("\nAll files verified successfully!")


# ==========================================
# 5. PREPARE PHOTOGRAPHS
# ==========================================

def prepare_image(image_path):

    print(f"Processing: {image_path.name}")

    image = Image.open(image_path).convert("RGB")

    image = ImageOps.fit(
        image,
        (VIDEO_WIDTH, VIDEO_HEIGHT),
        method=Image.Resampling.LANCZOS
    )

    # IMPORTANT FIX:
    # Convert PIL Image into NumPy array

    image_array = np.array(image)

    return image_array


# ==========================================
# 6. CREATE VIDEO CLIPS
# ==========================================

def create_video_clips():

    print("\nPreparing photographs...")

    group = prepare_image(GROUP_IMAGE)

    couple = prepare_image(COUPLE_IMAGE)

    female = prepare_image(FEMALE_IMAGE)

    print("\nCreating video clips...")

    clips = [

        ImageClip(group).with_duration(10),

        ImageClip(couple).with_duration(10),

        ImageClip(female).with_duration(10)

    ]

    return clips


# ==========================================
# 7. ADD ORIGINAL BACKGROUND MUSIC
# ==========================================

def add_background_music(video):

    print("\nLoading original MP3...")

    audio = AudioFileClip(str(MUSIC_FILE))

    if audio.duration < TOTAL_DURATION:

        audio.close()

        raise ValueError(
            "MP3 duration must be at least 30 seconds."
        )

    audio = audio.subclipped(0, TOTAL_DURATION)

    video = video.with_audio(audio)

    return video, audio


# ==========================================
# 8. GENERATE FINAL VIDEO
# ==========================================

def export_video(video):

    print("\nStarting video rendering...")

    video.write_videofile(

        str(OUTPUT_VIDEO),

        fps=FPS,

        codec="libx264",

        audio_codec="aac",

        preset="medium",

        threads=4

    )


# ==========================================
# 9. MAIN EXECUTION
# ==========================================

def main():

    clips = []
    video = None
    audio = None

    try:

        print("\n================================")
        print("    AI DANCE VIDEO CREATOR")
        print("================================")

        # Verify all input files
        check_files()

        # Create three video clips
        clips = create_video_clips()

        # Combine clips
        print("\nCombining video clips...")

        video = concatenate_videoclips(
            clips,
            method="compose"
        )

        # Add music
        video, audio = add_background_music(video)

        # Export MP4
        export_video(video)

        print("\n================================")
        print(" VIDEO GENERATED SUCCESSFULLY!")
        print("================================")

        print(f"\nSaved at: {OUTPUT_VIDEO}")

    except Exception as error:

        print("\nVIDEO GENERATION FAILED!")

        print(f"Error: {error}")

    finally:

        if video is not None:
            video.close()

        if audio is not None:
            audio.close()

        for clip in clips:
            clip.close()


# ==========================================
# 10. RUN PROGRAM
# ==========================================

if __name__ == "__main__":

    main()
