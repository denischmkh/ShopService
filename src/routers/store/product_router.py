from typing import Annotated

from fastapi import APIRouter, Depends
from .schemas import ProductCreateSchema, ProductReadSchema
from .service import ProductLogic
from ..auth.service import is_admin_current_user

router = APIRouter(prefix='/products', tags=['Products routers'])


@router.post("/create",
             response_model_exclude_none=False,
             description='Append new product',
             dependencies=[Depends(is_admin_current_user)]
             )
async def read_items(new_product_schema: Annotated[ProductReadSchema, Depends(ProductLogic.create_product)]):
    return new_product_schema
