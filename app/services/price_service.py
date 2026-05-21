from sqlalchemy import select, update

from app.database.db import SessionLocal
from app.database.models import Favorite, Price, Service

DEFAULT_SERVICES = [
    "Заміна оливи",
    "Діагностика",
    "Заміна гальмівних колодок",
    "Заміна свічок",
]

LEGACY_SERVICE_RENAMES = {
    "Замена масла": "Заміна оливи",
    "Диагностика": "Діагностика",
    "Замена тормозных колодок": "Заміна гальмівних колодок",
    "Замена свечей": "Заміна свічок",
}


def ensure_default_services() -> None:
    with SessionLocal() as session:
        services = session.scalars(select(Service)).all()
        services_by_name = {service.name: service for service in services}

        for old_name, new_name in LEGACY_SERVICE_RENAMES.items():
            old_service = services_by_name.get(old_name)
            if not old_service:
                continue

            new_service = services_by_name.get(new_name)
            if new_service and new_service.id != old_service.id:
                session.execute(
                    update(Price)
                    .where(Price.service_id == old_service.id)
                    .values(service_id=new_service.id)
                )
                session.execute(
                    update(Favorite)
                    .where(Favorite.service_id == old_service.id)
                    .values(service_id=new_service.id)
                )
                session.delete(old_service)
                services_by_name.pop(old_name, None)
                continue

            old_service.name = new_name
            services_by_name.pop(old_name, None)
            services_by_name[new_name] = old_service

        for service_name in DEFAULT_SERVICES:
            if service_name not in services_by_name:
                session.add(Service(name=service_name))
                services_by_name[service_name] = True
        session.commit()


def get_services():
    with SessionLocal() as session:
        stmt = select(Service).order_by(Service.name)
        return session.scalars(stmt).all()


def get_service_by_id(service_id: int):
    with SessionLocal() as session:
        stmt = select(Service).where(Service.id == service_id)
        return session.scalars(stmt).first()


def get_prices_for_service(service_id: int, car_model: str):
    with SessionLocal() as session:
        stmt = (
            select(Price)
            .where(Price.service_id == service_id, Price.car_model == car_model)
            .order_by(Price.price.asc())
        )
        return session.scalars(stmt).all()


def add_price(service_id: int, car_model: str, price_value: int, source: str | None = None):
    with SessionLocal() as session:
        price = Price(
            car_model=car_model,
            service_id=service_id,
            price=price_value,
            source=source,
        )
        session.add(price)
        session.commit()
        session.refresh(price)
        return price


def ensure_stub_prices(service_id: int, car_model: str):
    prices = get_prices_for_service(service_id=service_id, car_model=car_model)
    if prices:
        return prices

    add_price(service_id, car_model, 140, "independent-garage")
    add_price(service_id, car_model, 150, "bmw-official")
    add_price(service_id, car_model, 170, "service-partner")
    return get_prices_for_service(service_id=service_id, car_model=car_model)
