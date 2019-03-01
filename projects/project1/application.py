import os

from flask import Flask, render_template, session, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST", "GET"])
def search():
    """Search for a Book"""
    return render_template("search.html")

@app.route("/results", methods=["POST"])
def results():
    """Search Results"""

    # Get form information.
    book_id = request.form.get("book_id")

    books = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id})
    return render_template("results.html", books=books)

@app.route("/book/<int:book_id>")
def book(book_id):
    """ Lists details about a single book."""
    print("test")
    # Get all info for one book.
    print(book_id)
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    return render_template("book.html", book=book)
