import bottle
import pymongo
import sys
import user

from pymongo import MongoClient

def get_categories():
    connection = MongoClient('localhost',27017)
    db = connection.blog
    categories = db.categories

    return categories.find()


def post_newcategory(name):
    user.login_check()

    connection = MongoClient('localhost',27017)
    db = connection.blog
    categories = db.categories

    category = categories.find_one({'name':name})

    if category != None:
        return("Category already exists")

    if (name == ""):
        errors="Category must contain name."
        print "Category: category contained error..returning form with errors"
        return(errors)
    else:
        try:
            category = {"name": name}
            categories.insert(category)

        except:
            print "Could not update the collection, error"
            print "Unexpected error:", sys.exc_info()[0]

        print "categories: added the category....redirecting...."

        # TODO: pretty redirect
        bottle.redirect("/welcome")
