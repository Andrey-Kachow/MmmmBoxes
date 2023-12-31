import functools
from pickle import FALSE
from main.database import db

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app,
)
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        fullname = request.form["fullname"]
        is_officer = request.form.get("is-officer") is not None

        error = db.register_new_user(
            current_app.db_conn, fullname, email, username, password, is_officer
        )
        if error is not None:
            flash(error)
            return redirect(url_for("auth.register"))
        else:
            return redirect(url_for("auth.login"))

    else:
        return render_template("auth/register.html", signed_out=True)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        details = db.verify_password(current_app.db_conn, username, password)

        # If details is empty, something went wrong during login.
        if not details:
            flash("Incorrect login details!")
            return redirect(url_for("auth.register"))

        session.clear()
        session["user-id"] = details["id"]
        session["user-fullname"] = details["fullname"]
        session["user-is-officer"] = details["is_officer"]

        if not details["is_officer"]:
            return redirect(url_for("resident.overview"))

        return redirect(url_for("officer.overview"))

    else:
        return render_template("auth/login.html", signed_out=True)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user-id")
    is_officer = session.get("user-is-officer")

    # No user_id
    if user_id is None:
        g.user = None
        return

    details = db.get_user_by_id(current_app.db_conn, user_id)
    # User_id not found
    if not details:
        g.user = None
        return
    g.user = details


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view
