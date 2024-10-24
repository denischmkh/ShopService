from typing import Annotated

from fastapi import APIRouter, Depends
from .schemas import CategoryReadSchema, CategoryCreateSchema
from .service import CategoryLogic
from .constants import CREATE_CATEGORY_URL, DELETE_CATEGORY_URL, GET_ALL_CATEGORIES_URL, GET_CATEGORY
from ..auth.service import UserManager

router = APIRouter(prefix='/categories', tags=['Categories services'])


@router.get(GET_CATEGORY,
            response_model=CategoryReadSchema,
            description='Get category by id')
async def read_category(category: Annotated[CategoryReadSchema, Depends(CategoryLogic.get_category)]):
    return category

@router.get(GET_ALL_CATEGORIES_URL,
            response_model=list[CategoryReadSchema],
            description='Get all categories')
async def read_categories(categories: Annotated[list[CategoryReadSchema], Depends(CategoryLogic.get_all_categories)]):
    return categories


@router.post(CREATE_CATEGORY_URL,
             response_model=CategoryCreateSchema,
             description='Create new category',
             dependencies=[Depends(UserManager.get_current_admin_user)])
async def create_category(new_category: Annotated[CategoryCreateSchema, Depends(CategoryLogic.create_new_category)]):
    return new_category


@router.delete(DELETE_CATEGORY_URL,
               response_model=CategoryReadSchema,
               description='Delete category',
               dependencies=[Depends(UserManager.get_current_admin_user)])
async def delete_category(deleted_category: Annotated[CategoryCreateSchema, Depends(CategoryLogic.delete_category)]):
    return deleted_category
