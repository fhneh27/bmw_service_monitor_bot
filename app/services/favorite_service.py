from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.database.db import SessionLocal
from app.database.models import Favorite


def add_favorite(user_id: int, service_id: int, car_model: str):
    normalized_car_model = car_model.strip()

    with SessionLocal() as session:
        stmt = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.service_id == service_id,
            Favorite.car_model == normalized_car_model,
        )
        existing = session.scalars(stmt).first()
        if existing:
            return existing, False

        favorite = Favorite(
            user_id=user_id,
            service_id=service_id,
            car_model=normalized_car_model,
        )
        session.add(favorite)
        session.commit()
        session.refresh(favorite)
        return favorite, True


def get_favorite_by_triplet(user_id: int, service_id: int, car_model: str):
    normalized_car_model = car_model.strip()

    with SessionLocal() as session:
        stmt = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.service_id == service_id,
            Favorite.car_model == normalized_car_model,
        )
        return session.scalars(stmt).first()


def get_favorites_for_user(user_id: int):
    with SessionLocal() as session:
        stmt = (
            select(Favorite)
            .options(selectinload(Favorite.service))
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
        )
        return session.scalars(stmt).all()


def get_favorite_for_user(favorite_id: int, user_id: int):
    with SessionLocal() as session:
        stmt = (
            select(Favorite)
            .options(selectinload(Favorite.service))
            .where(Favorite.id == favorite_id, Favorite.user_id == user_id)
        )
        return session.scalars(stmt).first()


def remove_favorite(favorite_id: int, user_id: int) -> bool:
    with SessionLocal() as session:
        stmt = select(Favorite).where(Favorite.id == favorite_id, Favorite.user_id == user_id)
        favorite = session.scalars(stmt).first()
        if not favorite:
            return False

        session.delete(favorite)
        session.commit()
        return True


def remove_favorite_by_triplet(user_id: int, service_id: int, car_model: str) -> bool:
    with SessionLocal() as session:
        stmt = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.service_id == service_id,
            Favorite.car_model == car_model.strip(),
        )
        favorite = session.scalars(stmt).first()
        if not favorite:
            return False

        session.delete(favorite)
        session.commit()
        return True


def clear_favorites_for_user(user_id: int) -> int:
    with SessionLocal() as session:
        stmt = select(Favorite).where(Favorite.user_id == user_id)
        favorites = session.scalars(stmt).all()
        if not favorites:
            return 0

        removed_count = len(favorites)
        for favorite in favorites:
            session.delete(favorite)
        session.commit()
        return removed_count


def get_favorites_count(user_id: int) -> int:
    with SessionLocal() as session:
        stmt = select(func.count(Favorite.id)).where(Favorite.user_id == user_id)
        return session.scalar(stmt) or 0
