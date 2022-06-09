import psycopg2, json, os
import psycopg2.extras

import click
from flask import current_app, g
from flask.cli import with_appcontext


def init_heroku_db_creds():
    try:
        with open(os.path.join('flaskr', 'creds.json')) as f:
            return json.loads(f.read())
    except Exception as e:
        print("Credentials were not found!")
        return None


HEROKU_CREDS = init_heroku_db_creds();


def get_db_connection():
    if 'conn' not in g:
        if HEROKU_CREDS is None:
            # Not the best code
            g.conn = psycopg2.connect(
                current_app.config['DATABASE_URL'],
                sslmode="require")
        else:
            g.conn = psycopg2.connect(
                host=HEROKU_CREDS['host'],
                database=HEROKU_CREDS['database'],
                user=HEROKU_CREDS['user'],
                password=HEROKU_CREDS['password']
            )
    return g.conn


def get_db_cursor(conn=None):
    if conn is None:
        conn = get_db_connection()
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def close_db_connection(e=None):
    conn = g.pop('conn', None)

    if conn is not None:
        conn.close()


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    with current_app.open_resource('schema.sql') as f:
        cur.execute(f.read().decode('utf8'))
    conn.commit()
    cur.close()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db_connection)
    app.cli.add_command(init_db_command)
