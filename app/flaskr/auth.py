import functools
from .database import db

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash




bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        fullname = request.form["fullname"]
        role = request.form["user_role"]

        error = None
        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif not role:
            error = "Please select the role"
        elif not fullname:
            error = "Full Name is required"

        # Return on error
        if error is not None:
            flash(error)
            return render_template("auth/register.html")

        if role == "resident":
            db.add_new_resident(current_app.db_conn, fullname, email, username, password)
        else:
            db.add_new_officer(current_app.db_conn, fullname, email, username, password)

        return redirect(url_for("auth.login"))

    else:
        return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["user_role"]

        details = db.verify_password_resident(current_app.db_conn, username, password) if role == "resident" \
                     else db.verify_password_officer(current_app.db_conn, username, password)
        # If details is empty, something went wrong during login.
        if not details:
            flash("Incorrect login details!")
            return render_template("auth/register.html")

        session.clear()
        session["user_id"] = details["user_id"]
        session["user_fullname"] = details["user_fullname"]
        session["user_role"] = role
        return redirect(url_for("hello"))

    else:
        return render_template("auth/login.html")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    role = session.get("user_role")

    # No user_id
    if user_id is None:
        g.user = None
        return

    details = db.get_resident_by_id(current_app.db_conn, user_id) if role=="resident" \
            else db.get_officer_by_id(current_app.db_conn, user_id)
    # User_id not found
    if not details:
        g.user = None
        return

    g.user = details

@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("hello"))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view
