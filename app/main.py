import os, psycopg2
from flask import Flask

app = Flask(__name__)

# Connect to DB
DATABASE_URL = os.environ["DATABASE_URL"]
conn = psycopg2.connect(DATABASE_URL, sslmode="require")

@app.route("/")
def index():
    return f"""<h1>{conn} Hello world!</h1>{db_dump()}"""

# Dump entire 'test' table
def db_dump():
    with conn.cursor() as curs:
        curs.execute("""
        SELECT * FROM test;
        """)
        return curs.fetchall()


if __name__ == "__main__":
    with conn.cursor() as curs:
        curs.execute("""
        CREATE TABLE test (
            TestField int,
            TestField1 varchar(255)
        );
        """)

        curs.execute("""
        INSERT INTO test (TestField, TestField1)
        VALUES(1, \'hello world\');
        """)
    conn.commit()

    app.debug = True
    app.run()