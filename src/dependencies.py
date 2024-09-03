from contextlib import asynccontextmanager
from datetime import timedelta, datetime, timezone
from typing import AsyncGenerator, Annotated

import jwt
from fastapi import HTTPException, Depends, Form
from jwt.exceptions import ExpiredSignatureError
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

import config
from routers.schemas import UserCreateSchema
from sql_app.db_connect import AsyncSessionLocal

from passlib.context import CryptContext

from config import JWT_SECRET_TOKEN

####################################################
#              Depends functions                   #
####################################################

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1

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


class Token_Scheme(BaseModel):
    access_token: str
    token_type: str = 'Bearer'


def create_access_token(data: JWT_data, expires_delta: timedelta | None = None):
    data = data.dict()
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_TOKEN, algorithm=ALGORITHM)
    token_scheme = Token_Scheme(access_token=encoded_jwt)
    return token_scheme


def decode_token(access_token: str) -> dict | None:
    try:
        decode_token = jwt.decode(access_token, JWT_SECRET_TOKEN, algorithms=[ALGORITHM])
        return decode_token
    except ExpiredSignatureError:
        return None


def create_user_form(username: str = Form(description='Username'),
                     password1: str = Form(description='Password'),
                     password2: str = Form(description='Repeat password'),
                     Admin_key: Annotated[str | None, Form(description='Admin Key')] = None) -> UserCreateSchema:
    if password1 != password2:
        raise HTTPException(status_code=401, detail='Second password incorrect!')
    elif not Admin_key:
        user_create_schema = UserCreateSchema(username=username, password=password1, admin=False)
        return user_create_schema
    elif Admin_key != config.ADMIN_SECRET:
        raise HTTPException(status_code=401, detail='Incorrect admin key')
    else:
        user_create_schema = UserCreateSchema(username=username, password=password1, admin=True)
        return user_create_schema