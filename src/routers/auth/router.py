from uuid import UUID

from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sql_app.crud import UserCRUD
from typing import Annotated
from routers.schemas import UserReadSchema, UserDatabaseSchema, UserCreateSchema
from dependencies import create_access_token, JWT_data, Token_Scheme, decode_token, create_user_form
from sql_app.models import User

router = APIRouter(prefix='/auth', tags=['Authorization routers'])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    payload: dict = decode_token(token)
    user_from_db: UserReadSchema = await UserCRUD.read(user_id=payload.get("id"), username=payload.get("username"))
    if not user_from_db:
        raise HTTPException(status_code=404, detail='User not found')
    return user_from_db


@router.post('/register', response_model=UserReadSchema, description='Create new user')
async def create_user(user_scheme: Annotated[UserCreateSchema, Depends(create_user_form)]) -> UserDatabaseSchema:
    result: UserDatabaseSchema = await UserCRUD.create(user_scheme)
    return result


@router.get('/found_user', response_model=UserReadSchema, description='Get one user by id or username')
async def get_user_by_id(user_id: Annotated[UUID, Query()] = None,
                         username: Annotated[str, Query()] = None,
                         ):
    result = await UserCRUD.read(user_id=user_id, username=username)
    if not result:
        raise HTTPException(status_code=404, detail='User not found')
    return result


@router.get('/get_all_users', response_model=list[UserReadSchema], description='Get all users from db')
async def get_all_users_from_db():
    users = await UserCRUD.get_all_users()
    return users


@router.delete('/delete_user', response_model=UserReadSchema, description='Delete user by id')
async def delete_user_by_id(user_id: Annotated[UUID, Query()],
                            current_user: Annotated[UserReadSchema, Depends(get_current_user)]):
    if not current_user.admin:
        raise HTTPException(status_code=401, detail='You are not admin')
    deleted_user: UserReadSchema = await UserCRUD.delete(user_id)
    if not deleted_user:
        raise HTTPException(status_code=404, detail='User not found')
    return deleted_user


@router.post('/login', description='Authorize user and create JWT token')
async def authorization_user(user_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token_Scheme:
    user: User | None = await UserCRUD.verify_user(user_data)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    data_to_encode = JWT_data(username=user.username, id=str(user.id))
    jwt_token: Token_Scheme = create_access_token(data=data_to_encode)
    return jwt_token




@router.get('/get_current_user', response_model=UserReadSchema, description='Get current user by access token')
async def get_current_user_by_token(current_user: Annotated[UserReadSchema, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status_code=404, detail='Invalid Token')
    return current_user
