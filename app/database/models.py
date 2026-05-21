from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base


class Service(Base):
    __tablename__ = 'services'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

class Price(Base):
    __tablename__ = 'prices'
    id = Column(Integer, primary_key=True, index=True)
    car_model = Column(String, nullable=False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    price = Column(Integer, nullable=False)
    source = Column(String)

class Favorite(Base):
    __tablename__ = 'favorites'
    id = Column(Integer, primary_key=True, index=True)
    user_telegram_id = Column(String, nullable=False)
    price_id = Column(Integer, ForeignKey('prices.id'), nullable=False)

    price = relationship("Price")
