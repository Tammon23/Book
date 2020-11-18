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
        # method = request.form.get('method')
        query = request.form.get('query').strip()

        print("QUERY GOT {}".format(query))

        cur.execute("select * from books where BCourse = %s", [query])
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
    if request.method == 'POST':
        email = request.form["exampleInputEmail1"]
        username = request.form["userName1"]
        password = request.form["exampleInputPassword1"]
        confirm_password = request.form["exampleInputPassword2"]

        if password == "":
            print("password field empty")
            return redirect(url_for('signup'))
            # return jsonify({"error": "password field empty"})

        if password != confirm_password:
            print("password does not match confirmed password")
            return redirect(url_for('signup'))
            # return jsonify({"error": "password does not match confirmed password"})

        # attempting to create account, if account creation fails, returns False and reason is printed

        attempt_status, result = tool.register(username, password, email, conn)

        # if the account could not be registered display why
        if not attempt_status:
            print(result)
            return redirect(url_for('signup'))
            # return jsonify({"error": result})

        # if the account was created successfully log the account in
        # result should contain the user dict

        return login(result)
        # return jsonify({"ok": "boomer"})

    return render_template('signup.html')


# DB login page
@app.route('/login', methods=['GET', 'POST'])
def login(user=None):
    if request.method == "POST":

        # no user information is given, then look for credentials matching
        # that of the form
        # (should only be given after a successful signup)
        if user is None:
            email = request.form["InputEmail"]
            password = request.form["InputPassword"]
            user = tool.userLogin(email, password, conn)

        # if a user with matching credentials was found
        # save information into session
        if user is not None:
            session['logged_in'] = True
            session['email'] = user["UEmail"]
            session['user_type'] = "user"
            session['user_dict'] = user

            return redirect(url_for('home'))
        else:
            print("incorrect password or email")
    return render_template("login.html")


# posting page
@app.route('/posting')
def posting():
    return render_template("posting.html")


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.debug = True
    app.run()
