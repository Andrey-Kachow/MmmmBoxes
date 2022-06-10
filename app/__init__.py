import os

from flask import Flask, session, render_template, g, redirect, url_for
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app(version="Local"):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        # DATABASE_URL=os.environ["DATABASE_URL"],
        # DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return render_template(
            "hello.html",
            context={
                "short_hash_commit": version
            }
        )

    @app.route("/")
    def mainpage():
        return redirect(url_for("auth.login"))

    # database
    from .main.database import db
    app.db_conn = db.initialise_db_connection()

    # Check that tables are set up
    db.execute_sql_file(app.db_conn, "schema.sql")

    # authentication blueprint
    from .main import auth, officer, resident
    app.register_blueprint(auth.bp)
    app.register_blueprint(officer.bp)
    app.register_blueprint(resident.bp)

    socketio.init_app(app)


    return app
