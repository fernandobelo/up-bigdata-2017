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


def post_newcomment(name, email, body, permalink):
    user.login_check()

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
        #TODO: MOSTRAR ERRO
        # return dict(post=post, username="indefinido", errors=errors, comment=comment))
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
