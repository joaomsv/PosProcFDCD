from fastapi import FastAPI
import uvicorn
from bd import mongo

app = FastAPI()
conexao = mongo.inicia_conexao()

@app.get("/rec/v1")
def rota_padrao():
    return {"Rota padrão": "Você acessou a rota default"}

@app.get("/rec/v2/{usuario}")
def consulta_rec(usuario: int):
    return {"usuario": usuario, "resultado_recs": mongo.consulta_recomendacoes(usuario, conexao)}

# multi user, only movie IDs
@app.get("/rec/v3/{users}")
def consulta_rec_mov(users: str):
    rec = []
    for user in users.split(','):
        rec.append({'usuario': int(user), 'recomedacoes': mongo.consulta_rec_movies(int(user), conexao)})
    return {'Resultado': rec}

if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8000)
