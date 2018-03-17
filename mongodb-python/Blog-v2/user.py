import bottle
import cgi
import re
import hmac
import random
import string
import hashlib
import pymongo
import bson
import sys

from pymongo import MongoClient

def validate_signup(username, password, verify, email, errors):
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    PASS_RE = re.compile(r"^.{3,20}$")
    EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

    errors['username_error']  = ""
    errors['password_error'] = ""
    errors['verify_error'] = ""
    errors['email_error'] = ""


    if not USER_RE.match(username):
        errors['username_error']  = "invalid username. try just letters and numbers"
        return False

    if not PASS_RE.match(password):
        errors['password_error'] = "invalid password."
        return False

    if password != verify:
        errors['verify_error'] = "password must match"
        return False

    if email != "":
        if not EMAIL_RE.match(email):
            errors['email_error'] = "invalid email address"
            return False
        return True

def newuser(connection, username, password, email):
    password_hash = make_pw_hash(password)

    user = {'_id':username, 'password':password_hash}
    if (email != ""):
        user['email'] = email

    db = connection.blog
    users = db.users

    try:
        users.insert(user) #, safe=True)
    except pymongo.errors.DuplicateKeyError:
        print "oops, username is already taken"
        return False
    except pymongo.errors.OperationFailure:
        print "oops, mongo error"
        return False

    return True

def make_pw_hash(pw,salt=None):
    if (salt == None):
        salt = make_salt()
    
    return hashlib.sha256(pw + salt).hexdigest()+","+ salt

def make_salt():
    salt = ""
    for i in range(5):
        salt = salt + random.choice(string.ascii_letters)
    return salt


# will start a new session id by adding a new document to the sessions collection
def start_session(connection, username):
    db = connection.blog
    sessions = db.sessions

    session = {'username':username}

    try:
        sessions.insert(session) 
    except:
        print "Unexpected error on start_session:", sys.exc_info()[0]
        return -1
    
    return str(session['_id'])

def end_session(connection, session_id):
    db = connection.blog
    sessions = db.sessions 

    # this may fail because the string may not be a valid bson objectid
    try:
        id = bson.objectid.ObjectId(session_id)
        sessions.remove({'_id':id})
    except:
        return

SECRET = 'verysecret'
def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
    val = h.split('|')[0]
    if h == make_secure_val(val):
        return val


def get_session(connection, session_id):
    
    db = connection.blog
    sessions = db.sessions

    # this may fail because the string may not be a valid bson objectid
    try:
        id = bson.objectid.ObjectId(session_id)
    except:
        print "bad sessionid passed in"
        return None

    session = sessions.find_one({'_id':id})

    print "returning a session or none"
    return session

def validate_login(connection, username, password, user_record):
    db = connection.blog
    users = db.users

    try:
        user = users.find_one({'_id':username})
    except:
        print "Unable to query database for user"


    if user == None:
        print "User not in database"
        return False

    salt = user['password'].split(',')[1]


    if (user['password'] != make_pw_hash(password,salt)):
        print "user password is not a match"
        return False

    # looks good

    for key in user:
        user_record[key] = user[key] # perform a copy

    return True

def login_check():
    connection = MongoClient('localhost',27017)
    cookie = bottle.request.get_cookie("session")

    if (cookie == None):
        print "no cookie..."
        bottle.redirect("/signup")
    else:
        session_id = check_secure_val(cookie)

    if (session_id == None):
        print "no secure session_id"
        bottle.redirect("/signup")
    else:
        # look up username record
        session = get_session(connection, session_id)
        if (session == None):
            bottle.redirect("/signup")

        return session['username']

def process_login(username, password):
    
    connection = MongoClient('localhost',27017)

    print "user submitted ", username, "pass ", password

    userRecord = {}
    if (validate_login(connection, username, password, userRecord)):
        session_id = start_session(connection, username)
        if (session_id == -1):
            bottle.redirect("/internal_error")

        cookie = make_secure_val(session_id)

        bottle.response.set_cookie("session", cookie)

        bottle.redirect("/welcome")

    else:
        return "login",dict(username=cgi.escape(username), password="",login_error="Invalid Login")

def process_logout():
    
    connection = MongoClient('localhost',27017)

    cookie = bottle.request.get_cookie("session")

    if (cookie == None):
        print "no cookie..."
        bottle.redirect("/signup")

    else:
        session_id = check_secure_val(cookie)

        if (session_id == None):
            print "no secure session_id"
            bottle.redirect("/signup")

        else:
            # remove the session

            end_session(connection, session_id)

            print "clearing the cookie"

            bottle.response.set_cookie("session","")


            bottle.redirect("/signup")

def process_signup(email, username, password, verify):
    connection = MongoClient('localhost',27017)

    errors = {'username':cgi.escape(username), 'email':cgi.escape(email)}
    if (validate_signup(username, password, verify, email, errors)):
        if (not newuser(connection, username, password, email)):
            # trata duplicados
            errors['username_error'] = "Username already in use. Please choose another"
        
            return bottle.template("signup_template", errors)

        session_id = start_session(connection, username)
        print session_id
        cookie= make_secure_val(session_id)
        bottle.response.set_cookie("session",cookie)
        bottle.redirect("/welcome")
    else:
        print "user did not validate"
    
        return errors     