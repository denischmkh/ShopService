from typing import Annotated

from fastapi import APIRouter, Depends

from .constants import CREATE_PRODUCT, DELETE_PRODUCT, GET_ALL_PRODUCTS, GET_PRODUCT
from .schemas import ProductReadSchema
from .service import ProductLogic
from ..auth.service import UserManager

router = APIRouter(prefix='/products', tags=['Products services'])


@router.post(CREATE_PRODUCT,
             response_model_exclude_none=False,
             description='Append new product',
             dependencies=[Depends(UserManager.get_current_admin_user)]
             )
async def read_items(new_product_schema: Annotated[ProductReadSchema, Depends(ProductLogic.create_product)]):
    return new_product_schema


@router.get(GET_PRODUCT,
            response_model=ProductReadSchema,
            description='Get product by id'
            )
async def get_product(product: Annotated[ProductReadSchema, Depends(ProductLogic.get_product)]):
    return product


@router.get(GET_ALL_PRODUCTS,
            response_model=list[ProductReadSchema],
            description='Get Products by page'
            )
async def get_products(products: Annotated[list[ProductReadSchema], Depends(ProductLogic.get_products)]):
    return products


@router.delete(DELETE_PRODUCT,
               response_model=ProductReadSchema,
               description='Delete product by id',
               dependencies=[Depends(UserManager.get_current_admin_user)]
               )
async def delete_product_by_id(deleted_product: Annotated[ProductReadSchema, Depends(ProductLogic.delete_product)]):
    return deleted_product
