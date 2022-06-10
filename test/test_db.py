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

name = "Alex Jobson"
email = "aljobex@gmail.com"
username = "aljobex"
password_plain = "_huligancheg324_"
is_officer = False

def with_temp_psql_conn(test_func):

    def wrapper():
        psql = testing.postgresql.Postgresql(port=8765)
        conn = psycopg2.connect(
            **psql.dsn(),
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        # initialise temp db
        execute_sql_file(conn, DB_SCHEMA_PATH)

        try:
            # Run the test function
            test_func(conn)
        except AssertionError as e:
            pass
        finally:
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
    email = "somedifferentemail@gmail.com"

    res = register_new_user(conn, name, email, username, password_plain, is_officer)
    assert res == "Username is taken!"


@with_temp_psql_conn
def test_register_new_user_same_email_register(conn):

    register_new_user(conn, name, email, username, password_plain, is_officer)
    username = "somedifferentusername"

    res = register_new_user(conn, name, email, username, password_plain, is_officer)
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
