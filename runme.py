from app import create_app, socketio
from sys import argv
from os import environ

app = create_app()

if __name__ == "__main__":
    if not "FLASK_ENV" in environ:
        print("FLASK_ENV is not set! Terminating.")
        exit()
    if not "FLASK_APP" in environ:
        print("FLASK_APP is not set! Terminating.")
        exit()

    # Arguments have been passed in, so use them
    if argv[1:]:
        socketio.run(app, host=argv[1], port=argv[2])
    else:
        socketio.run(app)