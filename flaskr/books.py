from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('books', __name__)

@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
   db = get_db()
   books = []
   if request.method == 'POST':
        searchtext = request.form['search']
        error = None

        if not searchtext:
            error = 'Kindly enter ISBN, Book Title or Author Name'
        else:
            searchtext = "%s" % '%' + searchtext + '%'
            query = "SELECT id, title FROM books WHERE isbn LIKE '%s' or title LIKE '%s' or author LIKE '%s'" % (searchtext, searchtext, searchtext)
            books = db.execute(query).fetchall()
            if books:
                return render_template('books/index.html', books=books)
            else:
                error = 'Sorry no matches found!'

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
    db = get_db()
    reviews = db.execute('SELECT b.isbn, b.title, b.author, b.year, r.reviews, u.id, u.username FROM books b JOIN reviews r ON b.id = r.bookid JOIN users u ON u.id = r.userid WHERE b.id = :id', {"id" : id}).fetchall()

    return render_template('books/bookpage.html', book=book, reviews=reviews)