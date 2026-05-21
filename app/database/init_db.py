from sqlalchemy import inspect

from app.database.db import engine
from app.database.models import Base, Favorite


def init_db() -> None:
    _recreate_legacy_favorites_table()
    Base.metadata.create_all(bind=engine)


def _recreate_legacy_favorites_table() -> None:
    inspector = inspect(engine)
    if "favorites" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("favorites")}
    if "price_id" not in columns:
        return

    Favorite.__table__.drop(bind=engine, checkfirst=True)


if __name__ == "__main__":
    init_db()
    print("Таблицы созданы (если их не было).")
