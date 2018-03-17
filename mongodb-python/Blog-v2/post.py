import bottle

import pymongo
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

def newpost(title, content, tags, category):
    username = user.login_check()

    if (title == "" or content == ""):
        errors="Post must contain a title and blog entry"
        return bottle.template("newpost_template", dict(subject=cgi.escape(title, quote=True),body=cgi.escape(content, quote=True), tags=tags, errors=errors))

    # Extraindo  tags
    tags = cgi.escape(tags)
    tags_array = extract_tags(tags)

    # Entrada de dados, insira SCAPE
    escaped_post = cgi.escape(content, quote=True)

    # substituir alguns <p> para as quebras de paragrafo
    newline = re.compile('\r?\n')
    formatted_post = newline.sub("<p>",escaped_post)

    return insert_entry(title, formatted_post, tags_array, username, category)

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

def get_posts():
    username = user.login_check()

    connection = MongoClient('localhost',27017)
    db = connection.blog
    posts = db.posts
    cursor = posts.find().sort('date', direction=-1).limit(10)
    l=[]    
    
    for postinstance in cursor:
        print postinstance['title']
        postinstance['date'] = postinstance['date'].strftime("%A, %B %d %Y at %I:%M%p") # formatando data

        if ('comments' not in postinstance):
            postinstance['comments'] = []
        if ('tags' not in postinstance):
            postinstance['tags'] = []

        l.append({'title':postinstance['title'], 'body':postinstance['body'], 'post_date':postinstance['date'],'permalink':postinstance['permalink'],'tags':postinstance['tags'],'author':postinstance['author'],'comments':postinstance['comments'], 'category':postinstance['category']})
    
    return dict(myposts=l,username=username)

def show_post(permalink="notfound"):
    user.login_check()

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

    return dict(post=post, username="indefinido", errors="", comment=comment)

def posts_by_tag(tag="notfound"):
    user.login_check()

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
        
        l.append({'title':post['title'], 'body':post['body'], 'post_date':post['date'],'permalink':post['permalink'],'tags':post['tags'],'author':post['author'],'comments':post['comments'], 'category': post['category']})

    return dict(myposts=l,username="indefinido")


def posts_by_category(category="notfound"):
    user.login_check()

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

    return dict(myposts=l,username="indefinido")