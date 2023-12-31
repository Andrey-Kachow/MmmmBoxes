import os
import base64
from flask import current_app

# !!!TODO: Replace txt saved representation of imageData as actual image

SIGNATURES_ROOT = None


def is_valid(conn, given_fullname, given_package_title, given_package_id):
    """Returns if the given full name, package title and package id
    are consisitent with the database"""

    column = None

    with conn.cursor() as curs:
        curs.execute(
            """
            SELECT fullname, packages.id as package_id, title
            FROM packages
            INNER JOIN users
            ON packages.resident_id = users.id
            WHERE packages.id = %s;
            """,
            (given_package_id,),
        )
        column = curs.fetchone()

    if column is None:
        return False

    return (
        given_fullname == column["fullname"]
        and given_package_title == column["title"]
        and given_package_id == column["package_id"]
    )


def img_name(package_id):
    if SIGNATURES_ROOT is None:
        return os.path.join(
            current_app.instance_path, "media", "signatures", f"sig{package_id}.txt"
        )
    return os.path.join(SIGNATURES_ROOT, f"sig{package_id}.txt")


def package_is_signed(package_id):
    return os.path.exists(img_name(package_id))


def mark_package_signed(conn, package_id):
    # TODO: come back here after db migrations including signature representation
    return True


def add_signature(package_id, data_url):
    try:
        with open(img_name(package_id), "w") as f:
            f.write(data_url)
        # captured_img_data = data_url.split(';')[1].split(',')[1]
        # with open(img_name(package_id), "wb") as f:
        #     f.write(base64.decodebytes(captured_img_data))
    except:
        return False
    return True


def get_data_url(package_id):
    with open(img_name(package_id)) as f:
        return f.read()


def delete_signature(package_id):
    """Removes the img file from signatures root.
    Return True if the operation was successfull"""

    if not os.path.exists(img_name(package_id)):
        return False
    try:
        os.remove(img_name(package_id))
    except Exception as e:
        return False
    return True
