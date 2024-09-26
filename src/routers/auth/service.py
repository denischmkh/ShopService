from datetime import timedelta
from typing import Annotated
from uuid import UUID
from fastapi import HTTPException, Depends, Form, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

from .constants import REFRESH_TOKEN_EXPIRE_MINUTES, ACCESS_TOKEN_EXPIRE_MINUTES, PAGINATOR_ITEMS_PER_PAGE
from .utils import decode_token, create_user_form, login_user_form, \
    create_access_and_refresh_token
from .schemas import UserCreateSchema, UserReadSchema, UserDatabaseSchema, UserLoginSchema, AccessTokenScheme, \
    RefreshTokenScheme, TokenScheme
from sql_app.crud import UserCRUD
from sql_app.models import User

bearer = HTTPBearer()


async def create_new_user(user_create_schema: Annotated[UserCreateSchema, Depends(create_user_form)]) -> UserReadSchema:
    result: UserDatabaseSchema = await UserCRUD.create(user_create_schema=user_create_schema)
    user_read_schema = UserReadSchema(**result.dict())
    return user_read_schema


async def get_user_by_id_or_username(user_id: Annotated[UUID, Query()] = None,
                                     username: Annotated[str, Query()] = None,
                                     ):
    result = await UserCRUD.read(user_id=user_id, username=username)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return result


async def get_all_users_from_db(page: Annotated[int, Query(..., ge=1)] = 1) -> list[UserReadSchema]:
    users = await UserCRUD.get_all_users(page=page, per_page=PAGINATOR_ITEMS_PER_PAGE)
    return users


async def get_current_user(access_token: Annotated[HTTPAuthorizationCredentials, Depends(bearer)]):
    payload: dict = decode_token(access_token.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Token has been expired')
    if payload.get('type') != 'ACCESS':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Incorrect token type, necessary access')
    expiration_time = payload.get("exp")
    if expiration_time is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Token does not have an expiration time')
    user_from_db: User = await UserCRUD.read(user_id=payload.get("id"), username=payload.get("username"))
    if not user_from_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user_from_db


async def get_current_verified_user(current_user: UserReadSchema = Depends(get_current_user)) -> UserReadSchema:
    if not current_user.verified_email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not verified your email')

    return UserReadSchema.from_orm(current_user)


async def is_admin_current_user(current_user: UserReadSchema = Depends(get_current_verified_user)) -> UserReadSchema:
    if not current_user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=r"You don't have permission")
    return current_user


async def delete_user(user_id: Annotated[UUID, Query()],
                      current_user: Annotated[UserReadSchema, Depends(get_current_verified_user)]) -> UserReadSchema:
    if not current_user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not admin')
    deleted_user: UserReadSchema = await UserCRUD.delete(user_id)
    if not deleted_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return deleted_user


async def verify_user_and_make_token(user_data: Annotated[UserLoginSchema, Depends(login_user_form)]) -> TokenScheme:
    if not user_data.email and not user_data.username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Please, enter username or email')
    user: User | None = await UserCRUD.verify_user(user_data)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    access_token_data = AccessTokenScheme(username=user.username, email=user.email, id=str(user.id))
    refresh_token_data = RefreshTokenScheme(id=str(user.id))
    access_token: str = create_access_and_refresh_token(data=access_token_data,
                                                        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token: str = create_access_and_refresh_token(data=refresh_token_data,
                                                         expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))
    tokens_schemas = TokenScheme(access_token=access_token, refresh_token=refresh_token)
    return tokens_schemas


async def refresh_token(refresh_token: str = Query(...)):
    payload = decode_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Refresh token has been expired')
    if payload['type'] != 'REFRESH':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Incorrect token type')
    user: User = await UserCRUD.read(user_id=payload['id'])
    user_schema = UserReadSchema.from_orm(user)
    new_access_token_scheme = AccessTokenScheme(id=str(user_schema.id),
                                                username=user_schema.username,
                                                email=user_schema.email)
    access_token = create_access_and_refresh_token(new_access_token_scheme,
                                                   expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    token_scheme = TokenScheme(access_token=access_token)
    return token_scheme


async def banning_user(user_id: UUID = Form(...)):
    banned_user = await UserCRUD.ban_user(user_id=user_id)
    banned_user_schema = UserReadSchema.from_orm(banned_user)
    return banned_user_schema


async def unbanning_user(user_id: UUID = Form(...)):
    unbanned_user = await UserCRUD.unban_user(user_id=user_id)
    unbanned_user_schema = UserReadSchema.from_orm(unbanned_user)
    return unbanned_user_schema
