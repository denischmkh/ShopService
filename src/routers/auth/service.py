from typing import Annotated
from uuid import UUID
from fastapi import HTTPException, Depends, Form, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette import status

from .paginator import Paginator
from .utils import decode_token, create_user_form, Token_Scheme, JWT_data, create_access_token
from .schemas import UserCreateSchema, UserReadSchema, UserDatabaseSchema
from sql_app.crud import UserCRUD
from sql_app.models import User


ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


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
    users = await UserCRUD.get_all_users()
    paginator = Paginator(users, page=page)
    return paginator.paginated_items


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    payload: dict = decode_token(token)
    user_from_db: UserReadSchema = await UserCRUD.read(user_id=payload.get("id"), username=payload.get("username"))
    if not user_from_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user_from_db


async def get_current_verified_user(current_user: UserDatabaseSchema = Depends(get_current_user)):
    if not current_user.verified_email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not verified your email')
    return current_user


async def deleted_user(user_id: Annotated[UUID, Query()],
                       current_user: Annotated[UserReadSchema, Depends(get_current_verified_user)]) -> UserReadSchema:
    if not current_user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not admin')
    deleted_user: UserReadSchema = await UserCRUD.delete(user_id)
    if not deleted_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return deleted_user


async def verity_user_and_make_token(user_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token_Scheme:
    user: User | None = await UserCRUD.verify_user(user_data)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    data_to_encode = JWT_data(username=user.username, id=str(user.id))
    jwt_token: Token_Scheme = create_access_token(data=data_to_encode)
    return jwt_token


async def banning_user(current_user: Annotated[UserReadSchema, Depends(get_current_verified_user)],
                       user_id: UUID = Form(...)):
    if not current_user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not admin')
    banned_user = await UserCRUD.ban_user(user_id=user_id)
    banned_user_schema = UserReadSchema.from_orm(banned_user)
    return banned_user_schema


async def unbanning_user(current_user: Annotated[UserReadSchema, Depends(get_current_verified_user)],
                         user_id: UUID = Form(...)):
    if not current_user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not admin')
    unbanned_user = await UserCRUD.unban_user(user_id=user_id)
    unbanned_user_schema = UserReadSchema.from_orm(unbanned_user)
    return unbanned_user_schema





