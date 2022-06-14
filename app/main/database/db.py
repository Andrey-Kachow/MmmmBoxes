import psycopg2, json, os, string, psycopg2.extras
from werkzeug.security import check_password_hash, generate_password_hash


def initialise_db_connection():
    """
    Returns: a psycopg2 database connection.

    If local_db.json is found, returns a connection with local postgres database
    Otherwise, attempts to connect to URL given by DATABASE_URL environment variable."""

    # Attempt to get creds
    user_creds = None
    try:
        with open(os.path.join(os.path.dirname(__file__),"local_db.json")) as f:
            user_creds = json.loads(f.read())
            # Check that the relevant keys are in creds.json.
            if not all(cred_key in user_creds for cred_key in ["host", "dbname", "user" ,"password"]):
                print("Credentials are incomplete. Using DATABASE_URL variable.")
                user_creds = None

    except FileNotFoundError as e:
        print("Credentials were not found in database/ ! Using DATABASE_URL variable.")
        user_creds = None

    # Return a connection with user creds or DATABASE_URL, depending on existence of user_creds
    if user_creds is None:
        return psycopg2.connect(
                os.environ["DATABASE_URL"],
                sslmode="require",
                cursor_factory=psycopg2.extras.RealDictCursor
            )
    return psycopg2.connect(
            host=user_creds["host"],
            database=user_creds["dbname"],
            user=user_creds["user"],
            password=user_creds["password"],
            cursor_factory=psycopg2.extras.RealDictCursor
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
    Returns None if registration successful, String describing failure reason otherwise.
    """
    with conn.cursor() as curs:
        # Check if username is taken
        curs.execute(
            """
            SELECT id
            FROM users
            WHERE username=%s;
            """,
            (username, )
        )
        if curs.fetchone() is not None:
            return "Username is taken!"

        # Check if username is taken
        curs.execute(
            """
            SELECT id
            FROM users
            WHERE email=%s;
            """,
            (email, )
        )
        if curs.fetchone() is not None:
            return "Email is taken!"

        curs.execute(
            """
            INSERT INTO users (username, password, email, fullname, is_officer)
            VALUES (%s, %s, %s, %s, %s);
            """,
            (username, generate_password_hash(password_plain), email, name, is_officer)
        )
    conn.commit()
    return None

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
        # Check password
        if not check_password_hash(result.pop("password"), password_plain):
            return {}

        return dict(result)

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

        return result


def get_all_packages(conn, id=None):
    """Arguments: a database connection, Optional: id of user whose packages to get
    Returns: a list of every package in the system. Packages are dicts:
        - id
        - title
        - delivered
        - collected
        - fullname (of resident)
        - resident_id
        - email (of resident)
    """
    with conn.cursor() as curs:
        if id is None:
            curs.execute(
                """
                SELECT packages.id, packages.title, packages.delivered, packages.collected, users.fullname, users.id as resident_id, users.email
                FROM packages
                INNER JOIN users
                ON packages.resident_id = users.id;
                """
            )
        else:
            curs.execute(
                """
                SELECT packages.id, packages.title, packages.delivered, packages.collected, users.fullname, users.id as resident_id, users.email
                FROM packages
                INNER JOIN users
                ON packages.resident_id = users.id AND users.id=%s;
                """,
                (id,)
            )

        return [clean_package_dict(dict(p)) for p in curs.fetchall()]

def add_new_package(conn, resident_name, title):
    """Arguments: a database connection, recipient's name, package title
    Returns: A dict of the package added (BROADCAST THIS), or None if failed for some reason.
        - id
        - title
        - delivered
        - collected
        - fullname (of resident)
        - resident_id
        - email (of resident)"""
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
        result = curs.fetchone()
        # Resident does not exist
        if result is None:
            return None

        rid = result["id"]

        print(f"\n{rid}\n\n{title}\n")

        curs.execute(
            """
            INSERT INTO packages (resident_id, title)
            VALUES (%s, %s)
            RETURNING id;
            """,
            (result["id"], title)
        )
        # Get the id, proceed to look up the rest of the details
        package_id = curs.fetchone()["id"]
        curs.execute(
            """
            SELECT packages.id, packages.title, packages.delivered, packages.collected, users.fullname, users.id as resident_id, users.email
            FROM packages
            INNER JOIN users
            ON packages.resident_id = users.id
            WHERE packages.id = %s;
            """,
            (package_id,)
        )
        conn.commit()
        return clean_package_dict(dict(curs.fetchone()))


def get_all_resident_names(conn):
    with conn.cursor() as curs:
        curs.execute(
            """
            SELECT fullname
            FROM users
            WHERE is_officer = false
            """
        )
        return map(
            lambda real_dict: real_dict['fullname'],
            curs.fetchall()
        )
    return []


def clean_package_dict(pack_dict):
    """Arguments: package in dictionary form
    Returns: cleaned dictionary
    Converts timestamps to RFC3339 and assigns default values to Nones."""

    pack_dict["delivered"] = pack_dict["delivered"].isoformat()

    if pack_dict["collected"] is not None:
        pack_dict["collected"] = pack_dict["collected"].isoformat()
    else:
        pack_dict["collected"] = "Collection pending"

    return pack_dict
