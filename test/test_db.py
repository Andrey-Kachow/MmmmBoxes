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


def with_temp_psql_conn(test_func):

    def wrapper():
        psql = testing.postgresql.Postgresql(port=8765)
        conn = psycopg2.connect(
            **psql.dsn(),
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        # initialise temp db
        execute_sql_file(conn, DB_SCHEMA_PATH)

        # Run the test function
        test_func(conn)

        conn.close()
        psql.stop()

    return wrapper


@with_temp_psql_conn
def test_register_new_user_returns_none_if_successfull(conn):

    name = "Alex Jobson"
    email = "aljobex@gmail.com"
    username = "aljobex"
    password_plain = "_huligancheg324_"
    is_officer = False

    res = register_new_user(conn, name, email, username, password_plain, is_officer)
    assert res is None


@with_temp_psql_conn
def test_register_new_user_same_username_register(conn):

    name = "Alex Jobson"
    email = "aljobex@gmail.com"
    username = "aljobex"
    password_plain = "_huligancheg324_"
    is_officer = False

    register_new_user(conn, name, email, username, password_plain, is_officer)

    email = "somedifferentemail@gmail.com"

    res = register_new_user(conn, name, email, username, password_plain, is_officer)
    assert res == "Username is taken!"


@with_temp_psql_conn
def test_register_new_user_same_email_register(conn):

    name = "Alex Jobson"
    email = "aljobex@gmail.com"
    username = "aljobex"
    password_plain = "_huligancheg324_"
    is_officer = False

    register_new_user(conn, name, email, username, password_plain, is_officer)

    usename = "somedifferentusername"

    res = register_new_user(conn, name, email, username, password_plain, is_officer)
    assert res == "Email is taken!"
