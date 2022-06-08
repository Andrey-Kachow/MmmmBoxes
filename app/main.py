import os, psycopg2
from flask import Flask

app = Flask(__name__)
DATABASE_URL = os.environ["DATABASE_URL"]

@app.route("/")
def index():
    return "<h1>Hello world!</h1>"



if __name__ == "__main__":
    # connect to postgresSQL db
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    with conn.cursor() as curs:
        curs.execute("""
        CREATE TABLE test (
            TestField int,
            TestField1 varchar(255)
        );
        """)

        curs.execute("""
        INSERT INTO test (TestField, TestField1)
        VALUES(1, \'hello world\')
        """)

    app.debug = True
    app.run()