from os import environ, path, getcwd
import sys
from re import sub, DOTALL

sys.path.append(".")
print(getcwd())
from main.app import create_app, socketio


def replace_bg_colour(col):
    # Replace app/static/style.css background colour
    contents = None
    with open(path.join(path.dirname(__file__), "app/static/style.css")) as f:
        contents = f.read()
    with open(path.join(path.dirname(__file__), "app/static/style.css"), "w") as f:
        f.write(
            sub(
                r"(html.*background:)[^;]*(;.*)",
                r"\1" + col + r"\2",
                contents,
                flags=DOTALL,
            )
        )


if __name__ == "__main__":
    app = create_app()

    if not "FLASK_ENV" in environ:
        print("FLASK_ENV is not set! Terminating.")
        exit()
    if not "FLASK_APP" in environ:
        print("FLASK_APP is not set! Terminating.")
        exit()

    # Check if DRP_PHASE variable is defined. If not, assume running on local
    if not "DRP_PHASE" in environ or environ["DRP_PHASE"] == "local":
        print("Running locally.")
        socketio.run(app)
    else:
        if environ["DRP_PHASE"] == "dev":
            replace_bg_colour("#ff8484")
        socketio.run(app, host=sys.argv[1], port=sys.argv[2])
