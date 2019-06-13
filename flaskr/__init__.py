import os

from flask import Flask
from . import db
from . import auth
from . import books

def create_app():
    app = Flask(__name__)
    app.secret_key = 'super secret key'


    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(books.bp)
    app.add_url_rule('/', endpoint='index')
    return app