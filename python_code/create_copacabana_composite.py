
from pathlib import Path
from PIL import Image, ImageOps
from rembg import remove
import io

# ==================================================
# 1. PROJECT PATHS
# ==================================================

PROJECT = Path(__file__).resolve().parent.parent

INPUT = PROJECT / "Input"
OUTPUT = PROJECT / "Output"

OUTPUT.mkdir(parents=True, exist_ok=True)

BEACH = INPUT / "copacabana_beach.jpg"

MEN_PHOTO = INPUT / "group_men.JPG"
COUPLE_PHOTO = INPUT / "couple.jpg"
WOMAN_PHOTO = INPUT / "female.jpg"

FINAL = OUTPUT / "seven_member_copacabana.png"

WIDTH = 1920
HEIGHT = 1080


# ==================================================
# 2. CHECK INPUT FILES
# ==================================================

required_files = [
    BEACH,
    MEN_PHOTO,
    COUPLE_PHOTO,
    WOMAN_PHOTO
]

for file_path in required_files:
    if not file_path.exists():
        raise FileNotFoundError(
            f"Missing input file: {file_path}"
        )


# ==================================================
# 3. LOAD REAL COPACABANA BEACH
# ==================================================

print("Loading Copacabana beach photograph...")

background = Image.open(BEACH).convert("RGB")

background = ImageOps.fit(
    background,
    (WIDTH, HEIGHT),
    method=Image.Resampling.LANCZOS
).convert("RGBA")


# ==================================================
# 4. REMOVE BACKGROUND AND PREPARE PEOPLE
# ==================================================

def prepare_people(photo_path, target_height):

    print(f"Removing background: {photo_path.name}")

    image_bytes = photo_path.read_bytes()

    cutout_bytes = remove(image_bytes)

    person = Image.open(
        io.BytesIO(cutout_bytes)
    ).convert("RGBA")

    # Remove transparent margins
    alpha = person.getchannel("A")
    bbox = alpha.getbbox()

    if bbox is None:
        raise ValueError(
            f"Could not detect people in {photo_path.name}"
        )

    person = person.crop(bbox)

    # Preserve original aspect ratio
    scale = target_height / person.height

    new_width = int(person.width * scale)

    person = person.resize(
        (new_width, target_height),
        Image.Resampling.LANCZOS
    )

    return person


# ==================================================
# 5. PROCESS ALL THREE PHOTOGRAPHS
# ==================================================

# Equal target heights for consistent visual scale.
# Original proportions are preserved.

TARGET_HEIGHT = 600

men_group = prepare_people(
    MEN_PHOTO,
    TARGET_HEIGHT
)

couple_group = prepare_people(
    COUPLE_PHOTO,
    TARGET_HEIGHT
)

single_woman = prepare_people(
    WOMAN_PHOTO,
    TARGET_HEIGHT
)

groups = [
    men_group,
    couple_group,
    single_woman
]


# ==================================================
# 6. FIT GROUPS WITHIN THE IMAGE WIDTH
# ==================================================

GAP = 25
SIDE_MARGIN = 45

total_width = sum(image.width for image in groups)
total_width += GAP * (len(groups) - 1)

available_width = WIDTH - (2 * SIDE_MARGIN)

if total_width > available_width:

    scale = available_width / total_width

    resized_groups = []

    for person in groups:

        new_width = max(1, int(person.width * scale))
        new_height = max(1, int(person.height * scale))

        resized = person.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS
        )

        resized_groups.append(resized)

    groups = resized_groups

    GAP = max(5, int(GAP * scale))


# ==================================================
# 7. POSITION ALL SEVEN PEOPLE
# ==================================================

total_width = sum(image.width for image in groups)
total_width += GAP * (len(groups) - 1)

x_position = (WIDTH - total_width) // 2

BOTTOM_MARGIN = 35

for index, person in enumerate(groups):

    x = x_position
    y = HEIGHT - BOTTOM_MARGIN - person.height

    background.alpha_composite(
        person,
        (x, y)
    )

    print(
        f"Group {index + 1}: "
        f"x={x}, y={y}, "
        f"width={person.width}, "
        f"height={person.height}"
    )

    x_position += person.width + GAP


# ==================================================
# 8. SAVE FINAL IMAGE
# ==================================================

background.convert("RGB").save(
    FINAL,
    quality=95
)

print("\n===================================")
print("SUCCESS: COMPOSITE CREATED")
print("===================================")
print(f"Output: {FINAL}")
print("Resolution: 1920 x 1080")
print("Participants: 7 people")
print("Background: Actual Copacabana beach")
print("===================================")
