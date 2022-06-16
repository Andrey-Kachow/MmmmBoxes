import os, base64
from flask import current_app


SIGNATURES_ROOT = os.path.join(current_app.instance_path, 'media', 'signatures')

def is_valid(conn, given_fullname, given_package_title, given_package_id):
    ''' Returns if the given full name, package title and package id
        are consisitent with the database '''

    column = None

    with conn.cursor() as curs:
        curs.execute(
            """
            SELECT fullname, packages.id as package_id, title
            FROM packages
            INNER JOIN users
            ON packages.resident_id = users.id;
            """
        )
        column = curs.fetchone()

    if column is None:
        return False

    return (
        given_fullname == column['fullname'] and
        given_package_title == column['title'] and
        given_package_id == column['package_id']
    )


def img_name(package_id):
    return os.path.join(SIGNATURES_ROOT, f'sig{package_id}.png')


def package_is_signed(pakcage_id):
    return os.path.exist(img_name(package_id))


def mark_package_signed(package_id):
    # TODO: come back here after db migrations including signature representation
    return True


def add_signature(package_id, data_url):
    try:
        captured_img_data = data_url.split(';')[1].split(',')[1]
        with open(img_name(package_id), "wb") as f:
            f.write(base64.decodebytes(captured_img_data))
    except:
        return False
    return True
