import click
import csv
import os

from flask import current_app, g
from flask.cli import with_appcontext
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

def get_db():
    if 'db' not in g:
        engine = create_engine('postgresql://postgres:admin@localhost:5432/books')
        g.db = scoped_session(sessionmaker(bind=engine))
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.execute(f.read().decode('utf8'))
    db.commit()

    f = open("flaskr/books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute('INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)', {"isbn" : isbn, "title": title, "author" : author, "year": year})
    db.commit()

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)