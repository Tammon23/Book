# This file exists to provide tool functions for the main python script (app.py)
import os
import json
import names
import hashlib
import binascii
import constants
import random as rm
from coolname import generate


def genbook():
    '''
    Generates book information
    Title randomly generated from coolname
    Author randomly generated from names library
    ISBN is randomly generated 12 digit number
    CourseID is a randomly chosen id based off of known Ids
    :return: Dictionary containing a title, author, and ISBN-13
    '''
    title = ' '.join(generate(3)).title()

    author = names.get_full_name()

    # Generate ISBN with proper checksum
    isbn = ''.join([str(rm.randrange(10)) for i in range(12)])
    check = sum([int(i) * 3 if isbn.index(i) % 2 != 0 else int(i) for i in isbn]) % 10
    digit = check if check == 0 else 10 - check

    isbn += str(digit)
    courseID = rm.choice(constants.courseIds)

    BNumber = rm.randint(0, 200)
    BPic = rm.choice(constants.sampleBoookPics)

    # print(title,author, isbn)
    return {'id': BNumber, 'title': title, 'author': author, 'isbn': isbn, 'courseID': courseID, 'BPic': BPic}


# DB setup
def db_setup(connection, cursor, filename):
    """ Creates the tables of the database and inserts course data into Courses table"""

    if connection is not None:
        with open(filename, "r") as f:
            sqlfile = f.read()
            commands = sqlfile.split(";")

            for c in commands:
                try:
                    if c.strip() != "":
                        cursor.execute(c + ";")

                except:
                    pass

        connection.commit()

    else:
        print("Connection is None")


# adds a book to the database
def db_add_book(connection, cursor, book_info):
    if connection is not None:

        insertion_command = "INSERT INTO Books (BNumber, BTitle, BAuthor, BISBN, BCourse, BPic) VALUES (%s, %s, %s, " \
                            "%s, %s, %s) "

        if type(book_info) == list:
            cursor.executemany(insertion_command, book_info)
        else:
            cursor.execute(insertion_command, book_info)

        connection.commit()

    else:
        print("Connection is None")


# Acts as wrapper function for db_add_book to automatically inserts randomly generated books
def db_insert_random_books(connection, cursor, numberOfBooks):
    if connection is not None:
        book_info = [tuple(genbook().values()) for _ in range(numberOfBooks)]
        db_add_book(connection, cursor, book_info)

    else:
        print("Connection is not None")


# fetches n books stored in the db from top to bottom
def db_get_n_books(cursor, numberOfBooks):
    if cursor is not None:
        cursor.execute(f"select * from books limit {numberOfBooks}")
        return cursor.fetchall()

    else:
        print("Cursor is None")


# checks if a username + password matches anything stored
def userLogin(email, password, conn):
    cur = conn.cursor(dictionary=True)

    # getting the users infomation
    u = getUser("UPassword", email, conn)

    if u is None:
        return None

    # verifying password is the stored one
    salt = u["UPassword"][:64]

    if u["UPassword"] == hash_password(password, salt.encode('ascii')):
        return u

    return None


# given a username, their profile is retrieved
def getUser(attribute, email, conn):
    # looking for user in DB
    cur = conn.cursor(dictionary=True)

    # Grab info for user based on email
    cur.execute(f"select {attribute} from users where UEmail = '{email}'")

    # Try to fetch user info from DB
    u = cur.fetchone()
    cur.close()

    # if we found a user return user dict
    if u:
        if "UBooks" in u:
            # turning the list of books back into a list
            u["UBooks"] = json.loads(u["UBooks"])
            return u
        return u

    # if we didn't find user with said username, return None
    return None


def register(username, password, email, conn):
    """
    Creates a new user and adds their information into the database
    """

    # if the user has an allowed email
    if isUniversityEmail(email):
        if isAvailableEmail(email, conn):
            if isAvailableUsername(username, conn):
                # generate a user's profile
                user = dict(UserID=username, UPassword=hash_password(password, None), UEmail=email,
                            UBooks=json.dumps([]), UOtherInfo="")

                # insert user into the db
                cur = conn.cursor(dictionary=True)
                insertion_command = "INSERT INTO Users (UserID, UPassword, UEmail, UBooks, UOtherInfo) VALUES (%s, " \
                                    "%s, %s, %s, %s) "

                cur.execute(insertion_command, tuple(user.values()))

                conn.commit()

                return True, user

            else:
                return False, f"Username: {username} is not available"
        else:
            return False, f"Email: {email} is not available"
    else:
        return False, f"Email: {email} is not a university of windsor email"


def hash_password(password, salt=None):
    """
    convert a password into it's hashed representation
    when verifying passwords a salt can be given
    """
    if salt is None:
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')

    hashed_password = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    hashed_password = binascii.hexlify(hashed_password)

    return (salt + hashed_password).decode('ascii')


def isAvailableEmail(email, conn):
    """
    Checks if an account exists with a given email
    """
    cur = conn.cursor(dictionary=True)

    # Grab info for user based on email
    cur.execute("select UserID from users where UEmail = %s", [email])

    # Try to fetch user info from DB
    u = cur.fetchone()
    cur.close()

    return False if u else True


def isAvailableUsername(username, conn):
    """
    Checks if an account exists with a given username
    """
    cur = conn.cursor(dictionary=True)

    # Grab info for user based on email
    cur.execute("select UserID from users where UserID = %s", [username])

    # Try to fetch user info from DB
    u = cur.fetchone()
    cur.close()

    return False if u else True


def isUniversityEmail(email):
    """
    Checks if the person has a university of windsor email
    """
    return email.lower().endswith('@uwindsor.ca')


if __name__ == '__main__':
    genbook()
