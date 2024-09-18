import re
from datetime import datetime, timezone, timedelta
from typing import Annotated

import jwt
from fastapi import HTTPException, Form
from jwt import ExpiredSignatureError
from pydantic import BaseModel
from starlette import status

import config
from routers.auth.constants import JWT_TOKEN_EXPIRE_MINUTES
from routers.auth.schemas import UserCreateSchema, UserLoginSchema

ALGORITHM = "HS256"


class JWT_data(BaseModel):
    id: str
    username: str


class Token_Scheme(BaseModel):
    access_token: str
    token_type: str = 'Bearer'


def create_user_form(username: str = Form(description='Username', min_length=3, max_length=30),
                     password1: str = Form(description='Password', min_length=8),
                     password2: str = Form(description='Repeat password', min_length=8),
                     email: str = Form(description='Email adress'),
                     Admin_key: Annotated[str | None, Form(description='Admin Key')] = None,
                     ):
    if password1 != password2:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Second password incorrect!')
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Incorrect email')
    elif not Admin_key:
        user_create_schema = UserCreateSchema(username=username, password=password1, admin=False, email=email)
        return user_create_schema
    elif Admin_key != config.ADMIN_SECRET:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Incorrect admin key')
    else:
        user_create_schema = UserCreateSchema(username=username, password=password1, admin=True, email=email)
        return user_create_schema


def create_access_token(data: JWT_data, expires_delta: timedelta | None = None):
    data = data.dict()
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET_TOKEN, algorithm=ALGORITHM)
    token_scheme = Token_Scheme(access_token=encoded_jwt)
    return token_scheme


def decode_token(access_token: str) -> dict | None:
    try:
        decode_token = jwt.decode(access_token, config.JWT_SECRET_TOKEN, algorithms=[ALGORITHM])
        return decode_token
    except ExpiredSignatureError:
        return None

def login_user_form(username: Annotated[str | None, Form()] = None,
                    email: Annotated[str | None, Form()] = None,
                    password: str = Form()) -> UserLoginSchema:
    return UserLoginSchema(username=username, email=email, password=password)
