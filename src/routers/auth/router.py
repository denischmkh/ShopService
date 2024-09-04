from uuid import UUID

from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Annotated
from routers.schemas import UserReadSchema, UserDatabaseSchema, UserCreateSchema
from .dependencies import create_access_token, JWT_data, Token_Scheme, decode_token, create_user_form, get_current_user, \
    get_user_by_id, deleted_user, verity_user_and_make_token, create_new_user, get_all_users_from_db
from sql_app.models import User

router = APIRouter(prefix='/auth', tags=['Authorization routers'])


@router.post('/register', response_model=UserReadSchema, description='Create new user')
async def create_user(user_scheme: Annotated[UserCreateSchema, Depends(create_user_form)]) -> UserDatabaseSchema:
    result: UserDatabaseSchema = await create_new_user(user_scheme)
    return result


@router.get('/found_user', response_model=UserReadSchema, description='Get one user by id or username')
async def get_user(user_data: Annotated[UserReadSchema, Depends(get_user_by_id)]):
    return user_data



@router.get('/get_all_users', response_model=list[UserReadSchema], description='Get all users from db')
async def get_all_users_from_db(list_of_users: Annotated[list[UserReadSchema], Depends(get_all_users_from_db)]):
    return list_of_users


@router.delete('/delete_user', response_model=UserReadSchema, description='Delete user by id')
async def delete_user_by_id(delete_user: Annotated[UserReadSchema, Depends(deleted_user)]):
    return delete_user


@router.post('/login', description='Authorize user and create JWT token')
async def authorization_user(jwt_token: Annotated[Token_Scheme, Depends(verity_user_and_make_token)]) -> Token_Scheme:
    return jwt_token



@router.get('/get_current_user', response_model=UserReadSchema, description='Get current user by access token')
async def get_current_user_by_token(current_user: Annotated[UserReadSchema, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status_code=404, detail='Invalid Token')
    return current_user
