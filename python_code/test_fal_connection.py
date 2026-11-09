
from pathlib import Path
from dotenv import load_dotenv
import os
import fal_client

PROJECT = Path(__file__).resolve().parent.parent
IMAGE = PROJECT / "Output" / "seven_member_beach.png"

load_dotenv(PROJECT / ".env", override=True)

if not os.getenv("FAL_KEY"):
    raise ValueError("FAL_KEY missing.")

if not IMAGE.exists():
    raise FileNotFoundError(f"Image missing: {IMAGE}")

print("Uploading composite image to fal.ai...")

try:
    image_url = fal_client.upload_file(str(IMAGE))

    print("UPLOAD SUCCESSFUL!")
    print("Image URL received from fal.ai.")
    print("API authentication and upload are working.")

except Exception as error:
    print("UPLOAD FAILED:")
    print(type(error).__name__, str(error))
