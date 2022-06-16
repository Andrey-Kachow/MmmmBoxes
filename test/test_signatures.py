import tempfile, os

sys.path.append('..')

import drp11.app.main.database.db as tdb

from drp11.app.main.database.signatures import (
    is_valid,
    img_name,
    package_is_signed,
    add_signature,
)

AMONGUS_DATA_URL = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCA'
'YAAABzenr0AAAAAXNSR0IArs4c6QAAAnhJREFUWIXFlzGL1EAUx38v'
'5LKFpY2dXOEnsBDvG3igjd/A3CILuoKl2toKeoWsa0DxG6zgCfYLJy'
'xnf8XCdTaWKjGXZ5FJTLKZZJI98EEyyezMvP/7z3/e20g4V+U/mr/N'
'5GgsxXM4HxbHIABlxzcFVlrt6wPIG+o8DXzSkc9yZ4ffgZ+9m6sO8s'
'IAxD9/AKAjQ5xCOU4xVxr4/Ap8JxC9AHx4dJk08KnKVitP+dvItF0g'
'nDXwbjJq6BW8+I/rEtsBOE9iVrW+3Pnr5WkGR8jYkWwr8i2a7GUsNA'
'mz/ymQbGEvTtg/mKLlLVA4uLG7OWF5ymTvWuNyThp4/+BS4Tu/l/EU'
'fQJvj9e1EYqYjiY9WBmoD14BKVBWoKoiwPezNVeu7mbvAvOv64x7wx'
'bA7fuP+Th74QYgGgsz32PsZQR5cZK1RbRV5R9/WQBwJ5xWToggLKKX'
'tKUkKwO587Jp+R74SHTIrfBhQfkiemV1dBQdugGIxsJdEU5M1BsmYh'
'xqZeH9cFr0ZRwJYiSaj3E+BU/aCqT+032edr044VNL9G02uBqKCGqA'
'6qieHavmxYm1OPVKxWIcF5suYog2/QOsFwMKRdQVSSqVhNTHepfjXJ'
'yFu2GBDwewYTkSU4v74hkEoHJE8yxsanF9I6zHeSiAPMKTOOFbnBQp'
'V9mMvss5WET4FHhumVBO8eropM02GAjnyueOSW1676sB6zG83uJAHc'
'atOn5vBVDPWuXS3HXa6/+aAMI359bxziI8Mm0TxeFcC9CNWyB2N04A'
'xPN4Zp67GCinBRdzAnBvZqewC0iX9aoFXYJyHVM2Gfp1rGmCeFt92w'
'Jb1IKLcA7wF33s38CnTVLNAAAAAElFTkSuQmCC'

name = "Alex Jobson"
email = "aljobex@gmail.com"
username = "aljobex"
password_plain = "_huligancheg324_"
is_officer = False
package_title = "HP printer"

def with_temp_directory(test_func):

    def wrapper():
        with tempfile.TemporaryDirectory() as dirname:
            _temp = tdb.SIGNATURES_ROOT
            tdb.SIGNATURES_ROOT = dirname

            test_func(dirname)

            tdb.SIGNATURES_ROOT = _temp

    return wrapper


@tdb.with_temp_psql_conn
def test_package_is_valid_if_exists(conn):

    tdb.register_new_user(conn, name, email, username, password_plain, is_officer)
    tdb.add_new_package(conn, name, package_title)

    assert is_valid(conn, name, package_title, 1)
    assert not is_valid(conn, name, package_title, 2)


@with_temp_directory
def test_img_name_for_sanity(dirname):
    for package_id in range(100):
        assert os.path.join(dirname, f'sig{package_id}.png') == img_name(package_id)
