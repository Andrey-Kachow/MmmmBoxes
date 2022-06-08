import os

from flask import Flask, session, render_template


def create_app(test_config=None):
    ''' Application factory '''

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return render_template(
            'hello.html',
            hello_user_name=session.get("user_fullname"),
            hello_user_role=session.get("user_role")
        )

    # database
    from . import db
    db.init_app(app)

    # authentication blueprint
    from . import auth
    app.register_blueprint(auth.bp)

    return app
