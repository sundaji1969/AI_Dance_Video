
from pathlib import Path
from dotenv import load_dotenv
import os
import base64
import json
import requests

# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

PROJECT = Path(__file__).resolve().parent.parent

IMAGE_FILE = PROJECT / "Output" / "seven_member_beach.png"
CLIP_FOLDER = PROJECT / "generated_clips"

CLIP_FOLDER.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# 2. LOAD KLING API KEY
# --------------------------------------------------

load_dotenv(PROJECT / ".env", override=True)

API_KEY = os.getenv("KLING_API_KEY", "").strip()

if not API_KEY:
    raise ValueError(
        "KLING_API_KEY not found in main project .env file."
    )

if not IMAGE_FILE.exists():
    raise FileNotFoundError(
        f"Composite image not found: {IMAGE_FILE}"
    )

# --------------------------------------------------
# 3. CONVERT IMAGE TO BASE64 DATA URI
# --------------------------------------------------

print("Preparing seven-member beach image...")

with open(IMAGE_FILE, "rb") as image:
    image_base64 = base64.b64encode(
        image.read()
    ).decode("utf-8")

image_data_uri = (
    "data:image/png;base64," + image_base64
)

print("Image prepared successfully.")

# --------------------------------------------------
# 4. KLING 4.0 API CONFIGURATION
# --------------------------------------------------

API_URL = (
    "https://api-singapore.klingai.com/"
    "image-to-video/kling-4.0"
)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# --------------------------------------------------
# 5. DANCE ANIMATION PROMPT
# --------------------------------------------------

prompt = """
Create a realistic, energetic seven-person Tamil mass dance
on a beach at sunset.

Animate all seven people together in the same wide group shot.

Preserve the original faces, hairstyles, clothing and
identities of all seven people as closely as possible.

Dance choreography:
- Synchronized shoulder movements.
- Energetic Tamil-style hand gestures.
- Coordinated rhythmic group movements.
- Simple synchronized footwork.
- A powerful coordinated group finale pose.

Keep all seven participants visible throughout the video.

Do not add or remove people.
Do not merge bodies or duplicate faces.
Avoid close-ups and camera cuts.
Keep the original beach background.

Realistic human movement and natural body proportions.
"""

# --------------------------------------------------
# 6. PREPARE API REQUEST
# --------------------------------------------------

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
        "resolution": "720p",
        "duration": 5
    },
    "options": {
        "watermark_info": {
            "enabled": False
        }
    }
}

# --------------------------------------------------
# 7. SUBMIT KLING VIDEO GENERATION TASK
# --------------------------------------------------

print("\nSubmitting Kling 4.0 request...")
print("Model: Kling 4.0")
print("Duration: 5 seconds")
print("Resolution: 720p")
print("Participants: 7")

try:
    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=120
    )

    print("\nHTTP STATUS:", response.status_code)

    if not response.ok:
        print("KLING API ERROR:")
        print(response.text[:2000])
        response.raise_for_status()

    result = response.json()

    print("\nKLING RESPONSE:")
    print(json.dumps(result, indent=2))

    # Check API-level response
    if result.get("code") not in (None, 0):
        raise RuntimeError(
            f"Kling rejected request: {result.get('message')}"
        )

    task_data = result.get("data", {})
    task_id = task_data.get("id")

    if not task_id:
        raise RuntimeError(
            "Kling response did not contain a task ID."
        )

    # Save task ID for checking generation status
    task_file = CLIP_FOLDER / "kling_task_id.txt"

    task_file.write_text(
        task_id,
        encoding="utf-8"
    )

    print("\nSUCCESS!")
    print("Kling task submitted.")
    print("Task ID:", task_id)
    print("Saved in:", task_file)

except requests.exceptions.RequestException as error:
    print("\nNETWORK OR API ERROR:")
    print(str(error))
    raise

except Exception as error:
    print("\nERROR:")
    print(str(error))
    raise
