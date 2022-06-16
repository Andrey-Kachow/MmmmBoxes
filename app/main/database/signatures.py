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


def add_signature(conn, package_id, data_url):
    # TODO: implement
    return False
