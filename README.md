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

## Conclusão
