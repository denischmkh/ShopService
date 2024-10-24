from enum import Enum

from services.basket.schemas import BasketReadSchema, ProductInfoFromBasket
from services.store.schemas import ProductReadSchema


class UpdateProductQuantityChoose(int, Enum):
    addition = 1
    less = -1


def get_product_from_basket_info_list(basket: dict[str, BasketReadSchema], products: dict[str, ProductReadSchema]) -> list[ProductInfoFromBasket]:
    product_basket_info_list: list[ProductInfoFromBasket] = []
    for key, basket_schema in basket.items():
        product_price = products[key].price_with_discount if products[key].price_with_discount else products[key].price
        product_basket_schema = ProductInfoFromBasket(item=products[key],
                                                      quantity=basket_schema.quantity,
                                                      full_summa=product_price * basket_schema.quantity)
        product_basket_info_list.append(product_basket_schema)
    return product_basket_info_list