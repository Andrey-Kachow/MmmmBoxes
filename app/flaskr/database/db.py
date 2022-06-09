import psycopg2, json, os, string
from werkzeug.security import check_password_hash, generate_password_hash


def initialise_db_connection():
    """
    Returns: a psycopg2 database connection.

    If local_db.json is found, returns a connection with local postgres database
    If creds.json is found, returns a connection with those credentials.
    Otherwise, attempts to connect to URL given by DATABASE_URL environment variable."""

    try:
        with open(os.path.join(os.path.dirname(__file__),"local_db.json")) as f:
            conn_details = json.loads(f.read())
            return psycopg2.connect(
                    host=conn_details["host"],
                    dbname=conn_details["dbname"],
                    user=conn_details["user"],
                    password=conn_details["password"]
                )
    except FileNotFoundError as e:
        print("Local postgress database is not going to be used. Looking for credentials...")

    # Attempt to get creds
    user_creds = None
    try:
        with open(os.path.join(os.path.dirname(__file__),"creds.json")) as f:
            user_creds = json.loads(f.read())
            # Check that the relevant keys are in creds.json.
            if not all(cred_key in user_creds for cred_key in ["host", "database", "user" ,"password"]):
                print("Credentials are incomplete. Using DATABASE_URL variable.")
                user_creds = None

    except FileNotFoundError as e:
        print("Credentials were not found in database/ ! Using DATABASE_URL variable.")
        user_creds = None

    # Return a connection with user creds or DATABASE_URL, depending on existence of user_creds
    if user_creds is None:
        return psycopg2.connect(
            os.environ["DATABASE_URL"],
            sslmode="require")

    return psycopg2.connect(
            host=user_creds["host"],
            dbname=user_creds["database"],
            user=user_creds["user"],
            password=user_creds["password"]
        )


def execute_sql_file(conn, filename):
    """Arguments: a database connection, sql file in same directory as db.
    Executes the file."""
    sql_cmd = None
    try:
        with open(os.path.join(os.path.dirname(__file__), filename)) as f:
            sql_cmd = f.read()
    except FileNotFoundError as e:
        print(f"{filename} not found in database/ !")
        return

    with conn.cursor() as curs:
        curs.execute(sql_cmd)
    conn.commit()


def register_new_user(conn, name, email, username, password_plain, is_officer):
    """Arguments: a database connection, user info (name, email, username, password_plain, is_officer)
    Adds a new user to the database.
    Returns True if registration successful, False otherwise.
    """
    with conn.cursor() as curs:
        # Check if username/email is taken
        curs.execute(
            """
            SELECT id
            FROM users
            WHERE username=%s OR email=%s;
            """,
            (username, email)
        )
        if curs.fetchone() is not None:
            return False

        curs.execute(
            """
            INSERT INTO users (username, password, email, fullname, is_officer)
            VALUES (%s, %s, %s, %s, %s);
            """,
            (username, generate_password_hash(password_plain), email, name, is_officer)
        )
    conn.commit()
    return True

def verify_password(conn, username, password_plain):
    """Arguments: a database connection, details to check.
    Returns: a dict containing:
        - id,
        - username,
        - email,
        - fullname,
        - is_officer
        if the login information is correct. If not, the dict is empty.
    """
    with conn.cursor() as curs:
        # Fetch details, check password. Do not give reason for failed login - this is a security issue.
        curs.execute(
            """
            SELECT password, id, username, email, fullname, is_officer
            FROM users
            WHERE username=%s;
            """,
            (username,)
        )
        result = curs.fetchone()
        if result is None:
            return {}

        expected_hash, id, username, email, fullname, is_officer = result
        # Check password
        if not check_password_hash(expected_hash, password_plain):
            return {}

        return {
            "id": id,
            "username": username,
            "email": email,
            "fullname": fullname,
            "is_officer": is_officer
        }

def get_user_by_id(conn, id):
    """Arguments: a database connection, user id to get.
    Returns: a dict containing:
        - id,
        - username,
        - email,
        - fullname,
        - is_officer
        If id does not exist, returns empty dict.
    """
    with conn.cursor() as curs:
        curs.execute(
            """
            SELECT id, username, email, fullname, is_officer
            FROM users
            WHERE id=%s;
            """,
            (id,)
        )
        result = curs.fetchone()
        if result is None:
            return {}

        id, username, email, fullname, is_officer = result

        return {
            "id": id,
            "username": username,
            "email": email,
            "fullname": fullname,
            "is_officer": is_officer
        }


def get_all_packages(conn, id=None):
    """Arguments: a database connection, Optional: id of user whose packages to get
    Returns: a list of every package in the system. Packages are dicts:
        - id
        - resident_id
        - delivered
        - collected
        - title
    """
    with conn.cursor() as curs:
        if id is None:
            curs.execute(
                """
                SELECT id, resident_id, delivered, collected, title
                FROM packages;
                """
            )
        else:
            curs.execute(
                """
                SELECT id, resident_id, delivered, collected, title
                FROM packages
                WHERE resident_id=%s;
                """,
                (id,)
            )
        packages = curs.fetchall()
        return [
            {"id": id, "resident_id": rid, "delivered": deli, "collected": coll, "title": title}
            for (id, rid, deli, coll, title) in packages
        ]

def add_new_package(conn, resident_name, title):
    """Arguments: a database connection, recipient's name, package title
    Returns: True if package successfully added to system, false otherwise."""
    with conn.cursor() as curs:
        # Try to find this resident's id
        curs.execute(
            """
            SELECT id
            FROM users
            WHERE fullname=%s AND is_officer=FALSE;
            """,
            (resident_name,)
        )
        rid = curs.fetchone()
        # Resident does not exist
        if rid is None:
            return False

        curs.execute(
            """
            INSERT INTO packages (resident_id, title)
            VALUES (%s, %s)
            """,
            (rid, title)
        )
    conn.commit()
    return True
