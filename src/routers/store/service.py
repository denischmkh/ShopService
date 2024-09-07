from typing import Annotated
from uuid import UUID

from starlette import status

from routers.auth.service import get_current_user
from routers.schemas import CategoryReadSchema, CategoryCreateSchema, UserReadSchema
from sql_app.crud import CategoryCRUD
from sql_app.models import Category, User
from fastapi import Form, Depends, HTTPException


async def get_all_categories() -> list[CategoryReadSchema]:
    categories = await CategoryCRUD.read()
    return categories

def create_category_form(title: str = Form(..., min_length=2, max_length=30)):
    category_form = CategoryCreateSchema(title=title)
    return category_form

async def create_new_category(category_form: Annotated[CategoryCreateSchema, Depends(create_category_form)],
                              current_user: Annotated[User, Depends(get_current_user)]) -> CategoryCreateSchema:
    if not current_user.admin:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="You don't have permission to this action")
    result = await CategoryCRUD.create(category_form)
    return result

async def delete_category(category_id: UUID,
                          current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user.admin:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="You don't have permission to this action")
    result = await CategoryCRUD.delete(category_id)
    return result
