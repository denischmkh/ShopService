from datetime import datetime
from datetime import timedelta
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, UUID, Integer, String, Boolean, DateTime, DECIMAL

from routers.email.constants import VERIFY_CODE_EXPIRE_DAYS

Base = declarative_base()


class User(Base):
    """ Users Table """
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    username = Column(String(length=30), nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    admin = Column(Boolean, nullable=True)
    active = Column(Boolean)
    email = Column(String, nullable=False)
    verified_email = Column(Boolean)
    created_at = Column(DateTime)

    def to_dict(self):
        return {
            'id': str(self.id),  # Convert UUID to string
            'username': self.username,
            'hashed_password': self.hashed_password,
            'admin': self.admin,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Category(Base):
    """ Categorys Table """
    __tablename__ = 'categories'
    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    title = Column(String(length=30), nullable=False)
    created_at = Column(DateTime)


class Product(Base):
    """ Products Table """
    __tablename__ = 'store'
    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    title = Column(String(length=30), nullable=False)
    description = Column(String(length=300), nullable=True)
    price = Column(DECIMAL(9, 2), nullable=False)
    image = Column(String, unique=True, nullable=True)  # Link to image in static files with store
    discount = Column(Integer, nullable=True)  # Discount for price
    created_at = Column(DateTime)
    categories_id = Column(UUID(as_uuid=True), nullable=True)


class Basket(Base):
    """ Basket Table """
    __tablename__ = 'baskets'
    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    products_id = Column(UUID(as_uuid=True))  # ID from "store" table
    users_id = Column(UUID(as_uuid=True))  # ID from "users" table
    quantity = Column(Integer(), nullable=False)  # Product quantity in user basket


class VerificationCode(Base):
    """ Codes to verify email """
    __tablename__ = 'verification_codes'
    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False)
    verify_code = Column(DECIMAL(6), nullable=False)
    users_id = Column(UUID)
    expire_to = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=VERIFY_CODE_EXPIRE_DAYS))
