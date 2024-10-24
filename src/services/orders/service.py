import uuid
from typing import Annotated

from starlette import status

from mongo.crud import MongoCRUD
from services.auth.schemas import UserReadSchema
from services.auth.service import UserManager
from fastapi import Form, Depends, HTTPException, Query

from services.basket.schemas import FullBasketSchema
from services.basket.service import BasketManager
from services.orders.schemas import OrderSchema
from services.orders.utils import OrderStatus
from sql.crud import BasketCRUD


async def create_order_for_buying(full_basket: FullBasketSchema = Depends(BasketManager.get_full_basket),
                                  current_user: UserReadSchema = Depends(UserManager.get_current_verified_user),
                                  post_index: int = Form(..., description='Post index to delivery')) -> OrderSchema:
    if not full_basket.items:
        raise HTTPException(status_code=status.HTTP_201_CREATED, detail='Your basket is empty')
    order_schema = OrderSchema(
        basket=full_basket,
        username=current_user.username,
        post_index=post_index
    )
    json_order_schema = order_schema.json()
    try:
        await MongoCRUD.create(json_order_schema)
    except:
        raise HTTPException(status_code=status.HTTP_201_CREATED,
                            detail='Something not wrong with trying to save record!')
    await BasketCRUD.clear_basket(current_user.id)
    return order_schema


async def get_user_order_by_username(current_user: UserReadSchema = Depends(UserManager.get_current_verified_user),
                                     order_status: Annotated[OrderStatus, Query(...,
                                                                                description='Get orders by status, send empty if necessary get all orders')] = None):
    result = await MongoCRUD.get_user_orders(current_user.username, order_status)
    return result


async def get_user_order_by_status(order_status: OrderStatus = Query(..., description='Orders necessary status'),
                                   page: Annotated[int, Query(...)] = 1):
    result = await MongoCRUD.get_orders_for_processing(status=order_status, page=page)
    return result


async def update_order_status(order_id: uuid.UUID = Query(..., description='Unique order id to update status'),
                              new_status: OrderStatus = Query(...)):
    result = await MongoCRUD.update_order(order_id=order_id, new_status=new_status)
    return result
