
from pathlib import Path
from moviepy import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips,
    concatenate_audioclips,
)

PROJECT = Path(__file__).resolve().parent.parent

VIDEO_FILE = (
    PROJECT / "generated_clips" / "copacabana_dance_clip_1.mp4"
)

AUDIO_FILE = (
    PROJECT / "Input" / "AUDIO-2026-11-08-22-23-19.mp3"
)

OUTPUT_FOLDER = PROJECT / "Output"
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_FOLDER / "FINAL_SEVEN_MEMBER_DANCE.mp4"

TARGET_DURATION = 60

if not VIDEO_FILE.exists():
    raise FileNotFoundError(f"Video not found: {VIDEO_FILE}")

if not AUDIO_FILE.exists():
    raise FileNotFoundError(f"MP3 not found: {AUDIO_FILE}")

print("Loading Kling dance video...")
video = VideoFileClip(str(VIDEO_FILE)).without_audio()

print("Loading original MP3 song...")
audio = AudioFileClip(str(AUDIO_FILE))

# Repeat the dance clip until it reaches 60 seconds
repeat_count = int(TARGET_DURATION // video.duration) + 1

video_parts = [video] * repeat_count
final_video = concatenate_videoclips(
    video_parts, method="compose"
).subclipped(0, TARGET_DURATION)

# Trim the song or repeat it if it is shorter than 60 seconds
if audio.duration >= TARGET_DURATION:
    final_audio = audio.subclipped(0, TARGET_DURATION)
else:
    audio_repeat_count = int(TARGET_DURATION // audio.duration) + 1
    audio_parts = [audio] * audio_repeat_count

    final_audio = concatenate_audioclips(
        audio_parts
    ).subclipped(0, TARGET_DURATION)

# Add the original song to the video
final_video = final_video.with_audio(final_audio)

print("Creating final 60-second video...")

final_video.write_videofile(
    str(OUTPUT_FILE),
    codec="libx264",
    audio_codec="aac",
    fps=video.fps,
    preset="medium",
    threads=4
)

video.close()
audio.close()
final_video.close()
final_audio.close()

print("\nSUCCESS!")
print("Final video:", OUTPUT_FILE)
print("Duration: 60 seconds")
