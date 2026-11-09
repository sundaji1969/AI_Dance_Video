
from pathlib import Path
import base64

PROJECT = Path(__file__).resolve().parent.parent

IMAGE = PROJECT / "Output" / "seven_member_copacabana.png"

OUTPUT = PROJECT / "generated_clips" / "kling_image_base64.txt"

if not IMAGE.exists():
    raise FileNotFoundError(f"Image not found: {IMAGE}")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

image_bytes = IMAGE.read_bytes()

encoded_image = base64.b64encode(
    image_bytes
).decode("utf-8")

OUTPUT.write_text(encoded_image, encoding="utf-8")

print("SUCCESS: Kling image prepared")
print("Image size:", len(image_bytes), "bytes")
print("Base64 file:", OUTPUT)
