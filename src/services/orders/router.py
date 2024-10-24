from fastapi import APIRouter, Depends

from services.orders.schemas import OrderSchema
from services.orders.service import create_order_for_buying, get_user_order_by_username, get_user_order_by_status, \
    update_order_status
from .constants import CREATE_ORDER, CHANGE_ORDER_STATUS, GET_USER_ORDERS, GET_ALL_ORDERS
from ..auth.service import UserManager

router = APIRouter(prefix='/order', tags=['Orders routers'])


@router.post(CREATE_ORDER,
             description='Create order',
             response_model=OrderSchema)
async def create_order(order_schema: OrderSchema = Depends(create_order_for_buying)):
    return order_schema


@router.get(GET_USER_ORDERS,
            description='Get Order by username',
            response_model=list[OrderSchema])
async def get_user_orders(orders_schemas: list[OrderSchema] = Depends(get_user_order_by_username)):
    return orders_schemas


@router.get(GET_ALL_ORDERS,
            description='Get orders for processing status',
            response_model=list[OrderSchema],
            dependencies=[Depends(UserManager.get_current_admin_user)])
async def get_orders_for_processing(orders_schemas: list[OrderSchema] = Depends(get_user_order_by_status)):
    return orders_schemas


@router.put(CHANGE_ORDER_STATUS,
            description='Update order status',
            response_model=OrderSchema,
            dependencies=[Depends(UserManager.get_current_admin_user)])
async def update_order_status(updated_order: OrderSchema = Depends(update_order_status)):
    return updated_order
