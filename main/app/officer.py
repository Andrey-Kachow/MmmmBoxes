import functools
import json
from main.database import db
from main.database.signatures import (
    is_valid,
    add_signature,
    mark_package_signed,
    package_is_signed,
    get_data_url,
)

from flask import *
from werkzeug.security import check_password_hash, generate_password_hash

from main.app.populate_template import personalise_email, email_resident
from main.app import socketio
from main.app.auth import login_required
from main.app.ocr import get_package_details_from_file

bp = Blueprint("officer", __name__, url_prefix="/officer")

SUCCESS_200 = (json.dumps({"success": True}), 200, {"ContentType": "application/json"})
FAILURE_404 = (json.dumps({"success": False}), 404, {"ContentType": "application/json"})
EMAIL_LOCATION = "main/database/email-template.txt"


# Check user is logged in and is resident
@bp.before_request
def before_request():
    if "user-id" not in session:
        abort(403, "You are not logged in")
    if not session["user-is-officer"]:
        abort(403, "You are not an officer")


def add_signed_flag(real_dict):
    real_dict["is_signed"] = package_is_signed(real_dict["id"])
    return real_dict


@bp.context_processor
def utility_processor():
    def get_package_list():
        return list(map(add_signed_flag, db.get_all_packages(current_app.db_conn)))

    def get_all_resident_names():
        return db.get_all_resident_names(current_app.db_conn)

    def get_residents():
        return db.get_residents(current_app.db_conn)

    return dict(
        get_package_list=get_package_list,
        get_all_resident_names=get_all_resident_names,
        get_residents=get_residents,
        show_signature_button=True,
    )


@bp.route("/overview", methods=["GET", "POST"])
@login_required
def overview():
    if request.method == "POST":
        just_added = db.add_new_package(
            current_app.db_conn,
            request.form["resident-name"],
            request.form["package-title"],
        )
        if not just_added:
            flash("Oops! Didn't add")
        # Convert the just_added package timestamp to RFC3339 so it can be jsonified.
        socketio.emit("new_package", just_added, broadcast=True)

    return render_template(
        "officer/package-table/view-packages.html",
    )


@bp.route("/template")
def template():
    with open(EMAIL_LOCATION, "r") as f:
        email = f.read()
    return render_template(
        "officer/template-email/edit-template-email.html", email=email
    )


@bp.route("/delete_package/<package_id>", methods=["GET", "POST"])
def delete_package(package_id):
    success = db.delete_package(current_app.db_conn, package_id)
    if success:
        flash("Package deleted.")
    else:
        flash("Oops! Couldn't delete")
    return redirect(url_for("officer.overview"))


@bp.route("/collect_package/<package_id>", methods=["GET", "POST"])
def collect_package(package_id):
    success = db.collect_package(current_app.db_conn, package_id)
    if success:
        flash("Package Collected.")
    else:
        flash("Oops! Couldn't collect")
    return redirect(url_for("officer.overview"))


@bp.route("/residents")
def residents():
    return render_template("officer/resident-table/view-residents.html")


@bp.route("/residents/<int:id>/profile")
def resident_profile(id):
    return render_template(
        "officer/resident-table/resident-profile.html",
        resident=db.get_user_by_id(current_app.db_conn, id),
        get_package_list=lambda: list(
            map(add_signed_flag, db.get_all_packages(current_app.db_conn, id))
        ),
        hide_owner_details_in_table=True,
    )


@bp.route("/sent-email")
def email_all():
    packages = db.get_all_packages(current_app.db_conn)
    with open(EMAIL_LOCATION, "r") as f:
        email = f.read()
    for package in packages:
        if package["collected"] == "Collection pending":
            new_email = personalise_email(
                email,
                full_name=package["fullname"],
                date_d=package["delivered"],
                description=package["title"],
            )
            email_resident(package["email"], new_email)
    return render_template("officer/template-email/emails-sent.html")


@bp.route("/template", methods=["POST"])
def submit():
    email = request.form["email"]
    with open(EMAIL_LOCATION, "w") as f:
        f.write(email)
        flash("Changes Saved!")
    return render_template(
        "officer/template-email/edit-template-email.html", email=email
    )


@bp.route("/sign", methods=["post"])
def sign():
    fullname = request.json["fullname"]
    package_title = request.json["title"]
    package_id = request.json["packageId"]
    data_url = request.json["dataUrl"]

    if not is_valid(current_app.db_conn, fullname, package_title, package_id):
        return FAILURE_404

    if not add_signature(package_id, data_url):
        return FAILURE_404

    if not mark_package_signed(current_app.db_conn, package_id):
        return FAILURE_404

    return SUCCESS_200


@bp.route("/getsign", methods=["post"])
def getsign():
    package_id = request.json["packageId"]

    if not package_is_signed(package_id):
        return FAILURE_404

    return (
        json.dumps({"success": True, "dataUrl": get_data_url(package_id)}),
        200,
        {"ContentType": "application/json"},
    )


@bp.route("/ocr", methods=["post"])
def ocr():

    name = "Resik Odin"
    title = "boxxx pox"

    if "file" not in request.files:
        return FAILURE_404

    name, title = get_package_details_from_file(
        request.files["file"], current_app.db_conn
    )

    return (
        json.dumps(
            {
                "success": True,
                "name": name,
                "title": title,
            }
        ),
        200,
        {"ContentType": "application/json"},
    )
