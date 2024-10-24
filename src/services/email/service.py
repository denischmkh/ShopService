from fastapi import Form, Depends, HTTPException
from starlette import status

from services.auth.service import UserManager
from services.email.schemas import CreateVerificationCode
from services.auth.schemas import UserReadSchema
from sql.crud import VerifyCodeCRUD, UserCRUD


async def verify_user(verification_code: int = Form(..., lt=999999, ge=100000),
                      current_user: UserReadSchema = Depends(UserManager.get_current_user)):
    if current_user.verified_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You already verified')
    code_in_db = await VerifyCodeCRUD.read(current_user)
    if verification_code != code_in_db:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Incorrect code, try again!')
    db_updated_user = await UserCRUD.verifying_user(current_user.id)
    updated_user_schema = UserReadSchema.from_orm(db_updated_user)
    return updated_user_schema


async def make_new_code(current_user: UserReadSchema) -> int:
    new_code = CreateVerificationCode(users_id=current_user.id)
    await VerifyCodeCRUD.delete(user_schema=current_user)
    await VerifyCodeCRUD.create(new_code)
    return new_code.verify_code
