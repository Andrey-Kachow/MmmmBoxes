import os

from flask import Flask, session, render_template, g

def create_app(test_config=None):
    """ Application factory"""

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE_URL=os.environ["DATABASE_URL"],
        # DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route("/hello")
    def hello():
        return render_template(
            "hello.html",
        )

    @app.route("/")
    def mainpage():
        return render_template("base.html")

    # database
    from .database import db
    app.db_conn = db.initialise_db_connection()

    # Check that tables are set up
    db.execute_sql_file(app.db_conn, "schema.sql")

    # authentication blueprint
    from . import auth, officer, resident
    app.register_blueprint(auth.bp)
    app.register_blueprint(officer.bp)
    app.register_blueprint(resident.bp)

    return app
