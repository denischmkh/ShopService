import datetime
import uuid

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserReadSchema(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    verified_email: bool
    active: bool
    admin: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class UserCreateSchema(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8)
    admin: bool = False
    email: EmailStr
    verified_email: bool = False

    @field_validator('username', mode='before')
    @classmethod
    def validate_username(cls, username: str):
        if len(username) < 3 or len(username) > 30:
            raise HTTPException(status_code=422, detail='Username must contain minimum 3 characters, maximum 30')
        return username

    @field_validator('password', mode='before')
    @classmethod
    def validate_password(cls, password: str):
        if len(password) < 8:
            raise HTTPException(status_code=422, detail='Password too short!')
        if not any(el.isupper() for el in password):
            raise HTTPException(status_code=422, detail='Password must contain at least one capital letter')
        return password


class UserDatabaseSchema(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    username: str
    hashed_password: str
    active: bool = Field(default=True)
    admin: bool
    email: EmailStr
    verified_email: bool = False
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class UserLoginSchema(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str


class AccessTokenScheme(BaseModel):
    id: str
    username: str
    email: str
    type: str = 'ACCESS'


class RefreshTokenScheme(BaseModel):
    id: str
    type: str = 'REFRESH'


class TokenScheme(BaseModel):
    access_token: str
    refresh_token: str = None
    token_type: str = 'Bearer'
