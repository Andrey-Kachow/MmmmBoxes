from app import create_app, socketio
from sys import argv

if __name__ == "__main__":
    # Arguments have been passed in, so use them
    if argv[1:]:
        app = create_app(version=argv[3])
        socketio.run(app, host=argv[1], port=argv[2])
    else:
        app = create_app()
        socketio.run(app)