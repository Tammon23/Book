import os
import tool
import random as rm
import mysql.connector

from flask import Flask, render_template, redirect, url_for, request, session, jsonify

# DB connection
conn = mysql.connector.connect(user='root', password='root', host="localhost", database="book")

app = Flask(__name__)


# Init redirect
@app.route('/')
def index():
    return redirect(url_for('login'))


# Home page
@app.route('/home')
def home():
    cur = conn.cursor(dictionary=True)

    # Fetch some number of books from DB to display
    cur.execute("select * from books limit %s", [24])
    books = cur.fetchall()

    cur.close()
    return render_template('home.html', books=books)


# Page for specific book
@app.route('/book/<string:isbn>')
def book(isbn):
    cur = conn.cursor(dictionary=True)

    # Grab info for book based on isbn
    cur.execute("select * from books where BISBN = %s", [isbn])

    # Try to fetch book info from DB
    b = cur.fetchone()
    cur.close()

    # Only load page if book was found
    if b:
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
        method = request.form.get('searchby')
        query = request.form.get('query').strip()

        print("select * from books where {} like {}".format(method, '%' + query + '%'))
        cur.execute("select * from books where %s like %s", (method, '%' + query + '%'))
        books = cur.fetchall()

        # Add random price
        for b in books:
            b['price'] = "$" + str(rm.randrange(600)) + "." + str(rm.randrange(100)).zfill(2)

        cur.close()
        return render_template('search.html', books=books)

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
        return jsonify({"error": "password field empty"})

    if password != confirm_password:
        return jsonify({"error": "password does not match confirmed password"})

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
        session['logged_in'] = True
        # session['email'] = user["UEmail"]
        # session['user_type'] = "user"
        session['user_dict'] = user # all information needed can be found via this dict

        return redirect(url_for('home'))
    else:
        return jsonify({'error': 'Incorrect password or email'})


@app.route('/posting')
def posting():
    return render_template("posting.html")


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.debug = True
    app.run()
