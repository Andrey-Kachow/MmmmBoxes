import functools
from .database import db

from flask import *
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
        added = db.add_new_package(
            current_app.db_conn,
            request.form["resident_name"],
            request.form["package_title"]
        )
        if not added:
            flash("Oops! Didn't add")
    return render_template("officer/overview.html")
