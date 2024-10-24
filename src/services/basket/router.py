from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import Response

from .constants import GET_FULL_BASKET, DELETE_ITEM_FROM_BASKET, ADD_ITEM_TO_BASKET, CLEAR_BASKET, UPDATE_QUANTITY
from .schemas import BasketCreateSchema, BasketReadSchema, FullBasketSchema
from .service import BasketManager

router = APIRouter(prefix='/basket', tags=['Basket Routers'])


@router.get(GET_FULL_BASKET,
            response_model=FullBasketSchema,
            description='Get full user basket'
            )
async def get_full_user_basket(basket: Annotated[FullBasketSchema, Depends(BasketManager.get_full_basket)]):
    return basket


@router.post(ADD_ITEM_TO_BASKET,
             response_model=BasketCreateSchema,
             description='Add product to basket'
             )
async def add_item_to_basket(item_schema: Annotated[BasketCreateSchema, Depends(BasketManager.add_item_in_basket)]):
    return item_schema


@router.patch(UPDATE_QUANTITY,
              response_model=BasketReadSchema,
              description='Update quantity of product in basket'
              )
async def update_product_quantity(item_schema: Annotated[BasketReadSchema, Depends(BasketManager.update_quantity)]):
    return item_schema


@router.delete(DELETE_ITEM_FROM_BASKET,
               response_model=BasketReadSchema,
               description='Delete product from basket'
               )
async def delete_product_from_basket(deleted_item_schema: Annotated[BasketReadSchema, Depends(BasketManager.delete_item)]):
    return deleted_item_schema


@router.delete(CLEAR_BASKET,
               dependencies=[Depends(BasketManager.clear_basket)],
               description='Clear basket',
               status_code=status.HTTP_200_OK)
async def clear_user_basket():
    return {'Success': 'Basket successfully cleared'}
