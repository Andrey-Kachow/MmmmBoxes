import psycopg2
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from db import initialise_db_connection, execute_sql_file


def migrate(migration_file, url=None):
    if not url:
        conn = initialise_db_connection(True)
    else:
        conn = psycopg2.connect(url, sslmode="require")

    execute_sql_file(conn, os.path.join('migrations', migration_file))


migrate(sys.argv[1], sys.argv[2])
