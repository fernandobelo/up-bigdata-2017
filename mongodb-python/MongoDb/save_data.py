import pymongo
import sys

from pymongo import MongoClient

connection = MongoClient('localhost',27017)

db = connection.m101
people = db.people
person = {"name":"Barack Obama","role":"President","address":{"address1":"The White House","street":"1600 Pennsylvania Evenue","state":"DC","city":"Washington"},"interests":["government","basketball","the middle east"]}

people.insert(person)
