import functools
from .database import db

from flask import *
from .. import socketio
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint("officer", __name__, url_prefix="/officer")


# Check user is logged in and is resident
@bp.before_request
def before_request():
    if "user_id" not in session:
        abort(403, "You are not logged in")
    if not session["user_is_officer"]:
        abort(403, "You are not a resident")


@bp.context_processor
def utility_processor():

    def get_package_list():
        return db.get_all_packages(current_app.db_conn)

    return dict(get_package_list=get_package_list)


@bp.route("/overview", methods=["GET", "POST"])
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
        just_added["delivered"] = just_added["delivered"].strftime(r"%Y-%m-%dT%H:%M:%SZ")
        socketio.emit("new_package", just_added, broadcast=True)
    return render_template("officer/overview.html")

email_location = 'app/main/database/email-template.txt'

@bp.route("/template")
def template():
    with open(email_location, 'r') as f:
        email=f.read()
    return render_template("officer/template.html", email=email)

@bp.route("/template", methods=['POST'])
def submit():
    email = request.form['email']
    with open(email_location, 'w') as f:
        f.write(email)
        flash("Changes Saved!")
    return render_template("officer/template.html", email=email)