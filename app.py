import os
import json
import tool
import constants
import random as rm
import mysql.connector
from functools import wraps
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, session, jsonify

# DB connection
conn = mysql.connector.connect(user='root', password='root', host="localhost", database="book")

app = Flask(__name__)


# Wrapper function to verify that user is logged in
# If user is not logged in, redirects to login page
def isLoggedIn(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))

    return wrap


# Wrapper function to verify that user is logged in as admin
# If user is not logged in as admin, redirects to home page
# If user is not logged in, redirects to login
def isLoggedAdmin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            if session['user_type'] == 1:
                return f(*args, **kwargs)
            else:
                return redirect(url_for('home'))
        else:
            return redirect(url_for('login'))

    return wrap


# Init redirect
@app.route('/')
def index():
    return redirect(url_for('login'))


# Home page
@app.route('/home')
def home():
    cur = conn.cursor(dictionary=True)

    # Fetch some number of posts from DB to display
    cur.execute("select * from postings limit %s", [24])
    postings = cur.fetchall()

    # getting more book information from each post
    for post in postings:
        cur.execute("select * from books where BISBN = %s", [post['UBooks']])
        post.update(cur.fetchone())

    cur.close()
    return render_template('home.html', books=postings)


# Page for specific book
@app.route('/book/<string:isbn>')
@isLoggedIn
def book(isbn):
    cur = conn.cursor(dictionary=True)

    # Grab info for book based on isbn
    cur.execute("select * from books where BISBN = %s", [isbn])

    # Try to fetch book info from DB
    b = cur.fetchone()

    # Grab the person who posted the book based on isbn
    cur.execute("select * from postings where UBooks = %s", [isbn])

    # Try to fetch book info from DB
    p = cur.fetchone()
    cur.close()

    # getting the email of the poster
    UEmail = tool.getUser("UEmail", p['UserID'], conn)

    # Only load page if book was found
    if b and p:
        b.update(p)
        b.update(UEmail)
        return render_template('book.html', book=b)
    # if the book is not found then display error page
    else:
        return redirect(url_for('index'))


# DB search page
@app.route('/search', methods=['GET', 'POST'])
def search():
    # Result of search
    if request.method == 'POST':
        cur = conn.cursor(dictionary=True)

        # Grab info from HTML form
        method = request.form.get('searchby').strip()
        query = request.form.get('query').strip()

        # Builds query with column name using python string manipulation
        # Method is within a set of fixed values, low risk of SQL injection
        q = "select * from books where " + method + " like %s"
        args = ('%' + query + '%',)
        cur.execute(q, args)
        books = cur.fetchall()

        cur.close()
        return render_template('search.html', books=books, post=True, query=query)

    # GET method, display search and search options
    else:
        return render_template('search.html')


# DB signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')


# used to verify if all fields when signup is valid
@app.route('/verifySignUp', methods=['POST'])
def verifySignUp():
    email = request.form["email"]
    username = request.form["username"]
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]

    if password == "":
        return jsonify({"error": "Password field empty"})

    if password != confirm_password:
        return jsonify({"error": "Password does not match confirmed password"})

    # attempting to create account, if account creation fails, returns False and reason is printed
    attempt_status, result = tool.register(username, password, email, conn)

    # if the account could not be registered display why
    if not attempt_status:
        return jsonify({"error": result})

    # if the account was created successfully log the account in
    # result should contain the user dict

    return verifyLogin(result)


# DB login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")


@app.route('/logout')
@isLoggedIn
def logout():
    session.clear()
    return redirect(url_for('login'))


# used to verify if all fields when logging in is valid
@app.route('/verifyLogin', methods=['POST'])
def verifyLogin(user=None):
    # no user information is given, then look for credentials matching
    # that of the form
    # (should only be given after a successful signup)
    if user is None:
        email = request.form["email"]
        password = request.form["password"]
        user = tool.userLogin(email, password, conn)

    # if a user with matching credentials was found
    # save information into session
    if user is not None:
        if user['IsAdmin']:
            session['user_type'] = 1
        else:
            session['user_type'] = 2

        session['logged_in'] = True
        session['user_dict'] = user  # all information needed can be found via this dict

        return redirect(url_for('home'))
    else:
        return jsonify({'error': 'Incorrect password or email'})


@app.route('/posting')
@isLoggedIn
def posting():
    return render_template("posting.html", courses=constants.courseIds)


@app.route('/verifyPosting', methods=['POST'])
def verifyPosting():
    cur = conn.cursor(dictionary=True)

    BISBN = request.form["BISBN"]
    BTitle = request.form["BTitle"].strip()
    BAuthor = request.form["BAuthor"].strip()
    BCourse = request.form["BCourse"].strip()
    BPrice = float(request.form["BPrice"])
    BPic = rm.choice(constants.sampleBoookPics)
    BNumber = int(request.form["BNumber"])
    BDesc = request.form["BDesc"].strip()

    if not tool.isValidISBN(BISBN):
        return jsonify({"error": "Please enter a valid ISBN"})

    if BCourse == "default":
        return jsonify({"error": "Please select a course"})

    try:
        insertion_command = "INSERT INTO Books (BISBN, BTitle, BAuthor, BCourse, BPrice, BDesc, BPic, BNumber) VALUES " \
                            "(%s, %s, %s, %s, %s, %s, %s, %s)"

        cur.execute(insertion_command, [BISBN, BTitle, BAuthor, BCourse, BPrice, BDesc, BPic, BNumber])

        conn.commit()
        cur.close()

    except mysql.connector.Error as err:
        cur.close()
        return jsonify({"error": f"ISBN {BISBN} has already been posted"})

    # updating the user's posting profile
    postingHelper(BISBN)
    return redirect(url_for('home'))


# updates relevant tables after a post has been made
def postingHelper(BISBN):
    cur = conn.cursor(dictionary=True)
    # adding the posting to the posting tables
    insertion_command = "INSERT INTO Postings (UserID, UBooks, PostDates) VALUES (%s, %s, %s)"
    cur.execute(insertion_command,
                [session['user_dict']['UserID'], BISBN, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

    # updating the user's posting profile
    usersBooks = session['user_dict']['UBooks']
    usersBooks.append(BISBN)
    update_command = "UPDATE Users SET UBooks = %s WHERE UserID = %s"
    cur.execute(update_command, [json.dumps(usersBooks), session['user_dict']['UserID']])
    conn.commit()
    cur.close()


if __name__ == '__main__':
    # tool.db_setup(conn, conn.cursor(dictionary=True), "sqlcommands_initial.sql")
    # tool.db_insert_random_users(conn, numUsers=20)
    # tool.db_insert_n_random_postings(conn, numPostings=40)

    app.secret_key = os.urandom(12)
    app.debug = True
    app.run()
