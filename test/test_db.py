import testing.postgresql
import psycopg2
import os, sys

sys.path.append('..')

from drp11.app.main.database.db import (
    execute_sql_file,
    register_new_user,
    verify_password,
    get_user_by_id,
    get_all_packages,
    add_new_package,
)


DB_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '..', 'app', 'main', 'database', 'schema.sql')
DROP_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'app', 'main', 'database', 'drop_all.sql')

name = "Alex Jobson"
email = "aljobex@gmail.com"
username = "aljobex"
password_plain = "_huligancheg324_"
is_officer = False

of_name = "Patrick Bateman"
of_email = "patbat@gmail.com"
of_username = "patbat"
of_password_plain = "solo322$"
of_is_officer = True

def with_temp_psql_conn(test_func):

    def wrapper():
        psql = testing.postgresql.Postgresql(port=8765)
        conn = psycopg2.connect(
            **psql.dsn(),
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        # initialise temp db
        execute_sql_file(conn, DROP_DB_PATH)
        execute_sql_file(conn, DB_SCHEMA_PATH)

        test_func(conn)

        conn.close()
        psql.stop()

    return wrapper


@with_temp_psql_conn
def test_register_new_user_returns_none_if_successfull(conn):
    res = register_new_user(conn, name, email, username, password_plain, is_officer)
    assert res is None


@with_temp_psql_conn
def test_register_new_user_same_username_register(conn):

    register_new_user(conn, name, email, username, password_plain, is_officer)
    _email = "somedifferentemail@gmail.com"

    res = register_new_user(conn, name, _email, username, password_plain, is_officer)
    assert res == "Username is taken!"


@with_temp_psql_conn
def test_register_new_user_same_email_register(conn):
    global username

    register_new_user(conn, name, email, username, password_plain, is_officer)
    _username = "somedifferentusername"

    res = register_new_user(conn, name, email, _username, password_plain, is_officer)
    assert res == "Email is taken!"


@with_temp_psql_conn
def test_verify_password_returns_proper_dict_when_success(conn):

    register_new_user(conn, name, email, username, password_plain, is_officer)

    res = verify_password(conn, username, password_plain)
    assert bool(res)
    for key in ['id', 'username', 'email', 'fullname', 'is_officer']:
        assert key in res.keys()


@with_temp_psql_conn
def test_verify_password_returns_empty_dict_when_no_such_user(conn):

    register_new_user(conn, name, email, username, password_plain, is_officer)

    res = verify_password(conn, "never_existed_user", password_plain)
    assert not bool(res)


@with_temp_psql_conn
def test_verify_password_returns_empty_dict_when_incorrect_password(conn):

    register_new_user(conn, name, email, username, password_plain, is_officer)

    res = verify_password(conn, username, "incorrect_password")
    assert not bool(res)


@with_temp_psql_conn
def test_get_user_by_id_returns_empty_dict_when_incorrect_id(conn):

    register_new_user(conn, name, email, username, password_plain, is_officer)

    res = get_user_by_id(conn, 42069)
    assert not bool(res)


@with_temp_psql_conn
def test_get_user_by_id_returns_user_dict_when_correct_id(conn):

    register_new_user(conn, name, email, username, password_plain, is_officer)

    res = get_user_by_id(conn, 1)
    assert bool(res)
    for key in ['id', 'username', 'email', 'fullname', 'is_officer']:
        assert key in res.keys()


@with_temp_psql_conn
def test_add_new_package_returns_user_dict_when_correct_id(conn):

    register_new_user(conn, name, email, username, password_plain, is_officer)

    res = add_new_package(conn, name, "HP printer")
    assert bool(res)
    for key in ['id', 'title', 'email', 'fullname', 'delivered', 'collected', 'resident_id']:
        assert key in res.keys()

@with_temp_psql_conn
def test_add_new_package_cannot_add_officer_package(conn):

    register_new_user(conn, of_name, of_email, of_username, of_password_plain, of_is_officer)

    res = add_new_package(conn, of_name, "HP printer")
    assert res is None


@with_temp_psql_conn
def test_add_new_package_cannot_package_if_no_such_user_in_db(conn):

    register_new_user(conn, name, email, username, password_plain, is_officer)

    res = add_new_package(conn, "No Such Name", "HP printer")
    assert res is None


@with_temp_psql_conn
def test_get_all_packages_returns_empty_if_nothing_added(conn):

    register_new_user(conn, name, email, username, password_plain, is_officer)

    res = get_all_packages(conn)
    assert not bool(res)


@with_temp_psql_conn
def test_get_all_packages_items_are_added(conn):

    register_new_user(conn, name, email, username, password_plain, is_officer)

    # Observing the item count in the packages table
    res = []
    count = 0
    for package in ["HP printer", "AAAA bateries", "Paint Bruches", "Cool Shirt"]:
        add_new_package(conn, name, package)
        count += 1
        res = get_all_packages(conn)
        assert len(res) == count

    # Checking that all dictionaries have appropriate format and the dictionaries are not empty
    for package_dict in res:
        assert bool(package_dict)
        for key in ['id', 'title', 'email', 'fullname', 'delivered', 'collected', 'resident_id']:
            assert key in package_dict.keys()
