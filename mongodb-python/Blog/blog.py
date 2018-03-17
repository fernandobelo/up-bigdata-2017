import bottle

import pymongo
import cgi
import re
import datetime
import random
import hmac
import user
import sys

from pymongo import MongoClient

# insere a entrada de dados do blog e retorna um permalink
def insert_entry(title, post, tags_array, author, category):
    print "inserindo entrada de dados no blog", title, post

    connection = MongoClient('localhost',27017)
    db = connection.blog
    posts = db.posts

    exp = re.compile('\W') # combinar qualquer coisa que nao alfanumerico
    whitespace = re.compile('\s')
    temp_title = whitespace.sub("_",title)
    permalink = exp.sub('', temp_title)

    post = {"title": title,"author": author,"body": post,"permalink":permalink,"tags": tags_array,"date": datetime.datetime.utcnow(), "category": category}

    try:
        posts.insert(post)
        print "Inserido post"

    except:
        print "Erro ao inserir post"
        print "Erros inesperado:", sys.exc_info()[0]

    return permalink

def get_categories():
    connection = MongoClient('localhost',27017)
    db = connection.blog
    categories = db.categories

    return categories.find()

# Extrai a tag do elemento de formulario tags.
def extract_tags(tags):
    whitespace = re.compile('\s')

    nowhite = whitespace.sub("",tags)
    tags_array = nowhite.split(',')

    # limpando
    cleaned = []
    for tag in tags_array:
        if (tag not in cleaned and tag != ""):
            cleaned.append(tag)

    return cleaned

@bottle.route('/')
def blog_index():
    username = login_check()
    if (username == None):
        print "welcome: can't identify user...redirecting to signup"
        bottle.redirect("/signup")

    connection = MongoClient('localhost',27017)
    db = connection.blog
    posts = db.posts
    cursor = posts.find().sort('date', direction=-1).limit(10)
    l=[]    
    
    for post in cursor:
        print post['title']
        post['date'] = post['date'].strftime("%A, %B %d %Y at %I:%M%p") # formatando data

        if ('tags' not in post):
            post['tags'] = [] # preenche vazio se não existir
        if ('comments' not in post):
            post['comments'] = []

        l.append({'title':post['title'], 'body':post['body'], 'post_date':post['date'],'permalink':post['permalink'],'tags':post['tags'],'author':post['author'],'comments':post['comments'], 'category':post['category']})
    
    return bottle.template('blog_template', dict(myposts=l,username=username))
 
@bottle.get('/newpost')
def get_newpost():
    username = login_check()
    if (username == None):
        print "welcome: can't identify user...redirecting to signup"
        bottle.redirect("/signup")

    categories = get_categories()

    return bottle.template("newpost_template", dict(subject="", body="",errors="", tags="", categories=categories))

@bottle.post('/newpost')
def post_newpost():
    username = login_check()
    if (username == None):
        print "welcome: can't identify user...redirecting to signup"
        bottle.redirect("/signup")

    title = bottle.request.forms.get("subject")
    post = bottle.request.forms.get("body")
    tags = bottle.request.forms.get("tags")
    category = bottle.request.forms.get("category")

    if (title == "" or post == ""):
        errors="Post must contain a title and blog entry"
        return bottle.template("newpost_template", dict(subject=cgi.escape(title, quote=True),body=cgi.escape(post, quote=True), tags=tags, errors=errors))

    # Extraindo  tags
    tags = cgi.escape(tags)
    tags_array = extract_tags(tags)

    # Entrada de dados, insira SCAPE
    escaped_post = cgi.escape(post, quote=True)

    # substituir alguns <p> para as quebras de paragrafo
    newline = re.compile('\r?\n')
    formatted_post = newline.sub("<p>",escaped_post)

    permalink=insert_entry(title, formatted_post, tags_array, username, category)

    # redireciona para post criado
    bottle.redirect("/post/" + permalink)

# chamado tanto para os requests regulares e requests JSON
@bottle.get("/post/<permalink>")
def show_post(permalink="notfound"):
    username = login_check()
    if (username == None):
        print "welcome: can't identify user...redirecting to signup"
        bottle.redirect("/signup")

    connection = MongoClient('localhost',27017)
    db = connection.blog
    posts = db.posts

    permalink = cgi.escape(permalink)

    # determina requisica do json
    path_re = re.compile(r"^([^\.]+).json$")

    print "about to query on permalink = ", permalink
    post = posts.find_one({'permalink':permalink})

    if post == None:
        bottle.redirect("/post_not_found")

    print "date of entry is ", post['date']

    # Formata Data
    post['date'] = post['date'].strftime("%A, %B %d %Y at %I:%M%p")

    #inicializacao dos campos do formulario  para adicionar de comentarios
    comment = {}
    comment['name'] = ""
    comment['email'] = ""
    comment['body'] = ""

    return bottle.template("entry_template", dict(post=post, username="indefinido", errors="", comment=comment))


# usado para processar um comentario em um post de blog
@bottle.post('/newcomment')
def post_newcomment():
    username = login_check()
    if (username == None):
        print "welcome: can't identify user...redirecting to signup"
        bottle.redirect("/signup")

    name = bottle.request.forms.get("commentName")
    email = bottle.request.forms.get("commentEmail")
    body = bottle.request.forms.get("commentBody")
    permalink = bottle.request.forms.get("permalink")

    connection = MongoClient('localhost',27017)
    db = connection.blog
    posts = db.posts

    permalink = cgi.escape(permalink)

    post = posts.find_one({'permalink':permalink})

    if post == None:
        bottle.redirect("/post_not_found")

    errors=""
    if (name == "" or body == ""):
        # Formata data
        post['date'] = post['date'].strftime("%A, %B %d %Y at %I:%M%p")

        # Inicializa Comentarios
        comment = {}
        comment['name'] = name
        comment['email'] = email
        comment['body'] = body

        errors="Post must contain your name and an actual comment."
        print "newcomment: comment contained error..returning form with errors"
        return bottle.template("entry_template", dict(post=post, username="indefinido", errors=errors, comment=comment))
    else:
        comment = {}
        comment['author'] = name
        if (email != ""):
            comment['email'] = email
            comment['body'] = body

        try:
            last_error = posts.update({'permalink':permalink}, {'$push':{'comments':comment}}, upsert=False )

            print "about to update a blog post with a comment"
        except:
            print "Could not update the collection, error"
            print "Unexpected error:", sys.exc_info()[0]

        print "newcomment: added the comment....redirecting to post"

        bottle.redirect("/post/"+permalink)

@bottle.get("/post_not_found")
def post_not_found():
    username = login_check()
    if (username == None):
        print "welcome: can't identify user...redirecting to signup"
        bottle.redirect("/signup")

    return "Desculpe, post nao encontrado" 

@bottle.route('/tag/<tag>')
def posts_by_tag(tag="notfound"):
    username = login_check()
    if (username == None):
        print "welcome: can't identify user...redirecting to signup"
        bottle.redirect("/signup")

    connection = MongoClient('localhost',27017)
    db = connection.blog
    posts = db.posts

    tag = cgi.escape(tag)
    cursor = posts.find({'tags':tag}).sort('date', direction=-1).limit(10)
    l=[]

    for post in cursor:
        post['date'] = post['date'].strftime("%A, %B %d %Y at %I:%M%p")
        if ('tags' not in post):
            post['tags'] = []
        if ('comments' not in post):
            post['comments'] = []
        
        l.append({'title':post['title'], 'body':post['body'], 'post_date':post['date'],'permalink':post['permalink'],'tags':post['tags'],'author':post['author'],'comments':post['comments']})

    return bottle.template('blog_template', dict(myposts=l,username="indefinido"))

@bottle.route('/category/<category>')
def posts_by_category(category="notfound"):
    username = login_check()
    if (username == None):
        print "welcome: can't identify user...redirecting to signup"
        bottle.redirect("/signup")

    connection = MongoClient('localhost',27017)
    db = connection.blog
    posts = db.posts

    category = cgi.escape(category)
    cursor = posts.find({'category':category}).sort('date', direction=-1).limit(10)
    l=[]

    for post in cursor:
        post['date'] = post['date'].strftime("%A, %B %d %Y at %I:%M%p")
        if ('tags' not in post):
            post['tags'] = []
        if ('comments' not in post):
            post['comments'] = []
        
        l.append({'title':post['title'], 'body':post['body'], 'post_date':post['date'],'permalink':post['permalink'],'tags':post['tags'],'author':post['author'],'comments':post['comments'], 'category':post['category']})

    return bottle.template('blog_template', dict(myposts=l,username="indefinido"))


@bottle.get('/signup')
def present_signup():
    return bottle.template("signup",dict(username="", password="",password_error="",email="", username_error="", email_error="",verify_error =""))

@bottle.post('/signup')
def process_signup():
    connection = MongoClient('localhost',27017)

    email = bottle.request.forms.get("email")
    username = bottle.request.forms.get("username")
    password = bottle.request.forms.get("password")
    verify = bottle.request.forms.get("verify")

    errors = {'username':cgi.escape(username), 'email':cgi.escape(email)}
    if (user.validate_signup(username, password, verify, email, errors)):
        if (not user.newuser(connection, username, password, email)):
            # trata duplicados
            errors['username_error'] = "Username already in use. Please choose another"
        
            return bottle.template("signup", errors)

        session_id = user.start_session(connection, username)
        print session_id
        cookie= user.make_secure_val(session_id)
        bottle.response.set_cookie("session",cookie)
        bottle.redirect("/welcome")
    else:
        print "user did not validate"
    
        return bottle.template("signup", errors)

@bottle.get("/welcome")
def present_welcome():
    # check for a cookie, if present, then extract value

    username = login_check()
    if (username == None):
        print "welcome: can't identify user...redirecting to signup"
        bottle.redirect("/signup")

    return bottle.template("welcome", {'username':username})

@bottle.get('/newcategory')
def present_newcategory():

    username = login_check()
    if (username == None):
        print "welcome: can't identify user...redirecting to signup"
        bottle.redirect("/signup")

    return bottle.template("newcategory_template", dict(name="",username=username))

@bottle.post('/newcategory')
def post_newcategory():
    username = login_check()
    if (username == None):
        print "welcome: can't identify user...redirecting to signup"
        bottle.redirect("/signup")

    name = bottle.request.forms.get("name")

    connection = MongoClient('localhost',27017)
    db = connection.blog
    categories = db.categories

    category = categories.find_one({'name':name})

    if category != None:
        bottle.redirect("/category_already_exists")

    if (name == ""):
        errors="Category must contain name."
        print "Category: category contained error..returning form with errors"
        #TODO: pretty error message
        return ""
    else:
        try:
            category = {"name": name}
            categories.insert(category)

        except:
            print "Could not update the collection, error"
            print "Unexpected error:", sys.exc_info()[0]

        print "categories: added the category....redirecting...."

        # TODO: pretty redirect
        bottle.redirect("/welcome/")


def login_check():
    #connection = pymongo.Connection(connection_string, safe=True)
    connection = MongoClient('localhost',27017)
    cookie = bottle.request.get_cookie("session")

    if (cookie == None):
        print "no cookie..."
        return None
    else:
        session_id = user.check_secure_val(cookie)

    if (session_id == None):
        print "no secure session_id"
        return None
    else:
        # look up username record
        session = user.get_session(connection, session_id)
        if (session == None):
            return None

        return session['username'] 

@bottle.get('/login')
def present_login():
    return bottle.template("login", dict(username="", password="", login_error=""))

@bottle.post('/login')
def process_login():

    connection = MongoClient('localhost',27017)

    username = bottle.request.forms.get("username")
    password = bottle.request.forms.get("password")

    print "user submitted ", username, "pass ", password

    userRecord = {}
    if (user.validate_login(connection, username, password, userRecord)):
        session_id = user.start_session(connection, username)
        if (session_id == -1):
            bottle.redirect("/internal_error")

        cookie = user.make_secure_val(session_id)

        bottle.response.set_cookie("session", cookie)

        bottle.redirect("/welcome")

    else:
        return bottle.template("login",dict(username=cgi.escape(username), password="",login_error="Invalid Login"))

@bottle.get('/logout')
def process_logout():

    connection = MongoClient('localhost',27017)

    cookie = bottle.request.get_cookie("session")

    if (cookie == None):
        print "no cookie..."
        bottle.redirect("/signup")

    else:
        session_id = user.check_secure_val(cookie)

        if (session_id == None):
            print "no secure session_id"
            bottle.redirect("/signup")

        else:
            # remove the session

            user.end_session(connection, session_id)

            print "clearing the cookie"

            bottle.response.set_cookie("session","")


            bottle.redirect("/signup")

bottle.debug(True)
bottle.run(host='localhost', port=8082)