# Como executar o projeto

Siga estes passos a partir de um clone limpo do repositório.

Instale Python (3.11 é a versão de referência), com `pip` e `venv`, e Docker com Docker Compose. No Windows/macOS, abra o Docker Desktop e aguarde o mecanismo de containers Linux iniciar. No Linux, mantenha o serviço Docker em execução. Também é necessário um navegador; não é preciso instalar Node.js ou PostgreSQL separadamente neste fluxo.

1. Verifique os pré-requisitos:

```bash
python --version
docker --version
docker compose version
docker info
```

`docker info` deve mostrar o servidor sem erro de conexão. No Linux/macOS, use `python3 --version` se o comando `python` não existir.

2. Entre na pasta do projeto:

```bash
cd distruibuidos
```

A raiz é a pasta que contém `README.md`, `docker-compose.yml`, `backend/` e `frontend/`.

3. Crie o arquivo de ambiente da API, caso ainda não exista. No PowerShell:

```powershell
Copy-Item backend/.env.example backend/.env
```

No Windows CMD:

```bat
copy backend\.env.example backend\.env
```

No Linux/macOS:

```bash
cp backend/.env.example backend/.env
```

4. Suba o PostgreSQL com Docker Compose:

```bash
docker compose up -d --wait
docker compose ps
```

Aguarde o serviço `postgres` ficar saudável antes de iniciar a API.

5. Crie o ambiente virtual Python:

```bash
cd backend
python -m venv .venv
```

No Linux/macOS, substitua `python -m venv .venv` por `python3 -m venv .venv`.

6. Ative o ambiente virtual no Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

No Windows CMD:

```bat
.venv\Scripts\activate.bat
```

No Linux/macOS:

```bash
source .venv/bin/activate
```

Se o PowerShell bloquear a ativação, use diretamente `.\.venv\Scripts\python.exe` no lugar de `python` nos próximos comandos dentro de `backend`. A ativação vale apenas para o terminal atual.

7. Instale as dependências:

```bash
python -m pip install -r requirements.txt
python -m pip check
```

8. Inicie a API FastAPI:

```bash
python -m uvicorn app.main:app --reload
```

Execute dentro de `backend`, com o ambiente virtual ativo. A API cria a tabela automaticamente ao iniciar e precisa do PostgreSQL acessível. Mantenha este terminal aberto.

9. Verifique a saúde da API em outro terminal. No PowerShell:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

No CMD ou Linux/macOS:

```bash
curl http://localhost:8000/health
```

URL do backend: `http://localhost:8000`

Health check: `http://localhost:8000/health`

Swagger/OpenAPI: `http://localhost:8000/docs`

10. Abra o frontend em outro terminal, começando na raiz do projeto. No Windows (PowerShell ou CMD):

```powershell
cd frontend
..\backend\.venv\Scripts\python.exe -m http.server 5500
```

No Linux/macOS:

```bash
cd frontend
../backend/.venv/bin/python -m http.server 5500
```

Depois acesse exatamente `http://localhost:5500`. Não abra o HTML diretamente nem use `127.0.0.1:5500` com a configuração padrão: são origens diferentes para o CORS.

11. Teste o CRUD pela interface ou pelo Swagger.

12. Para popular o banco, abra outro terminal na raiz do projeto e siga [Como Popular o Banco](#como-popular-o-banco). Use o Python da `.venv` para que o script encontre o Faker e as demais dependências.

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

Exemplo de criação no PowerShell:

```powershell
$body = @{ nome = "Notebook"; categoria = "Informatica"; preco = 3500.00; estoque = 10; descricao = "Notebook para estudos" } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/produtos -Method Post -ContentType "application/json" -Body $body
```

No Windows CMD:

```bat
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

O modelo declara a chave primária e um índice adicional em `id` (`ix_produtos_id`, por causa de `index=True`). Não declara índices nos filtros por `categoria`, `preco` ou `categoria + preco`, permitindo comparar futuramente seu impacto.

Consultas úteis para experimentos futuros:

```sql
EXPLAIN ANALYZE SELECT * FROM produtos WHERE categoria = 'Informatica';
EXPLAIN ANALYZE SELECT * FROM produtos WHERE preco BETWEEN 100 AND 500;
EXPLAIN ANALYZE SELECT * FROM produtos WHERE categoria = 'Casa' AND preco BETWEEN 100 AND 500;
```

## Como Popular o Banco

O script `scripts/populate_database.py` usa Faker para gerar nomes, descrições, preços, estoques e categorias controladas.

Com o PostgreSQL funcionando, execute a partir da raiz do projeto (a pasta que contém `backend` e `scripts`). Os comandos abaixo usam diretamente o Python do ambiente virtual, sem depender da ativação no terminal.

No Windows PowerShell ou CMD, comece com poucos registros:

```powershell
.\backend\.venv\Scripts\python.exe scripts/populate_database.py 100
```

No Linux/macOS:

```bash
./backend/.venv/bin/python scripts/populate_database.py 100
```

Para volumes maiores, substitua `100` por `20000` ou `50000`. Cada execução **adiciona** a quantidade informada; não apaga registros anteriores nem ajusta o total do banco.

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

Remover o volume apaga os dados do PostgreSQL. Depois disso, a partir da raiz e com o ambiente virtual ativo, suba novamente o banco e execute a API para recriar a tabela:

```bash
docker compose up -d --wait
cd backend
python -m uvicorn app.main:app --reload
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

Além dos índices em `id` descritos acima, os índices de filtros poderão ser criados de forma controlada para comparar desempenho antes e depois:

```sql
CREATE INDEX idx_produtos_categoria ON produtos (categoria);
CREATE INDEX idx_produtos_preco ON produtos (preco);
CREATE INDEX idx_produtos_categoria_preco ON produtos (categoria, preco);
```

Esses índices não foram aplicados agora para preservar uma linha de base simples nos experimentos.

## Solução de Problemas

- PostgreSQL não iniciou: verifique `docker compose ps` e `docker compose logs postgres`.
- Erro de conexão com `dockerDesktopLinuxEngine`: abra o Docker Desktop, aguarde o mecanismo iniciar e verifique `docker info`.
- Porta 5432 ocupada: altere a porta publicada no `docker-compose.yml` e a porta em `DATABASE_URL` no `backend/.env`, ou pare o serviço conflitante. Alterar apenas `POSTGRES_PORT` não muda a conexão da API.
- FastAPI não conecta ao banco: confirme se `backend/.env` existe e se o container está saudável.
- Frontend recebe erro de CORS: confira se `FRONTEND_ORIGIN` em `backend/.env` corresponde à URL usada no navegador.
- Ambiente virtual não está ativado: ative a `.venv` antes de instalar dependências ou iniciar a API.
- `ModuleNotFoundError: No module named 'faker'`: use o comando com o Python da `.venv` na seção [Como Popular o Banco](#como-popular-o-banco). Se persistir, na raiz execute `.\backend\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt` no Windows, ou `./backend/.venv/bin/python -m pip install -r backend/requirements.txt` no Linux/macOS.
- Outra dependência ausente: dentro de `backend`, com a `.venv` ativa, execute `python -m pip install -r requirements.txt`.
- Banco ainda não possui tabela: inicie a API uma vez; ela executa `Base.metadata.create_all`.
- Arquivo `.env` ausente: copie `backend/.env.example` para `backend/.env`.
