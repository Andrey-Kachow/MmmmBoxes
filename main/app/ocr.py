from PIL import Image

import pytesseract, re

from main.database.db import get_all_resident_names

MIN_VALUABLE_STR_SIZE = 4

common_keywords = [
    'post', 'postage', 'mail',
    'box', 'package', 'parcel',
    'letter', 'amazon', 'ebay',
    'company', 'envelope', 'urgent'
]


def get_meaningful_lines(read_data):
    ''' Splits the text into lines and removes empty or too short lines '''

    return list(filter(
        lambda line: len(line) >= MIN_VALUABLE_STR_SIZE,
        read_data.split("\n")
    ))


def nice_read_heading(read_data):
    first_line = get_meaningful_lines(read_data)[0]
    lowercase_line = first_line.lower()
    if any([keyword in lowercase_line for keyword in common_keywords]):
        return first_line
    return None


def titled_as_from_whatever(read_data, matched_name):
    ''' Arguments are the text representation of parcel label and
        the already matched name
        Returns the title of the parcel as "From X" '''

    lines = get_meaningful_lines(read_data)
    line_with_from = None
    for line in lines:

        lowercase_line = line.lower()

        if (
            matched_name and
            matched_name.lower() in lowercase_line and
            len(lowercase_line) - len(matched_name) < MIN_VALUABLE_STR_SIZE
        ):
            continue

        if line_with_from:
            return f"From {line}"

        if 'from' in lowercase_line:
            line_with_from = line

    return None


def parse_read_data(conn, read_data):
    ''' Arguments are db connection and a text representation of the image.
        Returns a tuple (name, title) obtained from the OCR data read where
        name  :: is a Name of a package recipient
        title :: is a Package title '''

    existing_names = get_all_resident_names(conn)
    lowercase_data = read_data.lower()

    # Searching any of the existing resident names in the read_data
    matched_name = None
    for name in existing_names:
        if name.lower() in lowercase_data:
            matched_name = name
            break

    # Use the heading of the read_data if it looks like a fine package title
    nice_first_line = nice_read_heading(read_data)
    if (
        nice_first_line and
        matched_name and
        not matched_name.lower() in nice_first_line.lower()
    ):
        return matched_name, nice_first_line

    # Name package a.k. "From Someone"
    matched_package_title = None
    if 'from' in lowercase_data:
        matched_package_title = titled_as_from_whatever(read_data, matched_name)

    return matched_name, matched_package_title
