from contextlib import asynccontextmanager
from db_connect import AsyncSessionLocal
from abc import ABC, abstractmethod
from typing import Type, Any
from models import Base
from pydantic import BaseModel
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession


# Session generator
async def session_generator() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


# Function to get session
@asynccontextmanager
async def get_session() -> AsyncSession:
    async for session in session_generator():
        try:
            async with session.begin():
                yield session
        finally:
            await session.close()


class CRUDSettings(ABC):
    """ Every child class must contain his SQLAlchemy model to interact with her """
    __db_model = Type[Base]

    @classmethod
    @abstractmethod
    async def create(cls, database_data_model: Type[BaseModel]) -> Any:
        """ Create new record by using pydantic model """
        ...

    @classmethod
    @abstractmethod
    async def read(cls) -> Any:
        """ Create read data """
        ...

    @classmethod
    @abstractmethod
    async def delete(cls) -> Any:
        """ Delete record """
        ...
