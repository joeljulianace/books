import requests
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, jsonify
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('books', __name__)
key = '8zEy5qaZLzd0NwWTp0trJw'
secret = 'ENnd05HFryY6P6jKEra10yrdi8KJagAmGORvZeaQ4'

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
    book = db.execute('SELECT id, isbn, title, author, year FROM books where id = :id', {"id" : id}).fetchone()

    if book is None:
        abort(404, "Book id {} doesn't exist".format(id))
    return book

def get_review(id):
    db = get_db()
    review = db.execute('SELECT r.rating, r.reviews, r.bookid FROM reviews r JOIN users u ON r.userid = u.id WHERE r.review_id = :id', {"id" : id}).fetchone()

    if review is None:
        abort(404, "Review Id {} doesn't exist".format(id))    
    return review

def get_user_review(id):
    db = get_db()
    review = db.execute('select count(*) from reviews where bookid = :bookid and userid = :userid', {"bookid" : id, "userid" : g.user['id']}).fetchone()
    print(f'Review Count: {review[0]}')
    if review[0] == 1:
        return True
    return False

def get_review_rating(id):
    db = get_db()
    rating = db.execute('SELECT rating FROM reviews WHERE review_id = :reviewid', {"reviewid" : id}).fetchone()    
    print(f'Rating: {rating[0]}')
    return rating[0]

def get_book_average_rating(id):
    db = get_db()
    average = db.execute('SELECT ROUND(AVG(CAST(rating as INTEGER)),2) FROM reviews WHERE bookid = :bookid', {"bookid" : id}).fetchone()    
    if average is not None:
        return average[0]

def get_goodreads_rating_count(key, isbnnumber):
    response = requests.get("https://www.goodreads.com/book/review_counts.json", params = {"key" : key, "isbns" : isbnnumber})
    return response

def get_book_by_isbn(isbn):
    db = get_db()
    book = db.execute('SELECT id, isbn, title, author, year FROM books where isbn = :isbn', {"isbn" : isbn}).fetchone()
    return book

@bp.route('/<int:id>/bookpage', methods=['GET', 'POST'])
@login_required
def bookpage(id):
    book = get_book(id)
    userreview = get_user_review(id)
    average = get_book_average_rating(id)
    db = get_db()
    print('ISBN: {}'.format(book['isbn']))
    response = get_goodreads_rating_count(key, book['isbn'])
    if response.status_code != 200:
        goodreads_average = 'N/A'
        goodreads_work_ratings_count = 'N/A'
    else:
        data = response.json()
        goodreads_average = data['books'][0]['average_rating']
        goodreads_work_ratings_count = data['books'][0]['work_ratings_count']
    reviews = db.execute('SELECT b.isbn, b.title, b.author, b.year, r.reviews, u.id, r.review_id FROM books b JOIN reviews r ON b.id = r.bookid JOIN users u ON u.id = r.userid WHERE b.id = :id', {"id" : id}).fetchall()

    return render_template('books/bookpage.html', book=book, reviews=reviews, userreview=userreview, average=average, goodreads_average=goodreads_average, goodreads_work_ratings_count=goodreads_work_ratings_count)

@bp.route('/<int:id>/update', methods=['GET', 'POST'])    
@login_required
def update(id):
    review = get_review(id)
    bookid = review['bookid']
    book = get_book(bookid)
    rating = get_review_rating(id)

    if request.method == 'POST':
        if "cancel" in request.form:
            return redirect(url_for('books.bookpage', id=review['bookid']))
        elif "save" in request.form:
            review_body = request.form['review']
            rating = request.form['rating']
            error = None

            if not review_body:
                error = 'Review comment is required.'

            if error is not None:
                flash(error)
            else:
                db = get_db()
                db.execute('UPDATE reviews SET reviews = :review_body, rating = :rating WHERE review_id = :id', {"review_body" : review_body, "id" : id, "rating" : rating})
                db.commit()
                return redirect(url_for('books.bookpage', id=review['bookid']))
    return render_template('books/update.html', review=review, book=book, rating=rating)

@bp.route('/<int:id>/create', methods=['GET', 'POST'])    
@login_required
def create(id):
    book = get_book(id)

    if request.method == 'POST':
        if "cancel" in request.form:
            return redirect(url_for('books.bookpage', id=book['id']))
        elif "save" in request.form:
            review_body = request.form['review']
            rating = request.form['rating']
            error = None

        if not review_body:
            error = 'Review comment is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute('INSERT INTO reviews (rating, reviews, userid, bookid) VALUES (:rating, :reviews, :userid, :bookid)', {"rating" : rating, "reviews" : review_body, "userid" : g.user['id'], "bookid" : book['id']})
            db.commit()
            return redirect(url_for('books.bookpage', id=book['id']))
    return render_template('books/create.html')

@bp.route('/api/<string:isbn>')
def get_book_api(isbn):
    book = get_book_by_isbn(isbn)
    if book is None:
        return jsonify({"error":"ISBN Number Not Found"}), 404
    
    title = book['title']
    author = book['author']
    year = book['year']
    isbn = book['isbn']

    response = get_goodreads_rating_count(key, isbn)

    if response.status_code != 200:
        goodreads_average = 'N/A'
        goodreads_work_ratings_count = 'N/A'
    else:
        data = response.json()
        goodreads_average = data['books'][0]['average_rating']
        goodreads_work_ratings_count = data['books'][0]['work_ratings_count']
    
    return jsonify({
        "title" : title,
        "author" : author,
        "year" : year,
        "isbn" : isbn,
        "review_count" : goodreads_work_ratings_count,
        "average_score" : goodreads_average
    })