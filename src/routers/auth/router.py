from uuid import UUID

from fastapi import APIRouter, Body, Query, Request, HTTPException, Cookie
from fastapi.responses import JSONResponse
from src.sql_app.crud import UserCRUD
from typing import Annotated
from ..schemas import UserReadSchema, UserDatabaseSchema, UserCreateSchema, UserAuthScheme
from ...dependencies import create_access_token, JWT_data, decode_token
from ...sql_app.models import User

router = APIRouter(prefix='/auth', tags=['Authorization routers'])


@router.post('/register', response_model=UserReadSchema, description='Create new user')
async def create_user(user_scheme: Annotated[UserCreateSchema, Body()]) -> UserDatabaseSchema:
    result: UserDatabaseSchema = await UserCRUD.create(user_scheme)
    return result


@router.get('/found_user', response_model=UserReadSchema, description='Get one user by id or username')
async def get_user_by_id(user_id: Annotated[UUID, Query()] = None,
                         username: Annotated[str, Query()] = None):
    result = await UserCRUD.read(user_id=user_id, username=username)
    if not result:
        raise HTTPException(status_code=404, detail='User not found')
    return result


@router.get('/get_all_users', response_model=list[UserReadSchema], description='Get all users from db')
async def get_all_users_from_db():
    users = await UserCRUD.get_all_users()
    return users


@router.delete('/delete_user', response_model=UserReadSchema, description='Delete user by id')
async def delete_user_by_id(user_id: Annotated[UUID, Query()]):
    result = await UserCRUD.delete(user_id)
    if not result:
        raise HTTPException(status_code=404, detail='User not found')


@router.post('/login', response_class=JSONResponse, description='Authorize user and create JWT token')
async def authorization_user(user_data: UserAuthScheme):
    user: User | None = await UserCRUD.verify_user(user_data)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    data_to_encode = JWT_data(**{'username': user.username, 'id': str(user.id)})
    jwt_token = create_access_token(data=data_to_encode)
    response = JSONResponse(content={'access_token': jwt_token}, status_code=200)
    response.set_cookie(key='access_token', value=jwt_token)
    return response


@router.get('/get_current_user', response_model=UserReadSchema, description='Get current user by access token')
async def get_current_user(request: Request):
    user_data = decode_token(request.cookies.get('access_token'))
    if not user_data:
        raise HTTPException(status_code=404, detail='User not found')
    user = await UserCRUD.read(user_id=UUID(user_data.get('id')), username=user_data.get('username'))
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user
