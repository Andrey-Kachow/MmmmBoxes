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
    print(curs.fetchall())

    curs.execute("""
    CREATE TABLE test (
        TestField INTEGER,
        TestField1 TEXT
    );""")
    print(curs.fetchall())

    curs.execute("""
    INSERT INTO test (TestField, TestField1)
    VALUES (12, \'Hello!\');""")
    print(curs.fetchall())

    curs.execute("""
    SELECT * FROM test;""")
    result = cursor.fetchall()

    return result


if __name__ == "__main__":
    app.debug = True
    app.run()