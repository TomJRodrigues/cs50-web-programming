import os

from flask import Flask, render_template, redirect, session, request, jsonify, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_bcrypt import Bcrypt  # https://flask-bcrypt.readthedocs.io/en/latest/

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# http://flask.pocoo.org/docs/1.0/quickstart/
app.secret_key = 'b_5#y2L"F4Q8z\n\xec]/'

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login.html", methods=["POST", "GET"])
def login():
    
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":

        # Forget session
        session.clear()

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

@app.route("/logout.html")
def logout():
    # Remove the username from the session if it's there from http://flask.pocoo.org/docs/1.0/quickstart/
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route("/search", methods=["POST"])
def search():
    """Search for a Book"""
    # Forget a session
    session.clear()

    username = request.form.get("login_username")
    password = request.form.get("login_password")
    login_info = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()

    # Check if username submitted
    if not username:
        return render_template("error.html", message="Please enter a username.")

    # Check if password submitted
    if not password:
        return render_template("error.html", message="Please enter a password.")

    # Check if credentials are accurate
    if not login_info:
        return render_template("error.html", message="Username does not exist, please try again.")
    if not bcrypt.check_password_hash(login_info.hash, password):
        return render_template("error.html", message="Incorrect password, please try again.")

    # Set session
    session["user_id"] = login_info[0]
    session["user_name"] = login_info[1]

    return render_template("search.html", username=username)

@app.route("/results", methods=["POST"])
def results():
    """Search Results"""

    # Get form information.
    book_query = request.form.get("book_query")
    book_query = "%" + book_query + "%"

    # Find book info
    if db.execute("SELECT * FROM books WHERE title LIKE :query OR author LIKE :query OR isbn LIKE :query", {"query": book_query}).rowcount == 0:
        return render_template("error.html", message="No book title, author or isbn matches that query, please try again.")
    books = db.execute("SELECT * FROM books WHERE title LIKE :query OR author LIKE :query OR isbn LIKE :query", {"query": book_query})

    return render_template("results.html", books=books)

@app.route("/book/<int:book_id>", methods=["POST", "GET"])
def book(book_id):
    """ Lists details about a single book."""

    # Get all info for one book
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()

    # Get all reviews for that single book
    if db.execute("SELECT * FROM reviews WHERE book_id = :id", {"id": book.id}).rowcount == 0:
        reviews = None
    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :id", {"id": book.id})

    if request.method == "POST":
        review_text = request.form.get("review_text")
        review_score = request.form.get("review_score")

        # Check if review text supplied
        if not review_text:
            render_template("error.html", message="Please enter a review.")

        # Check if review score supplied
        if not review_score:
            render_template("error.html", message="Please enter a review score.")

        # Add review to database
        db.execute("INSERT INTO reviews (book_id, username, review_text, review_score) VALUES (:book_id, :username, :review_text, :review_score)", {"book_id": book.id, "username": session["user_name"], "review_text": review_text, "review_score": review_score})
        db.commit()
        return redirect(url_for('book', book_id=book.id)) # from: https://stackoverflow.com/questions/46822068/how-to-reload-flask-based-webpage-after-form-submission

    return render_template("book.html", book=book, reviews=reviews)

@app.route("/api/<isbn>", methods=["GET"])
def api(isbn):



    return isbn