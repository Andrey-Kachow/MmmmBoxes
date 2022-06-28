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
from main.app import socketio


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

    return dict(
        resident=db.get_user_by_id(current_app.db_conn, session.get("user-id")),
        get_package_list=get_package_list,
        hide_owner_details_in_table=True,
        user_profile=True
    )


def post_nominate(request):
    if request.method == "POST":
        nominee_id = request.form['nominee-id']
        package_id = request.form["package-id"]
        db.nominate_parcel(current_app.db_conn, package_id, nominee_id)
        socketio.emit("change", broadcast=True)



@bp.route("/overview", methods=["GET", "POST"])
@login_required
def overview():
    post_nominate(request)
    return render_template("resident/view-packages.html")


@bp.route("/revoke_nomination/<package_id>", methods=["GET", "POST"])
def revoke_nomination(package_id):
    success = db.revoke_nomination(current_app.db_conn, package_id, True)
    if success:
        flash("Nomination revoked.")
    else:
        flash("Oops! Couldn't revoke nomination")
    socketio.emit("change", broadcast=True)
    return redirect(url_for("resident.overview"))

@bp.route("/cancel_nomination/<package_id>", methods=["GET", "POST"])
def cancel_nomination(package_id):
    success = db.revoke_nomination(current_app.db_conn, package_id, False)
    if success:
        flash("Nomination cancelled.")
    else:
        flash("Oops! Couldn't cancell nomination")
    socketio.emit("change", broadcast=True)
    return redirect(url_for("resident.overview"))

@bp.route("/collect_package/<package_id>", methods=["GET", "POST"])
def collect_package(package_id):
    success = db.collect_package(current_app.db_conn, package_id)
    if success:
        flash("Package Collected.")
    else:
        flash("Oops! Couldn't collect")
    return redirect(url_for("resident.overview"))


@bp.route("/profile", methods=["GET"])
@login_required
def profile():
    return render_template("officer/resident-table/resident-profile.html")


ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg"])


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/profile", methods=["POST"])
def upload_image():
    if "nominee-id" in request.form:
        post_nominate(request)
        return redirect(request.url)
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


@bp.context_processor
def utility_processor():
    def get_residents():
        return db.get_residents(current_app.db_conn)

    return dict(
        get_residents=get_residents,
    )
