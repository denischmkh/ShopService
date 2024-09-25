from typing import Annotated

from fastapi import APIRouter, Depends
from .schemas import CategoryReadSchema, CategoryCreateSchema
from .service import CategoryLogic
from .constants import CREATE_CATEGORY_URL, DELETE_CATEGORY_URL, GET_ALL_CATEGORIES_URL
from ..auth.service import is_admin_current_user

router = APIRouter(prefix='/categories', tags=['Categories routers'])


@router.get(GET_ALL_CATEGORIES_URL,
            response_model=list[CategoryReadSchema],
            description='Get all categories'
            )
async def read_categories(categories: Annotated[list[CategoryReadSchema], Depends(CategoryLogic.get_all_categories)]):
    return categories


@router.post(CREATE_CATEGORY_URL,
             response_model=CategoryCreateSchema,
             description='Create new category',
             dependencies=[Depends(is_admin_current_user)]
             )
async def create_category(new_category: Annotated[CategoryCreateSchema, Depends(CategoryLogic.create_new_category)]):
    return new_category


@router.delete(DELETE_CATEGORY_URL,
               response_model=CategoryReadSchema,
               description='Delete category',
               dependencies=[Depends(is_admin_current_user)]
               )
async def delete_category(deleted_category: Annotated[CategoryCreateSchema, Depends(CategoryLogic.delete_category)]):
    return deleted_category
