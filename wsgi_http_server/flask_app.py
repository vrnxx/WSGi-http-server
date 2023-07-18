from flask import Flask
from flask import Response
flask_app = Flask('flaskapp')


@flask_app.route('/')
def home():
    return Response(
        'Congratulations! Your WSGI-http server is running Flask app\n',
        mimetype='text/plain'
    )


app = flask_app.wsgi_app