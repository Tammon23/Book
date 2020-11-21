import os
import tool
import random as rm
import mysql.connector
import sys
from flask import Flask, render_template, redirect, url_for, request, session, jsonify

# DB connection
conn = mysql.connector.connect(user='root', password='root', host="localhost", database="book")

app = Flask(__name__)


# Init redirect
@app.route('/')
def index():
    if 'logged_in' in session and session['logged_in']:
        return redirect((url_for(('home'))))

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
        return render_template('search.html', books=books, search_term=query)

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
        session['user_dict'] = user  # all information needed can be found via this dict

        return redirect(url_for('home'))
    else:
        return jsonify({'error': 'Incorrect password or email'})


@app.route('/posting')
def posting():
    # cur = conn.cursor()
    # cur.execute("select CourseID from courses")
    # courseIDs = cur.fetchall()
    # courseIDs = [tup[0] for tup in courseIDs]

    return render_template("posting.html")


@app.route('/verifyPosting', methods=['POST'])
def verifyPosting():
    cur = conn.cursor(dictionary=True)

    BISBN = request.form["BISBN"]
    BTitle = request.form["BTitle"]
    BAuthor = request.form["BAuthor"]
    BCourse = request.form["BCourse"]
    BPic = request.form["BPic"]
    BNumber = request.form["BNumber"]

    # Verifying that all the fields provided
    if BISBN == "":
        return jsonify({'error': 'Missing ISBN'})

    elif BTitle == "":
        return jsonify({'error': 'Missing Title'})

    elif BAuthor == "":
        return jsonify({'error': 'Missing Author'})

    elif BCourse == "":
        return jsonify({'error': 'Missing Course Code'})

    elif BNumber == "":
        return jsonify({'error': 'Missing Number of Books'})

    # verifying the are posting more than 0 of a particular book
    if BNumber < 1:
        return jsonify({'error': 'Must have positive number of books'})

    # If no picture link was provided, then use the default one
    if BPic == "":
        BPic = "static/img/1559138382833.jpg"

    # verifying the course code is a supported one
    try:
        insertion_command = "INSERT INTO Books (BNumber, BTitle, BAuthor, BISBN, BCourse, BPic) VALUES (%s, %s, %s, " \
                            "%s, %s, %s)"

        cur.execute(insertion_command, [BNumber, BTitle, BAuthor, BISBN, BCourse, BPic])

    except mysql.connector.errors.IntegrityError:
        cur.close()
        return jsonify({'error': 'BCourse not an accepted one'})

    except:
        cur.close()
        return jsonify({'error': sys.exc_info()[0]})

    cur.close()


if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.debug = True
    app.run()
