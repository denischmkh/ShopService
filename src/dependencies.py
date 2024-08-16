# Session generator
import uuid
from contextlib import asynccontextmanager
from datetime import timedelta, datetime, timezone
from typing import AsyncGenerator

import jwt
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.sql_app.db_connect import AsyncSessionLocal

from passlib.context import CryptContext

from .config import JWT_SECRET_TOKEN


####################################################
#              Depends functions                   #
####################################################

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def session_generator() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


# Context manager to get session
@asynccontextmanager
async def get_session() -> AsyncSession:
    async for session in session_generator():
        try:
            async with session.begin():
                yield session
        finally:
            await session.close()


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

class JWT_data(BaseModel):
    id: str
    username: str

def create_access_token(data: JWT_data, expires_delta: timedelta | None = None):
    data = data.dict()
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_TOKEN, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(access_token: str) -> dict:
    decode_token = jwt.decode(access_token, JWT_SECRET_TOKEN, algorithms=[ALGORITHM])
    return decode_token