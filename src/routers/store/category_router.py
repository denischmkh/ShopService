from typing import Annotated

from fastapi import APIRouter, Depends
from routers.schemas import CategoryReadSchema, CategoryCreateSchema
from routers.store.service import get_all_categories, create_new_category, delete_category
from .constants import CategoryUrls

router = APIRouter(prefix='/categories', tags=['Categories routers'])


@router.get(CategoryUrls.get_all_categories.value, response_model=list[CategoryReadSchema], description='Get all categories')
async def read_categories(categories: Annotated[list[CategoryReadSchema], Depends(get_all_categories)]):
    return categories

@router.post(CategoryUrls.create_category.value, response_model=CategoryCreateSchema, description='Create new category')
async def create_category(new_category: Annotated[CategoryCreateSchema, Depends(create_new_category)]):
    return new_category

@router.delete(CategoryUrls.delete_category.value, response_model=CategoryReadSchema, description='Delete category')
async def delete_category(deleted_category: Annotated[CategoryCreateSchema, Depends(delete_category)]):
    return deleted_category