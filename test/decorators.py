import testing.postgresql
import psycopg2
import tempfile
import main.database.signatures as sig
import main.database.db as db
import os


DB_SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "main", "database", "schema.sql"
)
DROP_DB_PATH = os.path.join(
    os.path.dirname(__file__), "..", "main", "database", "drop_all.sql"
)


def with_temp_psql_conn(test_func):
    def wrapper(*args):
        psql = testing.postgresql.Postgresql(port=8765)
        conn = psycopg2.connect(
            **psql.dsn(), cursor_factory=psycopg2.extras.RealDictCursor
        )
        # initialise temp db
        db.execute_sql_file(conn, DROP_DB_PATH)
        db.execute_sql_file(conn, DB_SCHEMA_PATH)

        args += (conn,)
        test_func(*args)

        conn.close()
        psql.stop()

    return wrapper


def with_temp_directory(test_func):
    def wrapper(*args):
        with tempfile.TemporaryDirectory() as dirname:
            _temp = sig.SIGNATURES_ROOT
            sig.SIGNATURES_ROOT = dirname
            args += (dirname,)
            test_func(*args)
            sig.SIGNATURES_ROOT = _temp

    return wrapper
