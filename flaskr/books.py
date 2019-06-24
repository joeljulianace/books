from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('books', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
   db = get_db()
   books = []
   if request.method == 'POST':
        searchtext = request.form['search']
        error = None

        if not searchtext:
            error = 'Kindly enter ISBN, Book Title or Author Name'
        else:
            print(f'Search Text {searchtext}')
            books = db.execute('SELECT id, title from books where title = :searchtext', {"searchtext" : searchtext}).fetchall()
            return render_template('books/index.html', books=books)
        
        flash(error)
    
   user_id = session.get('user_id')
   if user_id is None:
       return redirect(url_for('auth.login'))
   else:
       return render_template('books/index.html', books=books)

def get_book(id):
    db = get_db()    
    book = db.execute('SELECT isbn, title, author, year FROM books where id = :id', {"id" : id}).fetchone()

    if book is None:
        abort(404, "Book id {} doesn't exist".format(id))
    return book

@bp.route('/<int:id>/bookpage', methods=['GET', 'POST'])
@login_required
def bookpage(id):
    book = get_book(id)        

    return render_template('books/bookpage.html', book=book)