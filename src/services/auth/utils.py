import re
from datetime import datetime, timezone, timedelta
from typing import Annotated

import jwt
from fastapi import HTTPException, Form
from jwt import ExpiredSignatureError
from pydantic import BaseModel, EmailStr
from starlette import status


from passlib.context import CryptContext

import config

from services.auth.schemas import UserCreateSchema, UserLoginSchema, AccessTokenScheme, RefreshTokenScheme


ALGORITHM = "HS256"


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


def create_access_and_refresh_token(data: AccessTokenScheme | RefreshTokenScheme,
                                    expires_delta: timedelta):
    data = data.dict()
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET_TOKEN, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict | None:
    try:
        decode_token = jwt.decode(token, config.JWT_SECRET_TOKEN, algorithms=[ALGORITHM])
        return decode_token
    except ExpiredSignatureError:
        return None


def login_user_form(username: Annotated[str | None, Form()] = None,
                    email: Annotated[EmailStr | None, Form()] = None,
                    password: str = Form()) -> UserLoginSchema:
    return UserLoginSchema(username=username, email=email, password=password)



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)