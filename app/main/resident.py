import functools
from .database import db
from flask import *
from .. import socketio
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint("resident", __name__, url_prefix="/resident")


# Check user is logged in and is resident
@bp.before_request
def before_request():
    if "user_id" not in session:
        abort(403, "You are not logged in")
    if session["user_is_officer"]:
        abort(403, "You are not a resident")


@bp.context_processor
def utility_processor():

    def get_package_list():
        return db.get_all_packages(current_app.db_conn, session["user_id"])

    return dict(get_package_list=get_package_list)


@bp.route("/overview", methods=["GET"])
def overview():
    return render_template("resident/overview.html")
