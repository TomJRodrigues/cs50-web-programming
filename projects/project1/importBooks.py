import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    db.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, username VARCHAR NOT NULL, hash VARCHAR NOT NULL)")
    db.execute("CREATE TABLE reviews (id SERIAL PRIMARY KEY, book_id INTEGER NOT NULL, user_id INTEGER NOT NULL, review_text VARCHAR NOT NULL, review_score VARCHAR NOT NULL)")
    db.execute("CREATE TABLE books (id SERIAL PRIMARY KEY, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year VARCHAR NOT NULL, isbn VARCHAR NOT NULL)")
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        if year == "year":
            print("skipped first line")
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Added book isbn: {isbn} named {title} by {author} written in {year}.")
    print("Done!")
    db.commit()

if __name__ == "__main__":
    main()
