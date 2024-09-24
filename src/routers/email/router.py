from typing import Annotated

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from starlette import status
from starlette.responses import JSONResponse

from routers.auth.service import get_current_user
from routers.email.constants import VERIFY_ACCOUNT_URL, SEND_OR_RESEND_CODE_URL
from routers.email.service import verify_user, make_new_code
from routers.email.utils import send_email
from routers.auth.schemas import UserReadSchema

router = APIRouter(prefix='/email', tags=['Email routers'])


@router.post(VERIFY_ACCOUNT_URL, response_model=UserReadSchema, description='Verifying user account')
async def verifying_user(verified_user: Annotated[UserReadSchema, Depends(verify_user)]):
    return verified_user


@router.get(SEND_OR_RESEND_CODE_URL, description='Resend verification code')
async def resend_verify_code(user_scheme: Annotated[UserReadSchema, Depends(get_current_user)],
                             background_task: BackgroundTasks):
    if user_scheme.verified_email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You already verify your email')
    new_verify_code = await make_new_code(user_scheme)
    background_task.add_task(send_email, new_verify_code, user_scheme.email)
    message = {'message': f'New code successfully sending to your email: {user_scheme.email}'}
    return JSONResponse(content=message, status_code=status.HTTP_202_ACCEPTED)
