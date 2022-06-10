from app import create_app, socketio
from sys import argv

app = create_app()

if __name__ == "__main__":
    # Arguments have been passed in, so use them
    if argv[1:]:
        socketio.run(app, host=argv[1], port=argv[2])
    else:
        socketio.run(app)