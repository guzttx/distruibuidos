import argparse
import random
import sys
from pathlib import Path

from faker import Faker
from sqlalchemy.exc import SQLAlchemyError

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.append(str(BACKEND_DIR))

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models import Produto  # noqa: E402


CATEGORIAS = [
    "Eletronicos",
    "Informatica",
    "Casa",
    "Moveis",
    "Esportes",
    "Livros",
    "Vestuario",
    "Automotivo",
]


def gerar_produto(fake: Faker) -> dict[str, object]:
    """Gera um dicionário compatível com o modelo Produto."""

    categoria = random.choice(CATEGORIAS)
    return {
        "nome": f"{fake.word().title()} {fake.word().title()}",
        "categoria": categoria,
        "preco": round(random.uniform(10, 5000), 2),
        "estoque": random.randint(0, 1000),
        "descricao": fake.sentence(nb_words=12),
    }


def popular_banco(quantidade: int, tamanho_lote: int = 1000) -> None:
    """Insere produtos em lotes para reduzir commits e melhorar desempenho."""

    fake = Faker("pt_BR")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        for inicio in range(0, quantidade, tamanho_lote):
            tamanho_atual = min(tamanho_lote, quantidade - inicio)
            produtos = [Produto(**gerar_produto(fake)) for _ in range(tamanho_atual)]

            # Inserir em lotes evita milhares de commits individuais. Cada commit
            # força sincronização transacional com o banco, o que seria bem mais
            # lento para bases grandes como 50.000 registros.
            db.add_all(produtos)
            db.commit()
            print(f"Inseridos {inicio + tamanho_atual} de {quantidade} produtos")
    except SQLAlchemyError:
        db.rollback()
        raise
    finally:
        db.close()


def parse_args() -> argparse.Namespace:
    """Lê a quantidade de registros informada pela linha de comando."""

    parser = argparse.ArgumentParser(description="Popula o banco com produtos fake.")
    parser.add_argument("quantidade", type=int, help="Quantidade de produtos a inserir.")
    parser.add_argument(
        "--lote",
        type=int,
        default=1000,
        help="Quantidade de registros por commit. Padrão: 1000.",
    )
    return parser.parse_args()


def main() -> None:
    """Ponto de entrada do script de população."""

    args = parse_args()
    if args.quantidade <= 0:
        raise SystemExit("A quantidade precisa ser maior que zero.")
    if args.lote <= 0:
        raise SystemExit("O tamanho do lote precisa ser maior que zero.")

    popular_banco(args.quantidade, args.lote)


if __name__ == "__main__":
    main()
