from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProdutoBase(BaseModel):
    """Campos compartilhados pelos schemas de criação, edição e resposta."""

    nome: str = Field(..., min_length=1, max_length=150)
    categoria: str = Field(..., min_length=1, max_length=80)
    preco: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    estoque: int = Field(..., ge=0)
    descricao: str | None = None


class ProdutoCreate(ProdutoBase):
    """Schema usado para validar os dados recebidos no POST /produtos."""


class ProdutoUpdate(BaseModel):
    """Schema usado no PUT permitindo atualizar apenas os campos enviados."""

    nome: str | None = Field(default=None, min_length=1, max_length=150)
    categoria: str | None = Field(default=None, min_length=1, max_length=80)
    preco: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    estoque: int | None = Field(default=None, ge=0)
    descricao: str | None = None


class ProdutoResponse(ProdutoBase):
    """Schema devolvido pela API.

    ConfigDict(from_attributes=True) permite converter objetos SQLAlchemy para
    JSON validado pelo Pydantic sem montar dicionários manualmente.
    """

    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProdutoListResponse(BaseModel):
    """Resposta paginada para evitar retorno acidental de milhares de linhas."""

    page: int
    limit: int
    total: int
    items: list[ProdutoResponse]
