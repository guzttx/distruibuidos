# Como executar o projeto

Siga estes passos a partir de um clone limpo do repositório.

1. Verifique os pré-requisitos:

```bash
python --version
docker --version
docker compose version
```

2. Entre na pasta do projeto:

```bash
cd distribuidos
```

3. Crie o arquivo de ambiente da API:

```bash
copy backend\.env.example backend\.env
```

No Linux/macOS:

```bash
cp backend/.env.example backend/.env
```

4. Suba o PostgreSQL com Docker Compose:

```bash
docker compose up -d
```

5. Crie o ambiente virtual Python:

```bash
cd backend
python -m venv .venv
```

6. Ative o ambiente virtual no Windows:

```bash
.venv\Scripts\activate
```

No Linux/macOS:

```bash
source .venv/bin/activate
```

7. Instale as dependências:

```bash
pip install -r requirements.txt
```

8. Inicie a API FastAPI:

```bash
uvicorn app.main:app --reload
```

9. Verifique a saúde da API:

```bash
curl http://localhost:8000/health
```

URL do backend: `http://localhost:8000`

Health check: `http://localhost:8000/health`

Swagger/OpenAPI: `http://localhost:8000/docs`

10. Abra o frontend em outro terminal:

```bash
cd frontend
python -m http.server 5500
```

Depois acesse `http://localhost:5500`.

11. Teste o CRUD pela interface ou pelo Swagger.

12. Quando quiser popular o banco com dados fake, execute a partir da raiz do projeto:

```bash
python scripts/populate_database.py 100
```

Para o volume mínimo esperado no trabalho:

```bash
python scripts/populate_database.py 50000
```

## Sobre o Projeto

Este projeto é uma aplicação CRUD de catálogo de produtos para uma loja virtual. Ele foi estruturado para apoiar um trabalho acadêmico de Sistemas Distribuídos/Banco de Dados e servir como base para testes de desempenho com múltiplos clientes simultâneos.

O foco inicial é deixar banco, API e frontend funcionando de forma simples, reprodutível e fácil de explicar.

## Arquitetura

O fluxo principal é:

```text
Cliente HTML/CSS/JavaScript
-> HTTP/JSON
-> FastAPI
-> SQLAlchemy
-> PostgreSQL
```

O frontend executa requisições HTTP usando `fetch()`. A API FastAPI valida os dados com Pydantic, chama a camada CRUD, e o SQLAlchemy traduz operações Python em consultas SQL para o PostgreSQL.

O Apache JMeter entrará posteriormente chamando diretamente a API FastAPI, sem passar pelo frontend, para medir latência, vazão e comportamento sob concorrência.

## Tecnologias Utilizadas

- Python: linguagem usada no backend e no script de geração de dados.
- FastAPI: framework HTTP da API.
- SQLAlchemy: ORM responsável pelo mapeamento entre classes Python e tabelas.
- PostgreSQL: banco relacional da aplicação.
- psycopg: driver usado pelo SQLAlchemy para conversar com PostgreSQL.
- Docker Compose: usado inicialmente para executar apenas o PostgreSQL.
- HTML/CSS/JavaScript: frontend sem frameworks.
- Faker: geração de dados de teste.
- Apache JMeter: ferramenta planejada para testes de carga.

## Estrutura de Diretórios

```text
.
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── crud.py
│   │   └── routes/
│   │       └── produtos.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── scripts/
│   └── populate_database.py
├── jmeter/
├── resultados/
├── docker-compose.yml
├── .gitignore
└── README.md
```

`backend/app/database.py` concentra a configuração do SQLAlchemy, engine, pool de conexões e sessões. `models.py` define a tabela `produtos`. `schemas.py` define validações de entrada e formatos de resposta. `crud.py` contém operações de banco. `routes/produtos.py` expõe os endpoints HTTP.

## Como o Sistema Funciona

1. O usuário executa uma ação no navegador, como cadastrar ou excluir um produto.
2. O JavaScript lê o formulário ou o botão clicado.
3. O JavaScript envia uma requisição HTTP com `fetch()`.
4. O FastAPI recebe a requisição e valida os dados com Pydantic.
5. A rota chama uma função da camada CRUD.
6. O SQLAlchemy usa uma sessão para executar a operação no PostgreSQL.
7. O PostgreSQL retorna os dados.
8. O FastAPI serializa a resposta em JSON.
9. O JavaScript recebe o JSON e atualiza o DOM.

Esse fluxo separa responsabilidades: navegador cuida da interface, API cuida das regras HTTP e validação, ORM cuida do acesso ao banco, e PostgreSQL persiste os dados.

## Endpoints da API

| Método | Caminho | Descrição |
| --- | --- | --- |
| GET | `/health` | Verifica API e conexão com banco |
| POST | `/produtos` | Cria produto |
| GET | `/produtos/{id}` | Busca produto por ID |
| GET | `/produtos?page=1&limit=50` | Lista produtos com paginação |
| PUT | `/produtos/{id}` | Atualiza produto |
| DELETE | `/produtos/{id}` | Remove produto |

Exemplo de criação:

```bash
curl -X POST http://localhost:8000/produtos ^
  -H "Content-Type: application/json" ^
  -d "{\"nome\":\"Notebook\",\"categoria\":\"Informatica\",\"preco\":3500.00,\"estoque\":10,\"descricao\":\"Notebook para estudos\"}"
```

No Linux/macOS:

```bash
curl -X POST http://localhost:8000/produtos \
  -H "Content-Type: application/json" \
  -d '{"nome":"Notebook","categoria":"Informatica","preco":3500.00,"estoque":10,"descricao":"Notebook para estudos"}'
```

Exemplos de filtros:

```bash
curl "http://localhost:8000/produtos?categoria=Eletronicos"
curl "http://localhost:8000/produtos?preco_min=100&preco_max=500"
curl "http://localhost:8000/produtos?page=2&limit=50"
```

O limite máximo por página é 100 para impedir que uma chamada simples retorne dezenas de milhares de registros.

## Banco de Dados

A tabela `produtos` possui:

| Campo | Tipo | Observação |
| --- | --- | --- |
| id | inteiro | chave primária, auto incremento |
| nome | string | obrigatório |
| categoria | string | obrigatório |
| preco | decimal | obrigatório, não negativo |
| estoque | inteiro | obrigatório, não negativo |
| descricao | texto | opcional |
| created_at | timestamp | preenchido pelo banco |

Inicialmente o projeto usa apenas o índice da chave primária. Isso permite comparar futuramente o impacto de índices adicionais em filtros por `categoria`, `preco` e `categoria + preco`.

Consultas úteis para experimentos futuros:

```sql
EXPLAIN ANALYZE SELECT * FROM produtos WHERE categoria = 'Informatica';
EXPLAIN ANALYZE SELECT * FROM produtos WHERE preco BETWEEN 100 AND 500;
EXPLAIN ANALYZE SELECT * FROM produtos WHERE categoria = 'Casa' AND preco BETWEEN 100 AND 500;
```

## Como Popular o Banco

O script `scripts/populate_database.py` usa Faker para gerar nomes, descrições, preços, estoques e categorias controladas.

Execute com poucos registros primeiro:

```bash
python scripts/populate_database.py 100
```

Depois teste volumes maiores:

```bash
python scripts/populate_database.py 20000
python scripts/populate_database.py 50000
```

O script insere em lotes porque milhares de commits individuais tornam a carga mais lenta. Com lotes, várias linhas são confirmadas em uma mesma transação, reduzindo o custo de comunicação e sincronização com o banco.

## Como Verificar os Dados

Entre no container do PostgreSQL:

```bash
docker exec -it catalogo_produtos_postgres psql -U catalogo_user -d catalogo_produtos
```

Conte os produtos:

```sql
SELECT COUNT(*) FROM produtos;
```

Liste algumas linhas:

```sql
SELECT id, nome, categoria, preco, estoque FROM produtos ORDER BY id LIMIT 10;
```

## Como Resetar o Banco

Para parar os containers sem apagar dados:

```bash
docker compose down
```

Para apagar também o volume persistente:

```bash
docker compose down -v
```

Remover o volume apaga os dados do PostgreSQL. Depois disso, suba novamente o banco e execute a API para recriar a tabela:

```bash
docker compose up -d
cd backend
uvicorn app.main:app --reload
```

## Testes de Desempenho

A pasta `jmeter/` está preparada para receber planos de teste. Os cenários previstos são:

- Cenário A: 50% leitura e 50% escrita.
- Cenário B: 75% leitura e 25% escrita.
- Cenário C: 25% leitura e 75% escrita.

Uma distribuição futura aceitável é:

- Cenário A: 50% GET, 25% POST, 20% PUT, 5% DELETE.
- Cenário B: 75% GET, 10% POST, 10% PUT, 5% DELETE.
- Cenário C: 25% GET, 30% POST, 35% PUT, 10% DELETE.

Os resultados reais devem ser armazenados em `resultados/`. Não há resultados simulados no projeto.

## Índices e Experimentos Futuros

Na primeira fase, apenas a chave primária recebe índice automaticamente. Em uma etapa posterior, os índices poderão ser criados de forma controlada para comparar desempenho antes e depois:

```sql
CREATE INDEX idx_produtos_categoria ON produtos (categoria);
CREATE INDEX idx_produtos_preco ON produtos (preco);
CREATE INDEX idx_produtos_categoria_preco ON produtos (categoria, preco);
```

Esses índices não foram aplicados agora para preservar uma linha de base simples nos experimentos.

## Solução de Problemas

- PostgreSQL não iniciou: verifique `docker compose ps` e `docker compose logs postgres`.
- Porta 5432 ocupada: altere o mapeamento de porta no `docker-compose.yml` ou pare o serviço conflitante.
- FastAPI não conecta ao banco: confirme se `backend/.env` existe e se o container está saudável.
- Frontend recebe erro de CORS: confira se `FRONTEND_ORIGIN` em `backend/.env` corresponde à URL usada no navegador.
- Ambiente virtual não está ativado: ative a `.venv` antes de instalar dependências ou iniciar a API.
- Dependência ausente: execute `pip install -r backend/requirements.txt` dentro do ambiente virtual.
- Banco ainda não possui tabela: inicie a API uma vez; ela executa `Base.metadata.create_all`.
- Arquivo `.env` ausente: copie `backend/.env.example` para `backend/.env`.
