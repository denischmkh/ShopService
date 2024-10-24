from pprint import pprint
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Body, Form

from services.auth.schemas import UserReadSchema
from services.auth.service import UserManager
from services.basket.schemas import BasketCreateSchema, BasketReadSchema, ProductInfoFromBasket, FullBasketSchema
from services.basket.utils import UpdateProductQuantityChoose, get_product_from_basket_info_list
from sql.crud import BasketCRUD, ProductCRUD


class BasketManager:
    @staticmethod
    async def add_item_in_basket(current_user: UserReadSchema = Depends(UserManager.get_current_verified_user),
                                 product_id: UUID = Form(...)) -> BasketCreateSchema:
        await ProductCRUD.read(product_id)
        find_product_in_basket = await BasketCRUD.read(user_id=current_user.id, product_id=product_id)
        if not find_product_in_basket:
            basket_schema = BasketCreateSchema(products_id=product_id, users_id=current_user.id)
            result = await BasketCRUD.create(basket_schema=basket_schema)
        else:
            result = await BasketCRUD.update(user_id=current_user.id, product_id=product_id, quantity=1)
        return result

    @staticmethod
    async def update_quantity(current_user: UserReadSchema = Depends(UserManager.get_current_verified_user),
                              product_id: UUID = Form(...),
                              new_quantity: UpdateProductQuantityChoose = Form(...)) -> BasketReadSchema:
        result = await BasketCRUD.update(user_id=current_user.id, product_id=product_id, quantity=new_quantity.value)
        return result

    @staticmethod
    async def delete_item(current_user: UserReadSchema = Depends(UserManager.get_current_verified_user),
                          product_id: UUID = Form(...)) -> BasketReadSchema:
        result = await BasketCRUD.delete(user_id=current_user.id, product_id=product_id)
        return result

    @staticmethod
    async def get_full_basket(
            current_user: UserReadSchema = Depends(UserManager.get_current_verified_user)) -> FullBasketSchema:
        basket_schemas = await BasketCRUD.full_basket(user_id=current_user.id)
        product_schemas = await ProductCRUD.get_product_by_basket_schemas(basket_schemas=basket_schemas)
        dict_basket = {str(basket.products_id): basket for basket in basket_schemas}
        dict_products = {str(product.id): product for product in product_schemas}
        product_basket_info_list: list[ProductInfoFromBasket] = get_product_from_basket_info_list(
            products=dict_products,
            basket=dict_basket)
        full_products_summa = sum([product.full_summa for product in product_basket_info_list])
        final_basket_schema = FullBasketSchema(
            full_summa=full_products_summa,
            items=product_basket_info_list)
        return final_basket_schema

    @staticmethod
    async def clear_basket(current_user: UserReadSchema = Depends(UserManager.get_current_verified_user)) -> None:
        await BasketCRUD.clear_basket(user_id=current_user.id)
        return None
