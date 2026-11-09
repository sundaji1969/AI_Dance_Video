
import io
import sys
import traceback
from pathlib import Path

from PIL import Image, ImageDraw
from rembg import remove, new_session


# =====================================================
# 1. PROJECT CONFIGURATION
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = BASE_DIR / "Input"
OUTPUT_DIR = BASE_DIR / "Output"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GROUP_FILE = INPUT_DIR / "group_men.JPG"
COUPLE_FILE = INPUT_DIR / "couple.jpg"
FEMALE_FILE = INPUT_DIR / "female.jpg"

OUTPUT_FILE = OUTPUT_DIR / "seven_member_beach.png"

WIDTH = 1920
HEIGHT = 1080


# =====================================================
# 2. LOAD BACKGROUND REMOVAL MODEL
# =====================================================

def load_model():

    print("\nLoading background removal model...")

    session = new_session("u2net")

    print("AI model loaded successfully!")

    return session


# =====================================================
# 3. VERIFY INPUT PHOTOGRAPHS
# =====================================================

def verify_files():

    print("\nChecking original photographs...")

    required_files = [
        GROUP_FILE,
        COUPLE_FILE,
        FEMALE_FILE
    ]

    for file in required_files:

        if not file.exists():

            raise FileNotFoundError(
                f"Photograph not found: {file}"
            )

        print(f"FOUND: {file.name}")

    print("\nAll three photographs verified!")


# =====================================================
# 4. REMOVE BACKGROUND
# =====================================================

def remove_background(image_path, session):

    print(f"\nRemoving background: {image_path.name}")

    # Read photograph as binary bytes
    with open(image_path, "rb") as file:
        input_bytes = file.read()

    # Pass bytes to rembg
    result_bytes = remove(
        input_bytes,
        session=session
    )

    # Convert returned bytes into PIL image
    image = Image.open(
        io.BytesIO(result_bytes)
    ).convert("RGBA")

    # Crop transparent outer margins
    bbox = image.getbbox()

    if bbox is not None:
        image = image.crop(bbox)

    print(
        f"Background removed: "
        f"{image.width} x {image.height}"
    )

    return image


# =====================================================
# 5. CREATE BEACH BACKGROUND
# =====================================================

def create_beach_background():

    print("\nCreating beach background...")

    background = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        (245, 180, 140)
    )

    draw = ImageDraw.Draw(background)

    # Sunset sky
    draw.rectangle(
        (0, 0, WIDTH, 430),
        fill=(247, 164, 145)
    )

    # Sun
    draw.ellipse(
        (1480, 100, 1660, 280),
        fill=(255, 225, 155)
    )

    # Ocean
    draw.rectangle(
        (0, 430, WIDTH, 730),
        fill=(48, 133, 157)
    )

    # Ocean waves
    for y in range(460, 730, 45):

        draw.arc(
            (0, y, WIDTH, y + 55),
            start=0,
            end=180,
            fill=(190, 220, 215),
            width=3
        )

    # Beach sand
    draw.rectangle(
        (0, 730, WIDTH, HEIGHT),
        fill=(229, 195, 150)
    )

    return background.convert("RGBA")


# =====================================================
# 6. RESIZE PEOPLE WITHOUT DISTORTION
# =====================================================

def resize_person(image, max_width, max_height):

    scale = min(
        max_width / image.width,
        max_height / image.height
    )

    new_width = max(1, int(image.width * scale))
    new_height = max(1, int(image.height * scale))

    return image.resize(
        (new_width, new_height),
        Image.Resampling.LANCZOS
    )


# =====================================================
# 7. COMBINE ORIGINAL PHOTOGRAPHS
# =====================================================

def create_composite(session):

    print("\nProcessing original photographs...")

    # Four men
    group = remove_background(
        GROUP_FILE,
        session
    )

    # Couple: one man and one woman
    couple = remove_background(
        COUPLE_FILE,
        session
    )

    # Additional woman
    female = remove_background(
        FEMALE_FILE,
        session
    )

    print("\nPreparing beach background...")

    background = create_beach_background()

    # Resize original photo cutouts
    group = resize_person(
        group,
        1050,
        850
    )

    couple = resize_person(
        couple,
        450,
        800
    )

    female = resize_person(
        female,
        330,
        750
    )

    print("\nArranging seven participants...")

    # Align all source photographs along the bottom
    group_position = (
        0,
        HEIGHT - group.height
    )

    couple_position = (
        1080,
        HEIGHT - couple.height
    )

    female_position = (
        1570,
        HEIGHT - female.height
    )

    # Composite original photographs
    background.alpha_composite(
        group,
        group_position
    )

    background.alpha_composite(
        couple,
        couple_position
    )

    background.alpha_composite(
        female,
        female_position
    )

    # Save output
    print("\nSaving composite image...")

    background.convert("RGB").save(
        OUTPUT_FILE,
        format="PNG"
    )

    if not OUTPUT_FILE.exists():

        raise RuntimeError(
            "Composite image was not saved."
        )

    print("\n===================================")
    print("COMPOSITE CREATED SUCCESSFULLY")
    print("===================================")

    print(f"Output: {OUTPUT_FILE}")
    print(f"Resolution: {WIDTH} x {HEIGHT}")


# =====================================================
# 8. MAIN EXECUTION
# =====================================================

def main():

    print("\n===================================")
    print(" SEVEN MEMBER BEACH COMPOSITE")
    print("===================================")

    try:

        verify_files()

        session = load_model()

        create_composite(session)

    except Exception as error:

        print("\nCOMPOSITE GENERATION FAILED!")

        print(f"\nError: {error}")

        traceback.print_exc()

        sys.exit(1)


# =====================================================
# 9. START PROGRAM
# =====================================================

if __name__ == "__main__":

    main()
