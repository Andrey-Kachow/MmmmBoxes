from PIL import Image

import pytesseract, re, tempfile, os
from werkzeug.utils import secure_filename

from main.database.db import get_all_resident_names

MIN_VALUABLE_STR_SIZE = 4

common_keywords = [
    "post",
    "postage",
    "mail",
    "box",
    "package",
    "parcel",
    "letter",
    "amazon",
    "ebay",
    "company",
    "envelope",
    "urgent",
]


def get_meaningful_lines(read_data):
    """Splits the text into lines and removes empty or too short lines"""

    return list(
        filter(lambda line: len(line) >= MIN_VALUABLE_STR_SIZE, read_data.split("\n"))
    )


def nice_read_heading(read_data):
    try:
        first_line = get_meaningful_lines(read_data)[0]
        lowercase_line = first_line.lower()
        if any([keyword in lowercase_line for keyword in common_keywords]):
            return first_line
    except Exception as e:
        pass
    return None


def titled_as_from_whatever(read_data, matched_name):
    '''Arguments are the text representation of parcel label and
    the already matched name
    Returns the title of the parcel as "From X"'''

    lines = get_meaningful_lines(read_data)
    line_with_from = None
    for line in lines:

        lowercase_line = line.lower()

        if (
            matched_name
            and matched_name.lower() in lowercase_line
            and len(lowercase_line) - len(matched_name) < MIN_VALUABLE_STR_SIZE
        ):
            continue

        if line_with_from:
            return f"From {line}"

        if "from" in lowercase_line:
            line_with_from = line

    return None


def parse_read_data(conn, read_data):
    """Arguments are db connection and a text representation of the image.
    Returns a tuple (name, title) obtained from the OCR data read where
    name  :: is a Name of a package recipient
    title :: is a Package title"""

    existing_names = get_all_resident_names(conn)
    lowercase_data = read_data.lower()

    # Searching any of the existing resident names in the read_data
    matched_name = None
    for name in existing_names:
        if name.lower() in lowercase_data:
            matched_name = name
            break

    # Try to find a line which says has a substring "ref"
    for line in read_data.split("\n"):
        if "ref" in line.lower():
            return matched_name, line

    # Otherwise, find the line which has the longest word. +[""] is there to make sure l.split() is non-empty.
    reference = max(
        read_data.split("\n"), key=lambda l: max(len(w) for w in l.split() + [""])
    )

    return matched_name, reference


def get_package_details_from_file(ocr_file, conn):

    if "TESSDATA_PREFIX" in os.environ:
        pytesseract.pytesseract.tesseract_cmd = "/app/.apt/usr/bin/tesseract"
    elif "PYTESSERACT_PATH" in os.environ:
        pytesseract.pytesseract.tesseract_cmd = os.environ["PYTESSERACT_PATH"]

    with tempfile.TemporaryDirectory() as dirname:

        ocr_img_path = os.path.join(dirname, secure_filename(ocr_file.filename))
        ocr_file.save(ocr_img_path)

        # Open image, rescale largest dimension to be 1000px.
        im = Image.open(ocr_img_path)
        max_px = max(im.size[0], im.size[1])
        scale_factor = 1000 / max_px
        im.thumbnail((im.size[0] * max_px, im.size[1] * max_px))

        read_data = pytesseract.image_to_string(Image.open(ocr_img_path))

        matched_name, matched_package_title = parse_read_data(conn, read_data)

    return matched_name, matched_package_title
