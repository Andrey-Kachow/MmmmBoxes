import psycopg2
import json
import os
import string
import psycopg2.extras
import datetime
from werkzeug.security import check_password_hash, generate_password_hash

from main.database.signatures import delete_signature
from main.app.populate_template import personalise_email
from main.app.notifications import inform_nomination_cancellation
from main.app.notifications import inform_resident_parcel_arrived
from main.app.notifications import inform_nomination


DATE_FORMAT_STRING = "%H:%M on %a %e %B, %Y"


def initialise_db_connection(ignore_local_db=False):
    """
    Returns: a psycopg2 database connection.

    If local_db.json is found, returns a connection with local postgres database
    Otherwise, attempts to connect to URL given by DATABASE_URL environment variable."""

    # Attempt to get creds
    user_creds = None
    try:
        with open(os.path.join(os.path.dirname(__file__), "local_db.json")) as f:
            user_creds = json.loads(f.read())
            # Check that the relevant keys are in creds.json.
            if not all(
                cred_key in user_creds
                for cred_key in ["host", "dbname", "user", "password"]
            ):
                print("Credentials are incomplete. Using DATABASE_URL variable.")
                user_creds = None

    except FileNotFoundError as e:
        print("Credentials were not found in database/ ! Using DATABASE_URL variable.")
        user_creds = None

    # Return a connection with user creds or DATABASE_URL, depending on existence of user_creds
    if user_creds is None or ignore_local_db:
        return psycopg2.connect(
            os.environ["DATABASE_URL"],
            sslmode="require",
            cursor_factory=psycopg2.extras.RealDictCursor,
        )
    return psycopg2.connect(
        host=user_creds["host"],
        database=user_creds["dbname"],
        user=user_creds["user"],
        password=user_creds["password"],
        cursor_factory=psycopg2.extras.RealDictCursor,
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
            (username,),
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
            (email,),
        )
        if curs.fetchone() is not None:
            return "Email is taken!"

        curs.execute(
            """
            INSERT INTO users (username, password, email, fullname, is_officer)
            VALUES (%s, %s, %s, %s, %s);
            """,
            (username, generate_password_hash(password_plain), email, name, is_officer),
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
            (username,),
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
        - profile_picture
        If id does not exist, returns empty dict.
    """
    with conn.cursor() as curs:
        curs.execute(
            """
            SELECT id, username, email, fullname, is_officer, profile_picture
            FROM users
            WHERE id=%s;
            """,
            (id,),
        )
        result = curs.fetchone()
        if result is None:
            return {}

        return result


def get_all_packages(conn, id=None):
    """Arguments: a database connection, Optional: id of user whose packages to get
    All nominee fields are nullable
    Returns: a list of every package in the system. Packages are dicts:
        - id
        - title
        - delivered
        - deliverednice (human readable format)
        - collected
        - collectednice (human readable format)
        - fullname (of resident)
        - resident_id
        - email (of resident)
        - profile_picture (url)
        - nominee_id
        - nominee_email
        - nominee_fullname
        - nominee_profile_picture
        - mailto, a mailto: link for an individual package
    """
    with conn.cursor() as curs:
        if id is None:
            curs.execute(
                """
                SELECT packages.id, packages.title, packages.delivered, packages.collected, packages.nominee_id, users.fullname, users.id AS resident_id, users.email, users.profile_picture, nominee_table.id AS nominee_id, nominee_table.email AS nominee_email, nominee_table.fullname AS nominee_fullname, nominee_table.profile_picture AS nominee_profile_picture 
                FROM packages
                INNER JOIN users
                ON packages.resident_id = users.id 
                LEFT JOIN users AS nominee_table
                ON nominee_table.id = packages.nominee_id;
                """
            )
        else:
            curs.execute(
                """
                SELECT packages.id, packages.title, packages.delivered, packages.collected, packages.nominee_id, users.fullname, users.id AS resident_id, users.email, users.profile_picture, nominee_table.email AS nominee_email, nominee_table.fullname AS nominee_fullname, nominee_table.profile_picture AS nominee_profile_picture 
                FROM packages
                INNER JOIN users
                ON packages.resident_id = users.id 
                LEFT JOIN users AS nominee_table
                ON nominee_table.id = packages.nominee_id
                WHERE users.id=%s OR packages.nominee_id=%s;
                """,
                (
                    id,
                    id,
                ),
            )

        return [clean_package_dict(dict(p)) for p in curs.fetchall()]

def get_package_by_id(conn, id):
    """Arguments: a database connection, id of package to get
    All nominee fields are nullable
    Returns: a list of every package in the system. Packages are dicts:
        - id
        - title
        - delivered
        - deliverednice (human readable format)
        - collected
        - collectednice (human readable format)
        - fullname (of resident)
        - resident_id
        - email (of resident)
        - profile_picture (url)
        - nominee_id
        - nominee_email
        - nominee_fullname
        - nominee_profile_picture
        - mailto, a mailto: link for an individual package
    """
    with conn.cursor() as curs:
       
        curs.execute(
            """
            SELECT packages.id, packages.title, packages.delivered, packages.collected, packages.nominee_id, users.fullname, users.id AS resident_id, users.email, users.profile_picture, nominee_table.email AS nominee_email, nominee_table.fullname AS nominee_fullname, nominee_table.profile_picture AS nominee_profile_picture 
            FROM packages
            INNER JOIN users
            ON packages.resident_id = users.id 
            LEFT JOIN users AS nominee_table
            ON nominee_table.id = packages.nominee_id
            WHERE packages.id=%s;
            """,
            (
                id,
            ),
        )

        return clean_package_dict(dict(curs.fetchone()))


def revoke_nomination(conn, package_id, nominator_revoked):
    """Arguments: a database connection, package id
    sets the nominee_id to null in the specific entry of the package table which
    effectively cancels nomination"""
    with conn.cursor() as curs:
        curs.execute(
            """
            SELECT packages.id, packages.title, users.fullname, users.email, nominee_table.email AS nominee_email, nominee_table.fullname AS nominee_fullname
            FROM packages
            INNER JOIN users
            ON packages.resident_id = users.id 
            LEFT JOIN users AS nominee_table
            ON nominee_table.id = packages.nominee_id
            WHERE packages.id = %s
            """,
            (package_id,), 
        )

        result = curs.fetchone()
        if result is None: # package does not exist
            return False

        recipient_fullname = result["fullname"]
        recipient_email = result["email"]
        nominee_email = result["nominee_email"]
        nominee_fullname = result["nominee_fullname"]

        inform_nomination_cancellation(recipient_fullname, recipient_email, 
            nominee_fullname, nominee_email, nominator_revoked)

        curs.execute(
            """
            UPDATE packages 
            SET nominee_id = NULL 
            WHERE id = %s
            """,
            (package_id,),
        )
    return True


def add_new_package(conn, resident_name, title):
    """Arguments: a database connection, recipient's name, package title
    Returns: A dict of the package added (BROADCAST THIS), or None if failed for some reason.
        - id
        - title
        - delivered
        - deliverednice (human readable format)
        - collected
        - collectednice (human readable format)
        - fullname (of resident)
        - resident_id
        - email (of resident)"""
    with conn.cursor() as curs:
        # Try to find this resident's id
        curs.execute(
            """
            SELECT id, email, fullname
            FROM users
            WHERE fullname=%s AND is_officer=FALSE;
            """,
            (resident_name,),
        )
        result = curs.fetchone()
        # Resident does not exist
        if result is None:
            return None

        curs.execute(
            """
            INSERT INTO packages (resident_id, title)
            VALUES (%s, %s)
            RETURNING id;
            """,
            (result["id"], title),
        )
        #SEND EMAIL to result["email"] result["fullname"]
        # Get the id, proceed to look up the rest of the details
        package_id = curs.fetchone()["id"]
        curs.execute(
            """
            SELECT packages.id, packages.title, packages.delivered, packages.collected, packages.nominee_id, users.fullname, users.id AS resident_id, users.email
            FROM packages
            INNER JOIN users
            ON packages.resident_id = users.id
            WHERE packages.id = %s;
            """,
            (package_id,),
        )
        conn.commit()
        inform_resident_parcel_arrived(result["email"],result["fullname"])
        return clean_package_dict(dict(curs.fetchone()))


def delete_package(conn, package_id):
    with conn.cursor() as curs:
        curs.execute(
            """
            DELETE
            FROM packages
            WHERE packages.id = %s;
            """,
            (package_id,),
        )
        deleted = curs.rowcount == 1
        conn.commit()

    if deleted:
        delete_signature(package_id)
    return deleted


def collect_package(conn, package_id):
    collection_time = datetime.datetime.now().isoformat()
    with conn.cursor() as curs:
        curs.execute(
            """
            UPDATE packages
            SET collected = %s
            WHERE packages.id = %s;
            """,
            (
                collection_time,
                package_id,
            ),
        )
        conn.commit()
    return True


def update_profile_picture_extension(conn, extension, id):
    """Arguments: database connection, extension of new user profile pic, id of user"""
    with conn.cursor() as curs:
        curs.execute(
            """
            UPDATE users
            SET profile_picture = %s
            WHERE users.id = %s;
            """,
            (
                extension,
                id,
            ),
        )
        conn.commit()


def get_all_resident_names(conn):
    with conn.cursor() as curs:
        curs.execute(
            """
            SELECT fullname
            FROM users
            WHERE is_officer = false
            """
        )
        return list(map(lambda real_dict: real_dict["fullname"], curs.fetchall()))
    return []


def clean_package_dict(pack_dict):
    """Arguments: package in dictionary form
    Returns: cleaned dictionary
    Converts timestamps to RFC3339 and assigns default values to Nones.
    Creates new fields deliverednice and collectednice which can be read by non-programmers"""

    pack_dict["deliverednice"] = pack_dict["delivered"].strftime(DATE_FORMAT_STRING)
    pack_dict["delivered"] = pack_dict["delivered"].isoformat()

    if pack_dict["collected"] is not None:
        pack_dict["collectednice"] = pack_dict["collected"].strftime(DATE_FORMAT_STRING)
        pack_dict["collected"] = pack_dict["collected"].isoformat()
    else:
        pack_dict["collectednice"] = "Collection pending"
        pack_dict["collected"] = "Collection pending"

    pack_dict[
        "mailto"
    ] = f"mailto:{pack_dict['email']}?subject=Package collection: {pack_dict['title']}&body={personalise_email(email=get_template_email(), full_name=pack_dict['fullname'], date_d=pack_dict['deliverednice'], date_t=datetime.date.today().strftime(DATE_FORMAT_STRING), description=pack_dict['title'])}"
    return pack_dict


def get_residents(conn):
    with conn.cursor() as curs:
        curs.execute(
            """
            SELECT id, fullname
            FROM users
            WHERE is_officer = false
            """
        )
        return curs.fetchall()
    return []


def nominate_parcel(conn, package_id, nominee_id):
    """Arguments: database connection, primary key of package, foreign key of nominee
    sets the nominee field of package entry in packages table to be the foreign key of the nominee"""
    with conn.cursor() as curs:

        curs.execute(
            """
            SELECT users.fullname, users.email
            FROM packages
            INNER JOIN users
            ON packages.resident_id = users.id 
            WHERE packages.id = %s
            """,
            (package_id,), 
        )


        result = curs.fetchone()
        if result is None: # package does not exist
            return False

        recipient_fullname = result["fullname"]
        recipient_email = result["email"]

        curs.execute(
            """
            SELECT users.fullname, users.email
            FROM users
            WHERE users.id = %s
            """,
            (nominee_id,), 
        )

        result = curs.fetchone()
        if result is None: # nominee does not exist
            return False

        nominee_email = result["email"]
        nominee_fullname = result["fullname"]

        inform_nomination(recipient_fullname, recipient_email, 
            nominee_fullname, nominee_email)

        curs.execute(
            """
            UPDATE packages
            SET nominee_id = %s
            WHERE id = %s;
            """,
            (
                nominee_id,
                package_id,
            ),
        )
        conn.commit()


def get_template_email():
    with open(os.path.join(os.path.dirname(__file__), "email-template.txt")) as f:
        return f.read().replace("\n", "%0D%0A")
