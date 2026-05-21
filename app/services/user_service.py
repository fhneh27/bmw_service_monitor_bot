from sqlalchemy import select
from app.database.db import SessionLocal
from app.database.models import User


def get_or_create_user(
    telegram_id: int,
    username: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
) -> User:
    tg_id = str(telegram_id)

    with SessionLocal() as session:
        stmt = select(User).where(User.telegram_id == tg_id)
        user = session.scalars(stmt).first()

        if user:
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            session.commit()
            session.refresh(user)
            return user

        user = User(
            telegram_id=tg_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def get_user_by_telegram_id(telegram_id: int) -> User | None:
    with SessionLocal() as session:
        stmt = select(User).where(User.telegram_id == str(telegram_id))
        return session.scalars(stmt).first()