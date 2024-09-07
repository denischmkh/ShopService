import asyncio

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Annotated
from routers.schemas import UserReadSchema, UserDatabaseSchema, UserCreateSchema
from sql_app.models import User
from .constants import AuthenticationUrls
from .service import (Token_Scheme,
                      create_user_form,
                      get_current_user,
                      get_user_by_id_or_username,
                      deleted_user,
                      verity_user_and_make_token,
                      create_new_user,
                      get_all_users_from_db, banning_user, unbanning_user)
from fastapi_cache.decorator import cache

router = APIRouter(prefix='/auth', tags=['Authorization routers'])


@router.post(AuthenticationUrls.registration.value, response_model=UserDatabaseSchema, description='Create new user')
async def create_user(user_scheme: Annotated[UserCreateSchema, Depends(create_new_user)]) -> UserDatabaseSchema:
    result: UserDatabaseSchema = await create_new_user(user_scheme)
    return result


@router.post(AuthenticationUrls.authorization.value, response_model=Token_Scheme,
             description='Authorize user and create JWT token')
async def authorization_user(jwt_token: Annotated[Token_Scheme, Depends(verity_user_and_make_token)]):
    return jwt_token


@router.get(AuthenticationUrls.found_user_by_id_or_username.value, response_model=UserReadSchema,
            description='Get one user by id or username')
async def get_user(user_data: Annotated[UserReadSchema, Depends(get_user_by_id_or_username)]):
    return user_data


@router.get(AuthenticationUrls.get_all_users_from_db.value, response_model=list[UserReadSchema],
            description='Get all users from db')
async def get_all_users_from_database(list_of_users: Annotated[list[User], Depends(get_all_users_from_db)]):
    return list_of_users


@router.get(AuthenticationUrls.get_current_user_by_token.value, response_model=UserReadSchema,
            description='Get current user by access token')
async def get_current_user_by_token(current_user: Annotated[UserReadSchema, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status_code=404, detail='Invalid Token')
    return current_user

@router.patch(AuthenticationUrls.ban_user.value, response_model=UserReadSchema, description='Ban user')
async def ban_user(banned_user: Annotated[UserReadSchema, Depends(banning_user)]):
    return banned_user

@router.patch(AuthenticationUrls.unban_user.value, response_model=UserReadSchema, description='Ban user')
async def ban_user(ubbanned_user: Annotated[UserReadSchema, Depends(unbanning_user)]):
    return ubbanned_user

@router.delete(AuthenticationUrls.delete_user.value, response_model=UserReadSchema, description='Delete user by id')
async def delete_user_by_id(delete_user: Annotated[UserReadSchema, Depends(deleted_user)]):
    return delete_user
