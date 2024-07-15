# Sistema de Recomendação de Filmes com Docker Compose, PySpark, MongoDB, FastAPI

## Introdução

Neste texto, exploraremos um fluxo completo para geração e entrega de recomendações utilizando tecnologias modernas de maneira integrada. Utilizaremos a MLlib do Apache Spark, mais precisamente o modelo ALS (Alternating Least Squares), para desenvolver recomendações personalizadas. Essas recomendações serão persistidas no MongoDB, que estará operando em ambiente local. Para aqueles interessados, também será possível adaptar o ambiente utilizando containers Docker. Uma vez armazenadas as recomendações, iremos configurar uma API utilizando a biblioteca FastAPI. Essa API será responsável por receber solicitações de recomendações com base no ID do usuário, proporcionando uma solução escalável e eficiente para sistemas de recomendação.

### Docker Compose

O Docker Compose é uma ferramenta que permite definir e gerenciar múltiplos conteiners Docker como uma aplicação única. Com um arquivo YAML simples, você pode configurar todos os serviços necessários para sua aplicação e iniciar todos eles com um único comando. Isso facilita o desenvolvimento, teste e implantação de aplicações distribuídas, garantindo consistência e facilitando a escalabilidade.

### PySpark

PySpark é uma interface Python para Apache Spark, um poderoso framework de processamento distribuído de dados. Ele permite aos desenvolvedores escrever código em Python para processar grandes volumes de dados de maneira rápida e eficiente, aproveitando a escalabilidade e o paralelismo oferecidos pelo Spark. PySpark suporta diversas fontes de dados e operações complexas como transformações, análises e machine learning, tornando-o ideal para aplicações de big data e análise de dados em larga escala.

### MongoDB

MongoDB é um banco de dados NoSQL de alta performance, orientado a documentos. Ele armazena os dados em documentos flexíveis sem esquemas rígidos, o que facilita a escalabilidade e a manipulação de dados semi-estruturados. MongoDB suporta consultas poderosas, índices eficientes e replicação automática para garantir disponibilidade e tolerância a falhas. É amplamente utilizado em aplicações modernas que requerem flexibilidade no esquema de dados e necessitam lidar com grandes volumes de informações de forma distribuída.

### FastAPI

FastAPI é um framework moderno para desenvolvimento de APIs web em Python. Ele é rápido, fácil de usar e baseado em tipagem estática, o que facilita a criação de APIs robustas e com suporte a documentação automática interativa. FastAPI utiliza o padrão ASGI para alta performance e suporta operações assíncronas, permitindo lidar eficientemente com múltiplas requisições simultâneas. É uma escolha popular para desenvolvedores que buscam produtividade e desempenho ao criar serviços web escaláveis em Python.

## Objetivos

1. **Desenvolver um Sistema de Recomendação:** Usar o modelo ALS da MLlib do Spark para criar recomendações personalizadas.
2. **Armazenamento de Dados Eficiente:** Utilizar o MongoDB para guardar as recomendações de forma escalável.
3. **Criar uma API Rápida:** Implementar uma API com FastAPI para solicitar recomendações com base no ID do usuário.

## Experimentos

### Docker Compose Setup

A base desse trabalho será feita usando Docker Compose, para facilitar a implementação e o gerenciamento das ferramentas. O arquivo `compose.yaml` será dividido em três seções distintas para melhor organização e funcionalidade.

#### Criando a Rede

```yaml
networks:
  app-tier:
    driver: bridge
```

Uma rede é necessária para que os containers consigam se comunicar entre si. Aqui criamos a rede `app-tier` que utiliza o driver tipo `bridge`. O driver `bridge` cria uma rede isolada internamente ao host Docker. Cada container conectado a essa rede recebe um endereço IP dentro do intervalo pré-definido pelo Docker. Essa rede permite que os containers se comuniquem uns com os outros usando esses endereços IP internos, além de fornecer acesso externo ao host através de portas expostas pelos containers.

#### MongoDB Container

```yaml
mongo:
    image: mongo
    container_name: mongo
    networks:
      - app-tier
    ports:
      - 27017:27017
    volumes:
      - ./data:/data/db
```

As configurações do MongoDB são simples:

1. Vamos garantir que ele esteja na mesma rede `app-tier`.
2. Mapear a porta `27017` para garantir nosso acesso.
3. Mapear a pasta `/data/db` para garantir que os dados permaneçam mesmo se precisarmos recriar o container.

#### PySpark Container

```yaml
pyspark:
    image: jupyter/pyspark-notebook
    container_name: pyspark
    networks:
      - app-tier
    ports:
      - 11000:8888
    volumes:
      - ./exemplos:/home/jovyan/
```

Podemos ver que a configuração do PySpark é bem similar à do MongoDB. A maior diferença está no mapeamento das portas `11000:8888` e no mapeamento da pasta `./exemplos:/home/jovyan/` para garantir o compartilhamento dos arquivos de código sem a necessidade de importação.

#### Iniciando os Containers

Para subir os containers, utilize o comando `docker-compose up -d` no terminal.

![Docker Compose Up](media/dockerComposeUp.png 'Docker Compose Up')
![Containers](media/containers.png 'Containers')

Após a inicialização dos containers, podemos começar o trabalho. Para acessar o PySpark, precisamos abrir o link gerado automaticamente no log.

![Link PySpark](media/linkPySpark.png 'Link PySpark')

Acessando esse link, percebemos que ocorre um erro. Isso acontece porque precisamos alterar a parte da porta de `127.0.0.1:8888` para a porta que mapeamos, que é `127.0.0.1:11000`. Após fazer essa modificação, o PySpark abrirá sem problemas.

![PySpark](media/pyspark.png 'PySpark')

No lado esquerdo, podemos ver 2 arquivos:

- **ExemploALS.ipynb:** Contém o código para nosso sistema de recomendações.
![Codigo](media/codigo.png 'Codigo')
- **sample_movielens_ratings.txt:** É a nossa base de dados.
![Base de Dados](media/baseDeDados.png 'Base de Dados')

#### Criando um Spark Session

Antes de tudo, precisamos criar uma sessão do Spark para que possamos começar a fazer o treinamento dos modelos para nosso sistema.

```py
from __future__ import print_function

import sys
if sys.version >= '3':
    long = int

from pyspark.sql import SparkSession
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.sql import Row
```

Aqui estamos importando as bibliotecas necessárias.

```py
spark = SparkSession\
        .builder\
        .appName("ALSExample")\
        .config("spark.mongodb.read.connection.uri", "mongodb://172.20.0.2:27017/puc.recomendacoes") \
        .config("spark.mongodb.write.connection.uri", "mongodb://172.20.0.2:27017/puc.recomendacoes") \
        .config('spark.jars.packages',"org.mongodb.spark:mongo-spark-connector_2.12:10.3.0")\
        .getOrCreate()
```

Agora podemos iniciar nossa sessão do Spark. Precisamos configurar a sessão para que ela se conecte ao nosso MongoDB. Para isso, é necessário descobrir o IP que ele está utilizando.

![Inspect MongoDB](media/inspectMongoDB.png 'Inspect MongoDB')

Através da funcionalidade do Docker Desktop, podemos dar um `inspect` no container e identificar o IP, sendo neste caso `172.20.0.2`. Também criamos um banco `puc` e uma coleção `recomendacoes`.

#### Carregando os Dados

```py
lines = spark.read.text("sample_movielens_ratings.txt").rdd
parts = lines.map(lambda row: row.value.split("::"))
ratingsRDD = parts.map(lambda p: Row(userId=int(p[0]), movieId=int(p[1]),
                                     rating=float(p[2]), timestamp=long(p[3])))
ratings = spark.createDataFrame(ratingsRDD.collect())
```

Agora vamos fazer a leitura da nossa base de dados `sample_movielens_ratings.txt`. Cada linha contém um `userID`, `movieID`, `rating` e `timestamp`, separados por `::`. Faremos a leitura e criaremos um dataframe para que seja possível manipularmos os dados.

#### Treinando o Modelo

Agora que temos um dataframe, podemos começar a treinar os dados.

```py
(training, test) = ratings.randomSplit([0.8, 0.2])

als = ALS(maxIter=5, regParam=0.01, userCol="userId", itemCol="movieId", ratingCol="rating",
              coldStartStrategy="drop")
model = als.fit(training)
```

Dividimos de forma aleatória nossos dados em 2 conjuntos: 80% para treinamento e 20% para teste. Após isso, executamos o `ALS` limitando o número máximo de iterações no treinamento para 5 e usando a estratégia `drop` para cold start. Isso significa que ele irá ignorar qualquer usuário que tenha um número muito pequeno de interações para não gerar recomendações para ele, o que não seria eficaz.

#### Gerando as Recomendações

```py
predictions = model.transform(test)
evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating",
                                    predictionCol="prediction")
rmse = evaluator.evaluate(predictions)
print("Root-mean-square error = " + str(rmse))
```

Vamos calcular a margem de erro da nossa predição, que neste caso é `Root-mean-square error = 1.7488800236279904`.

```py
userRecs = model.recommendForAllUsers(10)
userRecs.show(10, False)
```

Finalmente, podemos gerar nossas recomendações. Decidimos gerar 10 recomendações para cada usuário.

![Recomendações](media/recomendacoes.png 'Recomendações')

#### Salvando no MongoDB

```py
userRecs.select(userRecs["userId"], \
                userRecs["recommendations"]["movieId"].alias("movieId"),\
userRecs["recommendations"]["rating"].cast('array<double>').alias("rating")).\
    write.format("mongodb").mode("append").save()
```

Para concluir, vamos salvar todas as recomendações geradas no MongoDB.

![MongoDB](media/mongodb.png 'MongoDB')

#### Instalando Dependencias para FastAPI

Agora que salvamos as recomendações no MongoDB, vamos criar uma API para que possamos consultá-las a qualquer momento. Iremos utilizar as seguintes bibliotecas:

```txt
fastapi==0.68.0
uvicorn==0.15.0
pymongo==3.12.0
```

Usamos FastAPI para criar uma API simples, PyMongo para acessar nosso banco no MongoDB e Uvicorn como nosso servidor ASGI. Para instalar, é só executar o comando `pip install -r requirements.txt`.

#### Consultando as Recomendações

Após executar nosso `main.py`, podemos ver que existem 3 APIs ao acessar `http://localhost:8000/docs`.

```py
@app.get("/rec/v1")
def rota_padrao():
    return {"Rota padrão": "Você acessou a rota default"}
```

O primeiro API é somente um teste para validar se está funcionando corretamente.

```py
@app.get("/rec/v2/{usuario}")
def consulta_rec(usuario: int):
    return {"usuario": usuario, "resultado_recs": mongo.consulta_recomendacoes(usuario, conexao)}
```

Aqui vamos consultar as recomendações de um usuário. O ID do usuário é passado no endereço como parâmetro e chama uma função `consulta_recomendacoes()` que irá retornar cada filme e sua rating.

```py
def consulta_recomendacoes(usuario, conexao):
    recomendacoes = list(conexao.find({"userId": usuario}))
    list_rec = []
    for rec in recomendacoes:
        list_rec.append((rec['movieId'],rec['rating']))
    return {'Recomendações': list_rec}
```

![Consulta Recomendações para 1 user](media/consultRec1.png 'Consulta Recomendações para 1 user')

Aqui consultamos as recomendações do usuário 3, sendo o primeiro conjunto de números o ID dos filmes e o segundo os ratings.

```py
@app.get("/rec/v3/{users}")
def consulta_rec_mov(users: str):
    rec = []
    for user in users.split(','):
        rec.append({'usuario': int(user), 'recomedacoes': mongo.consulta_rec_movies(int(user), conexao)})
    return {'Resultado': rec}
```

O nosso último API, iremos consultar múltiplos usuários, mas retornar somente os IDs dos filmes. Isso se torna possível utilizando os usuários passados no endereço, separados por vírgula, e enviando-os individualmente para a função `consulta_rec_movies()`.

```py
def consulta_rec_movies(usuario, conexao: Collection):
    recomendacoes = conexao.find({"userId": usuario})
    list_rec = {}
    for rec in recomendacoes:
        list_rec.update({'movieID': rec['movieId']})
    return list_rec
```

A função recebe o usuário, consulta o banco e logo retorna para a API um dicionário.

![Consulta Recomendações para 3 Users](media/consultRec3.png 'Consulta Recomendações 3 Users')

Aqui podemos ver uma consulta para 3 usuários.

## Conclusão

Em conclusão, desenvolvemos uma solução robusta e moderna para recomendações personalizadas, utilizando o modelo ALS da MLlib do Apache Spark e o MongoDB para armazenamento de dados. A implementação da API com FastAPI oferece uma interface escalável e eficiente para acessar as recomendações. Embora a margem de erro possa ser reduzida através de melhorias na base de dados e ajustes no algoritmo, a arquitetura atual é flexível e escalável, pronta para futuras expansões e adaptações. Em resumo, nossa solução proporciona uma base sólida e adaptável para sistemas de recomendação, com potencial para crescimento e otimização contínuos.
