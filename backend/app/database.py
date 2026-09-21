from collections.abc import Generator
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


class Settings(BaseSettings):
    """Representa as configurações externas da aplicação.

    A API lê variáveis de ambiente para evitar credenciais hardcoded no código.
    Em desenvolvimento, o arquivo backend/.env pode fornecer esses valores.
    """

    database_url: str
    frontend_origin: str = "http://localhost:5500"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Carrega as configurações uma única vez durante o ciclo de vida da API."""

    return Settings()


settings = get_settings()

# O engine é o ponto central de comunicação entre SQLAlchemy e PostgreSQL.
# Ele não representa uma conexão única: internamente mantém um pool de conexões
# reutilizáveis para reduzir o custo de abrir e fechar conexões a cada requisição.
engine = create_engine(
    settings.database_url,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

# SessionLocal é uma fábrica de sessões. Cada sessão representa uma unidade de
# trabalho com o banco: consultas, alterações, commit ou rollback.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base usada pelos modelos SQLAlchemy para mapear classes em tabelas."""


def get_db() -> Generator[Session, None, None]:
    """Entrega uma sessão para a rota FastAPI e garante seu fechamento.

    O FastAPI executa o código até o yield antes da rota e finaliza o bloco
    depois da resposta, fechando a conexão devolvida ao pool.
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> bool:
    """Executa uma consulta simples para validar a conexão com PostgreSQL."""

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True
