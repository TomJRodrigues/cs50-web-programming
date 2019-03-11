import os

from flask import Flask, render_template, session, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

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

@app.route("/login.html", methods=["POST", "GET"])
def login():
    username = request.form.get("register_username")
    password = request.form.get("register_password")
    password_confirmation = request.form.get("confirm_password")

    # Check if username submitted
    if not username:
        return render_template("error.html", message="Please enter a username.")

    # Check if username already exists
    checkUser = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
    if checkUser:
        return render_template("error.html", message="Username already exists, please choose a different username.")

    # Check if password submitted
    if not password:
        return render_template("error.html", message="Please enter a password.")
    
    # Check if password confirmation submitted
    if not password_confirmation:
        return render_template("error.html", message="Please confirm your password.")

    # Check if passwords are the same
    if password != password_confirmation:
        return render_template("error.html", message="Passwords must match.")

    # Encrypt password with bcrypt
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # Add user and password hash to users db table
    db.execute("INSERT INTO users (username, hash) VALUES (:username, :pw_hash)", {"username": username, "pw_hash": pw_hash})
    db.commit()

    return render_template("login.html", message="Account successfully created.")

@app.route("/register.html", methods=["GET"])
def register():
    return render_template("register.html")

@app.route("/search", methods=["POST", "GET"])
def search():
    """Search for a Book"""
    username = request.form.get("login_username")
    password = request.form.get("login_password")

    # If username exists, check password

    # Log user in, store in session

    # Display username if logged in or after registering

    return render_template("search.html", username=username)

@app.route("/results", methods=["POST"])
def results():
    """Search Results"""

    # Get form information.
    book_query = request.form.get("book_query")
    book_query = "%" + book_query + "%"

    if db.execute("SELECT * FROM books WHERE title LIKE :query OR author LIKE :query OR isbn LIKE :query", {"query": book_query}).rowcount == 0:
        return render_template("error.html", message="No book title, author or isbn matches that query, please try again.")
    books = db.execute("SELECT * FROM books WHERE title LIKE :query OR author LIKE :query OR isbn LIKE :query", {"query": book_query})
    return render_template("results.html", books=books)

@app.route("/book/<int:book_id>")
def book(book_id):
    """ Lists details about a single book."""
    print("test")
    # Get all info for one book.
    print(book_id)
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    return render_template("book.html", book=book)
