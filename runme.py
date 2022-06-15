from app import create_app, socketio
from sys import argv
from os import environ, path
from re import sub, DOTALL

app = create_app()

def replace_bg_colour(col):
    # Replace app/static/style.css background colour
    contents = None
    with open(path.join(path.dirname(__file__), "app/static/style.css")) as f:
        contents = f.read()
    with open(path.join(path.dirname(__file__), "app/static/style.css"), "w") as f:
        f.write(sub(r"(html.*background:)[^;]*(;.*)",
                        r"\1"+col+r"\2",
                        contents,
                        flags=DOTALL
                        ))

if __name__ == "__main__":
    if not "FLASK_ENV" in environ:
        print("FLASK_ENV is not set! Terminating.")
        exit()
    if not "FLASK_APP" in environ:
        print("FLASK_APP is not set! Terminating.")
        exit()

    # Check first argument to decide if running locally
    env = argv[1]

    if env == "live":
        print("Running live.")
        socketio.run(app, host=argv[2], port=argv[3])
    elif env == "dev":
        print("Running dev.")
        replace_bg_colour("#ff8484")
        socketio.run(app, host=argv[2], port=argv[3])
    elif env == "local":
        replace_bg_colour("#ff8484")

        print("Running locally.")
        socketio.run(app)

    else:
        print("Incorrect live/dev/local flag")
        exit()
