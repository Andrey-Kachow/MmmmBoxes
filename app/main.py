import os, psycopg2
from flask import Flask

app = Flask(__name__)

# Connect to DB
DATABASE_URL = os.environ["DATABASE_URL"]
conn = psycopg2.connect(DATABASE_URL, sslmode="require")

@app.route("/")
def index():
    return f"""<h1>{conn} Hello world!</h1>{db_test()}"""

# DB test
def db_test():
    curs = conn.cursor()

    curs.execute("""DROP TABLE IF EXISTS test;""")
    try:
        print(curs.fetchall())
    except psycopg2.ProgrammingError:
        print("Cursor no results")
    conn.commit()

    curs.execute("""
    CREATE TABLE test (
        TestField INTEGER,
        TestField1 TEXT
    );""")
    try:
        print(curs.fetchall())
    except psycopg2.ProgrammingError:
        print("Cursor no results")
    conn.commit()

    curs.execute("""
    INSERT INTO test (TestField, TestField1)
    VALUES (12, \'Hello!\');""")
    try:
        print(curs.fetchall())
    except psycopg2.ProgrammingError:
        print("Cursor no results")
    conn.commit()

    curs.execute("""
    SELECT * FROM test;""")
    result = curs.fetchall()

    return result


if __name__ == "__main__":
    app.debug = True
    app.run()