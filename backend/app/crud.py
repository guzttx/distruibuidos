from decimal import Decimal

from sqlalchemy import Select, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app import models, schemas


def create_produto(db: Session, produto: schemas.ProdutoCreate) -> models.Produto:
    """Cria um produto e confirma a transação no banco."""

    db_produto = models.Produto(**produto.model_dump())
    try:
        db.add(db_produto)
        # commit confirma a transação; sem ele a linha não é persistida.
        db.commit()
        # refresh recarrega campos gerados pelo banco, como id e created_at.
        db.refresh(db_produto)
        return db_produto
    except SQLAlchemyError:
        # rollback desfaz a transação quando algum erro ocorre durante a escrita.
        db.rollback()
        raise


def get_produto(db: Session, produto_id: int) -> models.Produto | None:
    """Busca um produto pela chave primária."""

    return db.get(models.Produto, produto_id)


def _apply_filters(
    statement: Select[tuple[models.Produto]] | Select[tuple[int]],
    categoria: str | None,
    preco_min: Decimal | None,
    preco_max: Decimal | None,
) -> Select[tuple[models.Produto]] | Select[tuple[int]]:
    """Aplica filtros reutilizados pela consulta de dados e pela contagem."""

    if categoria:
        statement = statement.where(models.Produto.categoria == categoria)
    if preco_min is not None:
        statement = statement.where(models.Produto.preco >= preco_min)
    if preco_max is not None:
        statement = statement.where(models.Produto.preco <= preco_max)
    return statement


def list_produtos(
    db: Session,
    page: int,
    limit: int,
    categoria: str | None = None,
    preco_min: Decimal | None = None,
    preco_max: Decimal | None = None,
) -> tuple[list[models.Produto], int]:
    """Lista produtos com paginação e filtros opcionais."""

    offset = (page - 1) * limit

    query = select(models.Produto).order_by(models.Produto.id)
    query = _apply_filters(query, categoria, preco_min, preco_max)

    count_query = select(func.count()).select_from(models.Produto)
    count_query = _apply_filters(count_query, categoria, preco_min, preco_max)

    total = db.scalar(count_query) or 0
    produtos = db.scalars(query.offset(offset).limit(limit)).all()
    return list(produtos), total


def update_produto(
    db: Session,
    produto_id: int,
    produto_update: schemas.ProdutoUpdate,
) -> models.Produto | None:
    """Atualiza um produto existente e retorna None quando ele não existe."""

    db_produto = get_produto(db, produto_id)
    if db_produto is None:
        return None

    update_data = produto_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_produto, field, value)

    try:
        db.commit()
        db.refresh(db_produto)
        return db_produto
    except SQLAlchemyError:
        db.rollback()
        raise


def delete_produto(db: Session, produto_id: int) -> bool:
    """Remove um produto e informa se a exclusão aconteceu."""

    db_produto = get_produto(db, produto_id)
    if db_produto is None:
        return False

    try:
        db.delete(db_produto)
        db.commit()
        return True
    except SQLAlchemyError:
        db.rollback()
        raise
