from abc import ABC, abstractmethod
from typing import Type, Any
from uuid import UUID

from fastapi.security import OAuth2PasswordRequestForm

from .models import Base, User, Product, Category, Basket
from pydantic import BaseModel
import sqlalchemy as _sql
from fastapi.exceptions import HTTPException
from routers.schemas import (UserReadSchema,
                                 UserCreateSchema,
                                 UserDatabaseSchema,
                                 CategoryReadSchema,
                                 CategoryCreateSchema,
                                 ProductCreateSchema,
                                 ProductReadSchema,
                                 BasketCreateSchema,
                                 BasketReadSchema, UserAuthScheme, )
from dependencies import get_session, get_password_hash, verify_password

############################################################################
#              Abstract class to give an example for child class           #
############################################################################

class BaseCRUD(ABC):
    """ Every child class must contain his SQLAlchemy model to interact with her """
    __db_model = Type[Base]

    @classmethod
    @abstractmethod
    async def create(cls, pydantic_schema: Type[BaseModel]) -> Any:
        """ Create new record by using pydantic model """
        ...

    @classmethod
    @abstractmethod
    async def read(cls, **kwargs) -> Any:
        """ Read record """
        ...

    @classmethod
    @abstractmethod
    async def delete(cls, **kwargs) -> Any:
        """ Delete record """
        ...


class UserCRUD(BaseCRUD):
    """ Controlling interaction with User """
    __db_model = User

    @classmethod
    async def create(cls, user_create_schema: UserCreateSchema) -> UserDatabaseSchema:
        async with get_session() as session:
            stmt = _sql.select(cls.__db_model).where(cls.__db_model.username == user_create_schema.username)
            result = await session.execute(stmt)
            existing_user = result.scalars().first()
            if existing_user:
                raise HTTPException(status_code=422, detail='Username already exists')
            hashed_password = get_password_hash(user_create_schema.password)
            user_database_schema = UserDatabaseSchema(**user_create_schema.dict(), hashed_password=hashed_password)
            new_user = cls.__db_model(
                **user_database_schema.dict(),
            )
            session.add(new_user)
            await session.commit()
            return user_database_schema

    @classmethod
    async def read(cls, user_id: UUID | None, username: str | None) -> UserReadSchema | None:
        async with get_session() as session:
            if user_id or username:
                stmt = _sql.select(cls.__db_model).where(_sql.or_(cls.__db_model.username == username, cls.__db_model.id == user_id))
            else:
                return None
            result = await session.execute(stmt)
            user = result.scalars().first()
            if user is None:
                return user
            return user

    @classmethod
    async def delete(cls, user_id: UUID) -> UserReadSchema | None:
        async with get_session() as session:
            stmt = _sql.select(cls.__db_model).where(cls.__db_model.id == user_id)
            result = await session.execute(stmt)
            user = result.scalars().first()
            if user is None:
                return user
            delete_stmt = _sql.delete(cls.__db_model).where(cls.__db_model.id == user_id)
            await session.execute(delete_stmt)
            return user

    @classmethod
    async def get_all_users(cls):
        async with get_session() as session:
            stmt = _sql.select(cls.__db_model)
            result = await session.execute(stmt)
            users = result.scalars().all()
            return users

    @classmethod
    async def verify_user(cls, user_data: OAuth2PasswordRequestForm) -> UserReadSchema | None:
        async with get_session() as session:
            stmt = _sql.select(cls.__db_model).where(cls.__db_model.username == user_data.username)
            result = await session.execute(stmt)
            user: User = result.scalars().first()
            if not user:
                return None
            verify: bool = verify_password(password=user_data.password, hashed_password=user.hashed_password)
            if not verify:
                raise HTTPException(status_code=401, detail='Incorrect password')
            return user
