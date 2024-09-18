from fastapi import APIRouter, HTTPException, Depends, Request, Response, BackgroundTasks
from typing import Annotated
from .schemas import UserReadSchema
from sql_app.models import User
from .constants import DELETE_USER_URL, BAN_USER_URL, UNBAN_USER_URL, GET_CURRENT_USER_BY_TOKEN_URL, \
    GET_ALL_USERS_FROM_DB_URL, FOUND_USER_BY_ID_OR_USERNAME_URL, AUTHORIZATION_URL, REGISTRATION_URL
from .service import (Token_Scheme,
                      get_current_user,
                      get_user_by_id_or_username,
                      deleted_user,
                      verity_user_and_make_token,
                      create_new_user,
                      get_all_users_from_db, banning_user, unbanning_user)
from fastapi_cache.decorator import cache
router = APIRouter(prefix='/auth', tags=['Authorization routers'])


@router.post(REGISTRATION_URL, response_model=UserReadSchema, description='Create new user')
async def create_user(user_scheme: Annotated[UserReadSchema, Depends(create_new_user)]) -> UserReadSchema:
    return user_scheme


@router.post(AUTHORIZATION_URL, response_model=Token_Scheme,
             description='Authorize user and create JWT token')
async def authorization_user(jwt_token: Annotated[Token_Scheme, Depends(verity_user_and_make_token)]):
    return jwt_token


@router.get(FOUND_USER_BY_ID_OR_USERNAME_URL, response_model=UserReadSchema,
            description='Get one user by id or username')
async def get_user(user_data: Annotated[UserReadSchema, Depends(get_user_by_id_or_username)]):
    return user_data


@router.get(GET_ALL_USERS_FROM_DB_URL, response_model=list[UserReadSchema],
            description='Get all users from db')
async def get_all_users_from_database(list_of_users: Annotated[list[User], Depends(get_all_users_from_db)]):
    return list_of_users


@router.get(GET_CURRENT_USER_BY_TOKEN_URL, response_model=UserReadSchema,
            description='Get current user by access token')
async def get_current_user_by_token(current_user: Annotated[UserReadSchema, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status_code=404, detail='Invalid Token')
    return current_user


@router.patch(BAN_USER_URL, response_model=UserReadSchema, description='Ban user')
async def ban_user(banned_user: Annotated[UserReadSchema, Depends(banning_user)]):
    return banned_user


@router.patch(UNBAN_USER_URL, response_model=UserReadSchema, description='Unban user')
async def ban_user(ubbanned_user: Annotated[UserReadSchema, Depends(unbanning_user)]):
    return ubbanned_user


@router.delete(DELETE_USER_URL, response_model=UserReadSchema, description='Delete user by id')
async def delete_user_by_id(delete_user: Annotated[UserReadSchema, Depends(deleted_user)]):
    return delete_user
