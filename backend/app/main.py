from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.database import Base, check_database_connection, engine, settings
from app.routes import produtos

# create_all cria as tabelas mapeadas pelos modelos quando a aplicação sobe.
# Para um projeto acadêmico inicial isso simplifica a execução. Em sistemas de
# produção, migrações versionadas com Alembic costumam ser preferíveis.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Catálogo de Produtos",
    description="CRUD acadêmico com FastAPI, SQLAlchemy e PostgreSQL.",
    version="1.0.0",
)

# O CORS permite que o frontend estático, servido em outra origem/porta, chame
# a API no navegador. A origem fica configurável para evitar liberar tudo com *.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)

app.include_router(produtos.router)


@app.get("/health")
def health() -> dict[str, str]:
    """Verifica se a API está no ar e se consegue falar com o PostgreSQL."""

    try:
        check_database_connection()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API iniciou, mas não conseguiu conectar ao PostgreSQL.",
        ) from exc

    return {"status": "ok", "database": "connected"}
