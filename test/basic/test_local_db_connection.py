import pytest
import psycopg2
import os

DATABASE_URL = os.environ["DATABASE_URL"]
conn = psycopg2.connect(DATABASE_URL, sslmode="require")


def test_functional():
    with conn.cursor() as curs:
        curs.execute("""DROP TABLE IF EXISTS temp;""")
        conn.commit()
        curs.execute(
            """
        CREATE TABLE temp (
            Name TEXT,
            Age INTEGER
        );"""
        )
        conn.commit()
        curs.execute(
            """
        INSERT INTO temp
        VALUES (\'Bob\', 42);"""
        )
        conn.commit()

        curs.execute("""SELECT * FROM temp;""")
        result = curs.fetchone()

        assert result == ("Bob", 42)
