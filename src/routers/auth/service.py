import asyncio
from datetime import timedelta, datetime, timezone
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import HTTPException, Depends, Form, Query, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import ExpiredSignatureError
from pydantic import BaseModel

import config
from routers.schemas import UserCreateSchema, UserReadSchema, UserDatabaseSchema

from passlib.context import CryptContext

from config import JWT_SECRET_TOKEN
from sql_app.crud import UserCRUD
from sql_app.models import User

####################################################
#              Depends functions                   #
####################################################

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


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


async def create_new_user(user_create_scheme: UserCreateSchema) -> UserDatabaseSchema:
    result: UserDatabaseSchema = await UserCRUD.create(user_create_schema=user_create_scheme)
    return result


async def get_user_by_id_or_username(user_id: Annotated[UUID, Query()] = None,
                                     username: Annotated[str, Query()] = None,
                                     ):
    result = await UserCRUD.read(user_id=user_id, username=username)
    if not result:
        raise HTTPException(status_code=404, detail='User not found')
    return result


async def get_all_users_from_db() -> list[UserReadSchema]:
    users = await UserCRUD.get_all_users()
    return users


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    payload: dict = decode_token(token)
    user_from_db: UserReadSchema = await UserCRUD.read(user_id=payload.get("id"), username=payload.get("username"))
    if not user_from_db:
        raise HTTPException(status_code=404, detail='User not found')
    return user_from_db


async def deleted_user(user_id: Annotated[UUID, Query()],
                       current_user: Annotated[UserReadSchema, Depends(get_current_user)]) -> UserReadSchema:
    if not current_user.admin:
        raise HTTPException(status_code=401, detail='You are not admin')
    deleted_user: UserReadSchema = await UserCRUD.delete(user_id)
    if not deleted_user:
        raise HTTPException(status_code=401, detail='User not found')
    return deleted_user


async def verity_user_and_make_token(user_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token_Scheme:
    user: User | None = await UserCRUD.verify_user(user_data)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    data_to_encode = JWT_data(username=user.username, id=str(user.id))
    jwt_token: Token_Scheme = create_access_token(data=data_to_encode)
    return jwt_token
