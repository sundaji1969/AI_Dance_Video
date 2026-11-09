
from pathlib import Path
from dotenv import load_dotenv
import os
import base64
import requests
import json

# ==========================================
# PROJECT PATHS
# ==========================================

PROJECT = Path(__file__).resolve().parent.parent

IMAGE_FILE = PROJECT / "Output" / "seven_member_copacabana.png"
BASE64_FILE = PROJECT / "generated_clips" / "kling_image_base64.txt"
TASK_FILE = PROJECT / "generated_clips" / "copacabana_task_1.txt"

PROJECT.joinpath("generated_clips").mkdir(
    parents=True, exist_ok=True
)

# ==========================================
# LOAD API KEY
# ==========================================

load_dotenv(PROJECT / ".env", override=True)

API_KEY = os.getenv("KLING_API_KEY", "").strip()

if not API_KEY:
    raise ValueError("KLING_API_KEY missing from .env")

if not IMAGE_FILE.exists():
    raise FileNotFoundError(IMAGE_FILE)

# ==========================================
# PREPARE IMAGE AS BASE64 DATA URI
# ==========================================

print("Preparing seven-member image...")

image_bytes = IMAGE_FILE.read_bytes()

encoded_image = base64.b64encode(
    image_bytes
).decode("utf-8")

image_data_uri = "data:image/png;base64," + encoded_image

print("Image size:", len(image_bytes), "bytes")

# ==========================================
# KLING VIDEO PROMPT
# ==========================================

prompt = """
Create a realistic, energetic Tamil mass dance video
featuring exactly seven people from the supplied image.

All seven people must dance together simultaneously
in one wide-angle group formation on Copacabana Beach,
Rio de Janeiro, Brazil.

Preserve the original faces, identities, hairstyles,
clothing and appearance of all seven people.

Do not add or remove people.
Do not merge faces or duplicate participants.

Choreography:
Start with synchronized shoulder movements and
energetic Tamil-style hand gestures.

Continue with coordinated side steps, rhythmic footwork,
small turns and group formation changes.

All seven participants should move together,
with energetic expressions and natural body movement.

Finish with a powerful synchronized group dance pose.

Keep all seven people visible throughout the video.
Use a wide full-body camera view.
Keep the real beach background visually consistent.

Photorealistic human movement, natural proportions,
realistic lighting and cinematic beach atmosphere.
"""

# ==========================================
# KLING API REQUEST
# ==========================================

API_URL = (
    "https://api-singapore.klingai.com/"
    "image-to-video/kling-4.0"
)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "contents": [
        {
            "type": "prompt",
            "text": prompt
        },
        {
            "type": "first_frame",
            "url": image_data_uri
        }
    ],
    "settings": {
        "resolution": "1080p",
        "duration": 30
    },
    "options": {
        "watermark_info": {
            "enabled": False
        }
    }
}

# ==========================================
# SUBMIT VIDEO GENERATION
# ==========================================

print("\nSubmitting 30-second video to Kling...")
print("Please wait...")

response = requests.post(
    API_URL,
    headers=headers,
    json=payload,
    timeout=180
)

print("HTTP status:", response.status_code)

try:
    result = response.json()
except ValueError:
    raise RuntimeError(
        "Kling returned a non-JSON response: "
        + response.text[:1000]
    )

print("\nKLING RESPONSE:")
print(json.dumps(result, indent=2))

if response.status_code not in (200, 201):
    raise RuntimeError(
        f"Kling API error: {response.status_code}"
    )

if result.get("code") not in (None, 0):
    raise RuntimeError(
        f"Kling rejected the request: {result}"
    )

task_id = result.get("data", {}).get("id")

if not task_id:
    raise RuntimeError(
        "Task ID not found in Kling response."
    )

TASK_FILE.write_text(
    str(task_id),
    encoding="utf-8"
)

print("\nSUCCESS: Kling task submitted.")
print("Task ID:", task_id)
print("Saved task ID:", TASK_FILE)
print("\nVideo generation is now running.")
