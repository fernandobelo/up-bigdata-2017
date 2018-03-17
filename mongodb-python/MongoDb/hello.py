import bottle
import pymongo

@bottle.route('/')
def index():
    from pymongo import MongoClient
    connection = MongoClient('localhost',27017)
    db = connection.test # Teste de banco de dados

    names = db.names # coleção 
    item = names.find_one() # busca um documento
    return '<b> Hello %s!' % item['name']
    
bottle.run(host='localhost',port=8082)