from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/produtos", tags=["produtos"])


@router.post(
    "",
    response_model=schemas.ProdutoResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_produto(
    produto: schemas.ProdutoCreate,
    db: Session = Depends(get_db),
) -> schemas.ProdutoResponse:
    """Recebe JSON validado pelo Pydantic e cadastra um produto."""

    try:
        return crud.create_produto(db, produto)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao salvar produto no banco de dados.",
        ) from exc


@router.get("/{produto_id}", response_model=schemas.ProdutoResponse)
def obter_produto(
    produto_id: int,
    db: Session = Depends(get_db),
) -> schemas.ProdutoResponse:
    """Retorna um produto específico ou HTTP 404 quando ele não existe."""

    produto = crud.get_produto(db, produto_id)
    if produto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )
    return produto


@router.get("", response_model=schemas.ProdutoListResponse)
def listar_produtos(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100),
    categoria: str | None = Query(default=None),
    preco_min: Decimal | None = Query(default=None, ge=0),
    preco_max: Decimal | None = Query(default=None, ge=0),
    db: Session = Depends(get_db),
) -> schemas.ProdutoListResponse:
    """Lista produtos de forma paginada, com filtros úteis para experimentos."""

    if preco_min is not None and preco_max is not None and preco_min > preco_max:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="preco_min não pode ser maior que preco_max.",
        )

    produtos, total = crud.list_produtos(
        db=db,
        page=page,
        limit=limit,
        categoria=categoria,
        preco_min=preco_min,
        preco_max=preco_max,
    )
    return schemas.ProdutoListResponse(
        page=page,
        limit=limit,
        total=total,
        items=produtos,
    )


@router.put("/{produto_id}", response_model=schemas.ProdutoResponse)
def atualizar_produto(
    produto_id: int,
    produto_update: schemas.ProdutoUpdate,
    db: Session = Depends(get_db),
) -> schemas.ProdutoResponse:
    """Atualiza um produto existente usando os campos enviados no corpo."""

    try:
        produto = crud.update_produto(db, produto_id, produto_update)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar produto no banco de dados.",
        ) from exc

    if produto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )
    return produto


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_produto(
    produto_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Exclui um produto ou retorna HTTP 404 caso ele não exista."""

    try:
        deleted = crud.delete_produto(db, produto_id)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao excluir produto no banco de dados.",
        ) from exc

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )
