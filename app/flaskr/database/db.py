import psycopg2, json, os, string
from werkzeug.security import check_password_hash, generate_password_hash


def initialise_db_connection():
    """
    Returns: a psycopg2 database connection.

    If creds.json is found, returns a connection with those credentials.
    Otherwise, attempts to connect to URL given by DATABASE_URL environment variable."""
    # Attempt to get creds
    user_creds = None
    try:
        with open(os.path.join(os.path.dirname(__file__),"creds.json")) as f:
            user_creds = json.loads(f.read())
            # Check that the relevant keys are in creds.json.
            if all(cred_key in user_creds for cred_key in ["host", "database", "user" ,"password"]):
                pass
            else:
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
    else:
        return psycopg2.connect(
                host=user_creds["host"],
                database=user_creds["database"],
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


def sanitise_input(unsafe_str,
                allowed=string.ascii_letters + string.digits + string.whitespace + ".@"):
    """Arguments: string to be sanitised. Optional: allowed characters
    Returns: sanitised string
    Removes all characters except ascii letters, numbers, whitespace, dots and @."""
    return "".join(c for c in unsafe_str if c in allowed)

def add_new_resident(conn, name, email, username, password_plain):
    """Arguments: a database connection, resident info (name, email, username, password_plain)
    Adds a new resident to the database.
    """
    q_username = f"'{sanitise_input(username)}'"
    q_hashed = f"'{generate_password_hash(password_plain)}'"
    q_email = f"'{sanitise_input(email)}'"
    q_name = f"'{sanitise_input(name)}'"
    with conn.cursor() as curs:
        curs.execute(
            "INSERT INTO resident (username, password, email, fullname) "
            f"VALUES ({q_username}, {q_hashed}, {q_email}, {q_name});"
        )
    conn.commit()

def add_new_officer(conn, name, email, username, password_plain):
    """Arguments: a database connection, officer info (name, email, username, password_plain)
    Adds a new officer to the database.
    """
    q_username = f"'{sanitise_input(username)}'"
    q_hashed = f"'{generate_password_hash(password_plain)}'"
    q_email = f"'{sanitise_input(email)}'"
    q_name = f"'{sanitise_input(name)}'"
    with conn.cursor() as curs:
        curs.execute(
            "INSERT INTO officer (username, password, email, fullname) "
            f"VALUES ({q_username}, {q_hashed}, {q_email}, {q_name});"
        )
    conn.commit()

def verify_password_resident(conn, username, password_plain):
    """Arguments: a database connection, details to check.
    Returns: a dict containing:
        - user_id
        - user_fullname
        - username
        - user_role
        If the login information is correct. If not, the dict is empty.
    """
    with conn.cursor() as curs:
        # Fetch details, check password. Do not give reason for failed login - this is a security issue.
        q_username = f"'{sanitise_input(username)}'"
        curs.execute(f"SELECT password, id, fullname, username FROM resident WHERE username={q_username};")
        result = curs.fetchone()
        if result is None:
            return {}

        expected_hash, user_id, user_fullname, username = result
        # Check password
        if not check_password_hash(expected_hash, password_plain):
            return {}

        return {
            "user_id": user_id,
            "user_fullname": user_fullname,
            "username": username,
            "user_role": "resident"
        }


def verify_password_officer(conn, username, password_plain):
    """Arguments: a database connection, details to check.
    Returns: a dict containing:
        - user_id
        - user_fullname
        - username
        - user_role
        If the login information is correct. If not, the dict is empty.
    """
    with conn.cursor() as curs:
        # Fetch details, check password. Do not give reason for failed login - this is a security issue.
        q_username = f"'{sanitise_input(username)}'"
        curs.execute(f"SELECT password, id, fullname, username FROM officer WHERE username={q_username};")
        result = curs.fetchone()
        if result is None:
            return {}

        expected_hash, user_id, user_fullname, username = result
        # Check password
        if not check_password_hash(expected_hash, password_plain):
            return {}

        return {
            "user_id": user_id,
            "user_fullname": user_fullname,
            "username": username,
            "user_role": "officer"
        }


def get_resident_by_id(conn, id):
    """Arguments: a database connection, resident id to get.
    Returns: a dict containing:
        - user_id
        - user_fullname
        - username
        - user_role
        If id does not exist, returns empty dict.
    """
    with conn.cursor() as curs:
        curs.execute(f"SELECT id, fullname, username FROM resident WHERE id={id};")
        result = curs.fetchone()
        if result is None:
            return {}

        user_id, user_fullname, username = result

        return {
            "user_id": user_id,
            "user_fullname": user_fullname,
            "username": username,
            "user_role": "resident"
        }

def get_officer_by_id(conn, id):
    """Arguments: a database connection, officer id to get.
    Returns: a dict containing:
        - user_id
        - user_fullname
        - username
        - user_role
        If id does not exist, returns empty dict.
    """
    with conn.cursor() as curs:
        curs.execute(f"SELECT id, fullname, username FROM officer WHERE id={id};")
        result = curs.fetchone()
        if result is None:
            return {}

        user_id, user_fullname, username = result

        return {
            "user_id": user_id,
            "user_fullname": user_fullname,
            "username": username,
            "user_role": "officer"
        }