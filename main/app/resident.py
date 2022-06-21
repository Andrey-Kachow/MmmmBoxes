import functools
from main.database import db
from flask import *
from werkzeug.security import check_password_hash, generate_password_hash
from main.app.auth import login_required
from werkzeug.utils import secure_filename
import os
import requests
from flask import current_app
import base64

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


@bp.route("/profile")
@login_required
def profile():
    return render_template(
        "officer/resident-table/resident-profile.html",
        resident=db.get_user_by_id(current_app.db_conn, session.get("user-id")),
        get_package_list=lambda: db.get_all_packages(
            current_app.db_conn, session.get("user-id")
        ),
        hide_owner_details_in_table=True,
        user_profile=True,
    )


ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg"])


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/profile", methods=["POST"])
def upload_image():
    if "file" not in request.files:
        flash("No file part")
        return redirect(request.url)
    file = request.files["file"]
    if file.filename == "":
        flash("No image selected for uploading")
        return redirect(request.url)
    if file and allowed_file(file.filename):
        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": "4e296b8010cd29c178d8b70279515dbd",
            "image": base64.b64encode(file.read()),
        }
        res = requests.post(url, payload)
        profile_picture_extension = res.json()["data"]["url"]
        db.update_profile_picture_extension(
            current_app.db_conn, profile_picture_extension, session.get("user-id")
        )
        flash("Image successfully uploaded and displayed below")
        return redirect("profile")
    else:
        flash("Allowed image types are - png, jpg, jpeg")
        return redirect(request.url)
