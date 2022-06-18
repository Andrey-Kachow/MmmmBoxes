import os

from flask import Flask, session, render_template, g, redirect, url_for
from flask_socketio import SocketIO

from .main.auth import login_required

socketio = SocketIO()


def create_app():
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
    )

    # Ensure the instance folder exists
    initialize_instance(app)

    # A simple page that says hello
    @app.route("/hello")
    @login_required
    def hello():
        return render_template("hello.html", hide_return=True)

    @app.route("/")
    def mainpage():
        return redirect(url_for("auth.login"))

    # Database
    from .main.database import db

    app.db_conn = db.initialise_db_connection()

    # Check that tables are set up
    db.execute_sql_file(app.db_conn, "schema.sql")

    # Authentication, Officer and Resident blueprints
    from .main import auth, officer, resident

    app.register_blueprint(auth.bp)
    app.register_blueprint(officer.bp)
    app.register_blueprint(resident.bp)

    socketio.init_app(app)

    return app


def initialize_instance(app):
    print("Initializing instance...")
    try:
        os.makedirs(app.instance_path)
        os.makedirs(os.path.join(app.instance_path, "media", "signatures"))
    except OSError:
        pass
