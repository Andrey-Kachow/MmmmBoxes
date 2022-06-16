import functools
from .database import db

from flask import *
from .. import socketio
from werkzeug.security import check_password_hash, generate_password_hash

from .auth import login_required

bp = Blueprint("officer", __name__, url_prefix="/officer")


# Check user is logged in and is resident
@bp.before_request
def before_request():
    if "user_id" not in session:
        abort(403, "You are not logged in")
    if not session["user_is_officer"]:
        abort(403, "You are not an officer")


@bp.context_processor
def utility_processor():

    def get_package_list():
        return db.get_all_packages(current_app.db_conn)

    def get_all_resident_names():
        return db.get_all_resident_names(current_app.db_conn)

    def get_residents():
        return db.get_residents(current_app.db_conn)

    return dict(
        get_package_list=get_package_list,
        get_all_resident_names=get_all_resident_names,
        get_residents=get_residents,
        show_signature_button=True
    )


@bp.route("/overview", methods=["GET", "POST"])
@login_required
def overview():
    if request.method == "POST":
        just_added = db.add_new_package(
            current_app.db_conn,
            request.form["resident_name"],
            request.form["package_title"]
        )
        if not just_added:
            flash("Oops! Didn't add")
        # Convert the just_added package timestamp to RFC3339 so it can be jsonified.
        socketio.emit("new_package", just_added, broadcast=True)
    return render_template("officer/overview.html")

email_location = 'app/main/database/email-template.txt'

@bp.route("/template")
def template():
    with open(email_location, 'r') as f:
        email=f.read()
    return render_template("officer/template.html", email=email)


@bp.route("/residents")
def residents():
    return render_template("officer/residents.html")


@bp.route("/residents/<int:id>/profile")
def resident_profile(id):
    return render_template(
        "officer/resident_profile.html",
        resident=db.get_user_by_id(current_app.db_conn, id),
        get_package_list=lambda: db.get_all_packages(current_app.db_conn, id),
        hide_owner_details_in_table=True
     )

@bp.route("/template", methods=['POST'])
def submit():
    email = request.form['email']
    with open(email_location, 'w') as f:
        f.write(email)
        flash("Changes Saved!")
    return render_template("officer/template.html", email=email)
