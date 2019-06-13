from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('books', __name__)

@bp.route('/')
def index():
   db = get_db()
   books = db.execute('SELECT isbn, title, author, year from books').fetchall()
   return render_template('books/index.html', books=books)