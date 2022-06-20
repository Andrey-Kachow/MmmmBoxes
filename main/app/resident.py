import functools
from main.database import db
from flask import *
from werkzeug.security import check_password_hash, generate_password_hash
from main.app.auth import login_required


bp = Blueprint("resident", __name__, url_prefix="/resident")


# Check user is logged in and is resident
@bp.before_request
def before_request():
    if "user-id" not in session:
        abort(403, "You are not logged in")
    if session["user-is-officer"]:
        abort(403, "You are not a resident")


@bp.context_processor
def utility_processor():
    def get_package_list():
        return db.get_all_packages(current_app.db_conn, session["user-id"])

    return dict(get_package_list=get_package_list)


@bp.route("/overview", methods=["GET"])
@login_required
def overview():
    return render_template("resident/view-packages.html")
