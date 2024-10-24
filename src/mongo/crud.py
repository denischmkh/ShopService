import json
import uuid
from typing import AsyncIterator

from fastapi import HTTPException

from services.orders.schemas import OrderSchema
from contextlib import asynccontextmanager
from config import MONGO_CONNECT

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from services.orders.utils import OrderStatus


class MongoCRUD:
    """ CRUD - Functions to create, read and interaction with orders """

    @staticmethod
    @asynccontextmanager
    async def get_mongo_collection() -> AsyncIterator[AsyncIOMotorCollection]:
        client = AsyncIOMotorClient(MONGO_CONNECT)
        collection: AsyncIOMotorCollection = client.Orders.orders
        try:
            yield collection
        finally:
            client.close()

    @classmethod
    async def create(cls, order_schema: str) -> str:
        async with cls.get_mongo_collection() as collection:
            parsed_data = json.loads(order_schema)
            await collection.insert_one(parsed_data)
            return parsed_data

    @classmethod
    async def get_user_orders(cls, username: str, status: OrderStatus | None = None) -> list[OrderSchema]:
        async with cls.get_mongo_collection() as collection:
            query = {'username': username}
            if status:
                query['status'] = status.value
            cursor = collection.find(query)
            orders = await cursor.to_list(length=None)
            return [OrderSchema(**order) for order in orders]

    @classmethod
    async def get_orders_for_processing(cls, page: int = 1, status: OrderStatus | None = None) -> list[OrderSchema]:
        async with cls.get_mongo_collection() as collection:
            cursor = collection.find({'status': status.value})
            orders = await cursor.to_list(length=None)
            start = (page - 1) * 10
            end = page * 10
            return orders[start:end]

    @classmethod
    async def update_order(cls, order_id: uuid.UUID, new_status: OrderStatus) -> OrderSchema:
        async with cls.get_mongo_collection() as collection:
            await collection.update_one({'id': str(order_id)}, {'$set': {'status': new_status.value}})
            updated_order = await collection.find_one({'id': str(order_id)})
            if updated_order is None:
                raise HTTPException(status_code=404, detail="Order not found")
            return OrderSchema(**updated_order)