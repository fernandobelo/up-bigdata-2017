import bottle

import cgi
import re
import datetime
import random
import hmac
import user
import post
import comment
import category
import sys


@bottle.route('/')
def blog_index():
    return bottle.template('blog_template', post.get_posts())
 
@bottle.get('/newpost')
def get_newpost():
    return bottle.template("newpost_template", dict(subject="", body="",errors="", tags="", categories=category.get_categories()))

@bottle.post('/newpost')
def post_newpost():
    title = bottle.request.forms.get("subject")
    content = bottle.request.forms.get("body")
    tags = bottle.request.forms.get("tags")
    category = bottle.request.forms.get("category")

    # redireciona para post criado
    bottle.redirect("/post/" + post.newpost(title,content,tags,category))

# chamado tanto para os requests regulares e requests JSON
@bottle.get("/post/<permalink>")
def show_post(permalink="notfound"):
    return bottle.template("entry_template", post.show_post(permalink))

# usado para processar um comentario em um post de blog
@bottle.post('/newcomment')
def post_newcomment():
    name = bottle.request.forms.get("commentName")
    email = bottle.request.forms.get("commentEmail")
    body = bottle.request.forms.get("commentBody")
    permalink = bottle.request.forms.get("permalink")

    comment.post_newcomment(name,email,body,permalink)

@bottle.get("/post_not_found")
def post_not_found():
    user.login_check()

    return "Desculpe, post nao encontrado" 

@bottle.route('/tag/<tag>')
def posts_by_tag(tag="notfound"):
    return bottle.template('blog_template', post.posts_by_tag(tag))

@bottle.route('/category/<category>')
def posts_by_category(category="notfound"):
    return bottle.template('blog_template', post.posts_by_category(category))


@bottle.get('/signup')
def present_signup():
    return bottle.template("signup_template",dict(username="", password="",password_error="",email="", username_error="", email_error="",verify_error =""))

@bottle.post('/signup')
def process_signup():
    email = bottle.request.forms.get("email")
    username = bottle.request.forms.get("username")
    password = bottle.request.forms.get("password")
    verify = bottle.request.forms.get("verify")

    return bottle.template("signup_template", user.process_signup(email,username,password,verify))

@bottle.get("/welcome")
def present_welcome():
    # check for a cookie, if present, then extract value
    username = user.login_check()

    return bottle.template("welcome_template", {'username':username})

@bottle.get('/newcategory')
def present_newcategory():
    username = user.login_check()
    return bottle.template("newcategory_template", dict(name="",username=username))

@bottle.post('/newcategory')
def post_newcategory():
    name = bottle.request.forms.get("name")

    return bottle.template("error_template",error=category.post_newcategory(name))

@bottle.get('/login')
def present_login():
    return bottle.template("login_template", dict(username="", password="", login_error=""))

@bottle.post('/login')
def process_login():
    username = bottle.request.forms.get("username")
    password = bottle.request.forms.get("password")

    return bottle.template("login_template",user.process_login(username, password))

@bottle.get('/logout')
def process_logout():
    user.process_logout()

bottle.debug(True)
bottle.run(host='localhost', port=8082)