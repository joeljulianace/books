import os

from flask import Flask
from . import db

def create_app():
    app = Flask(__name__)

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    db.init_app(app)
    return app