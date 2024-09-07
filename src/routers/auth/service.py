from typing import Annotated
from uuid import UUID
from fastapi import HTTPException, Depends, Form, Query, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette import status
from routers.auth.utils import decode_token, create_user_form, Token_Scheme, JWT_data, create_access_token
from routers.schemas import UserCreateSchema, UserReadSchema, UserDatabaseSchema, CreateVerificationCode
from sql_app.crud import UserCRUD, VerifyCodeCRUD
from sql_app.models import User

####################################################
#              Depends functions                   #
####################################################


ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


async def create_new_user(
        user_create_scheme: Annotated[UserCreateSchema, Depends(create_user_form)]) -> UserDatabaseSchema:
    result: UserDatabaseSchema = await UserCRUD.create(user_create_schema=user_create_scheme)
    return result


async def get_user_by_id_or_username(user_id: Annotated[UUID, Query()] = None,
                                     username: Annotated[str, Query()] = None,
                                     ):
    result = await UserCRUD.read(user_id=user_id, username=username)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return result


async def get_all_users_from_db() -> list[UserReadSchema]:
    users = await UserCRUD.get_all_users()
    return users


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
    return banned_user


async def unbanning_user(current_user: Annotated[UserReadSchema, Depends(get_current_verified_user)],
                         user_id: UUID = Form(...)):
    if not current_user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not admin')
    unbanned_user = await UserCRUD.unban_user(user_id=user_id)
    return unbanned_user

async def create_verify_code_in_db(verify_code_schema: CreateVerificationCode) -> CreateVerificationCode:
    await VerifyCodeCRUD.create(verify_code_schema)
    return verify_code_schema


async def verify_user(verification_code: int = Form(..., lt=999999, ge=100000),
                      current_user: UserReadSchema = Depends(get_current_user)):
    if current_user.verified_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You already verified')
    code_in_db = await VerifyCodeCRUD.read(current_user)
    if verification_code != code_in_db:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Incorrect code, try again!')
    await UserCRUD.verifying_user(current_user.id)
    return current_user