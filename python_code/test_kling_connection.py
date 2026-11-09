
from pathlib import Path
from dotenv import load_dotenv
import os

PROJECT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT / ".env", override=True)

api_key = os.getenv("KLING_API_KEY", "").strip()

if not api_key:
    print("ERROR: Kling API key not found.")
else:
    print("SUCCESS: Kling API key found.")
    print("Key length:", len(api_key))
    print("Key format:", "Valid-looking API key" if api_key.startswith("api-key-kling-") else "Please check key format")
