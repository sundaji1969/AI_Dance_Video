
from pathlib import Path
from dotenv import load_dotenv
import os
import requests
import json

# ==========================================
# 1. PROJECT PATHS
# ==========================================

PROJECT = Path(__file__).resolve().parent.parent

TASK_FILE = (
    PROJECT / "generated_clips" / "copacabana_task_1.txt"
)

OUTPUT_FOLDER = PROJECT / "generated_clips"
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

VIDEO_FILE = OUTPUT_FOLDER / "copacabana_dance_clip_1.mp4"

# ==========================================
# 2. LOAD KLING API KEY
# ==========================================

load_dotenv(PROJECT / ".env", override=True)

API_KEY = os.getenv("KLING_API_KEY", "").strip()

if not API_KEY:
    raise ValueError("KLING_API_KEY missing from .env")

# ==========================================
# 3. READ TASK ID
# ==========================================

if not TASK_FILE.exists():
    raise FileNotFoundError(
        f"Task ID file not found: {TASK_FILE}"
    )

TASK_ID = TASK_FILE.read_text(
    encoding="utf-8"
).strip()

if not TASK_ID:
    raise ValueError("Task ID file is empty.")

print("Kling Task ID:", TASK_ID)

# ==========================================
# 4. CHECK TASK STATUS
# ==========================================

API_URL = "https://api-singapore.klingai.com/tasks"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

params = {
    "task_ids": TASK_ID
}

print("\nChecking Kling video generation status...")

response = requests.get(
    API_URL,
    headers=headers,
    params=params,
    timeout=60
)

print("HTTP Status:", response.status_code)

response.raise_for_status()

result = response.json()

print("\nKLING RESPONSE:")
print(json.dumps(result, indent=2))

if result.get("code") not in (None, 0):
    raise RuntimeError(
        f"Kling API error: {result.get('message', result)}"
    )

# ==========================================
# 5. EXTRACT TASK INFORMATION
# ==========================================

data = result.get("data", {})

if isinstance(data, list):
    tasks = data
elif isinstance(data, dict):
    tasks = data.get("result", [])

    if not tasks and data.get("id") == TASK_ID:
        tasks = [data]
else:
    tasks = []

if not tasks:
    raise RuntimeError(
        "No task information returned. "
        "Check the task ID and API response."
    )

task = next(
    (
        item for item in tasks
        if item.get("id") == TASK_ID
        or item.get("task_id") == TASK_ID
    ),
    tasks[0]
)

status = (
    task.get("status")
    or task.get("task_status")
    or "UNKNOWN"
).lower()

print("\nVIDEO STATUS:", status.upper())

# ==========================================
# 6. HANDLE PROCESSING STATUS
# ==========================================

if status in ("submitted", "processing"):
    print("\nKling is still generating your video.")
    print("Run this script again later.")

# ==========================================
# 7. HANDLE FAILED STATUS
# ==========================================

elif status in ("failed", "failure"):
    print("\nVIDEO GENERATION FAILED.")

    print(
        "Reason:",
        task.get("message")
        or task.get("task_status_msg")
        or "No failure reason supplied."
    )

# ==========================================
# 8. DOWNLOAD COMPLETED VIDEO
# ==========================================

elif status in ("succeeded", "success", "succeed"):

    outputs = task.get("outputs", [])

    # Support the alternate legacy response format
    if not outputs:
        outputs = (
            task.get("task_result", {}).get("videos", [])
        )

    if not outputs:
        raise RuntimeError(
            "Task succeeded, but no video output URL was returned."
        )

    video_url = (
        outputs[0].get("url")
        or outputs[0].get("video_url")
    )

    if not video_url:
        raise RuntimeError("Video URL not found in response.")

    print("\nVideo generation completed!")
    print("Downloading MP4...")

    video_response = requests.get(
        video_url,
        timeout=180,
        stream=True
    )

    video_response.raise_for_status()

    with open(VIDEO_FILE, "wb") as video:
        for chunk in video_response.iter_content(
            chunk_size=1024 * 1024
        ):
            if chunk:
                video.write(chunk)

    print("\nSUCCESS!")
    print("Video saved:", VIDEO_FILE)
    print("File size:", round(VIDEO_FILE.stat().st_size / (1024 * 1024), 2), "MB")

else:
    print("\nUnrecognized task status:", status)
    print("Please share the complete API response.")

