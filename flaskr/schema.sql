DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS books;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    isbn TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    year TEXT NOT NULL
);

CREATE TABLE reviews(
    review_id SERIAL PRIMARY KEY,
    rating VARCHAR(2) NOT NULL,
    reviews TEXT NOT NULL,
    userid INTEGER REFERENCES users(id),
    bookid INTEGER REFERENCES books(id)
);