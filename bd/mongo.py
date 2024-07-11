from pymongo import MongoClient
from pymongo.collection import Collection

def inicia_conexao():

    client = MongoClient('localhost', 27017)
    db = client['puc']
    col = db['recomendacoes']
    return col

def consulta_recomendacoes(usuario, conexao):

    recomendacoes = list(conexao.find({"userId": usuario}))
    list_rec = []
    for rec in recomendacoes:
        list_rec.append((rec['movieId'],rec['rating']))

    return {'Recomendações': list_rec}

def consulta_rec_movies(usuario, conexao: Collection):

    recomendacoes = conexao.find({"userId": usuario})
    list_rec = {}
    for rec in recomendacoes:
        list_rec.update({'movieID': rec['movieId']})

    return list_rec

conn = inicia_conexao()
for x in conn.find({'userId': 28}):
    print(x)
