
from pathlib import Path
import os
import requests
import fal_client
from dotenv import load_dotenv

# Project paths
PROJECT = Path(__file__).resolve().parent.parent
IMAGE = PROJECT / "Output" / "seven_member_beach.png"
OUTPUT = PROJECT / "generated_clips"
OUTPUT.mkdir(exist_ok=True)

# Load API key from project root .env
load_dotenv(PROJECT / ".env")

if not os.getenv("FAL_KEY"):
    raise ValueError("FAL_KEY not found. Check your .env file.")

if not IMAGE.exists():
    raise FileNotFoundError(f"Composite image not found: {IMAGE}")

print("Uploading seven-member image to fal.ai...")

# Upload local image
image_url = fal_client.upload_file(str(IMAGE))

print("Image uploaded.")
print("Submitting 5-second Kling dance test...")

prompt = """
Animate all seven people in the reference image dancing together
on the beach at sunset.

Keep all seven people visible together in one wide camera shot.
Preserve their original faces, hairstyles, clothing and identities
as closely as possible.

Create energetic synchronized Tamil mass-dance movements:
rhythmic shoulder movements, coordinated hand gestures,
simple dance steps and group movements.

All seven people should move together.
Finish with a coordinated group dance pose.

Do not add or remove people.
Do not change the beach background.
Avoid camera cuts, close-ups, face distortion and body merging.
"""

# Submit AI video generation request
result = fal_client.subscribe(
    "kling/v4/image-to-video",
    arguments={
        "start_image_url": image_url,
        "prompt": prompt,
        "duration": 5,
        "resolution": "1080p"
    },
    with_logs=True
)

# Retrieve generated video
video_url = result["video"]["url"]

print("Video generated. Downloading...")

response = requests.get(video_url, timeout=180)
response.raise_for_status()

video_path = OUTPUT / "seven_member_dance_test.mp4"
video_path.write_bytes(response.content)

print("\nSUCCESS!")
print("Test video saved at:")
print(video_path)
