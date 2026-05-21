from sqlalchemy import select
from app.database.db import SessionLocal
from app.database.models import Service, Price, Favorite


def get_services():
    with SessionLocal() as session:
        stmt = select(Service)
        services = session.scalars(stmt).all()
        return services


def get_price(service_name: str, car_model: str):
    with SessionLocal() as session:
        stmt = select(Service).where(Service.name == service_name)
        service = session.scalars(stmt).first()
        if not service:
            return []

        stmt = select(Price).where(Price.service_id == service.id, Price.car_model == car_model)
        prices = session.scalars(stmt).all()
        return prices


def add_price(service_name: str, car_model: str, price_value: int, source: str = None):
    with SessionLocal() as session:
        stmt = select(Service).where(Service.name == service_name)
        service = session.scalars(stmt).first()
        if not service:
            service = Service(name=service_name)
            session.add(service)
            session.commit()

        price = Price(car_model=car_model, service_id=service.id, price=price_value, source=source)
        session.add(price)
        session.commit()
        return price


def add_to_favorites(user_telegram_id: str, price_id: int):
    with SessionLocal() as session:
        stmt = select(Favorite).where(
            Favorite.user_telegram_id == user_telegram_id,
            Favorite.price_id == price_id
        )
        existing = session.scalars(stmt).first()
        if existing:
            return existing

        favorite = Favorite(user_telegram_id=user_telegram_id, price_id=price_id)
        session.add(favorite)
        session.commit()
        return favorite