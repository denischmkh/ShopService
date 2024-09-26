from sqlalchemy import RowMapping, Row

from routers.store.schemas import ProductReadSchema
from sql_app.models import Product


def make_products_read_schema(product: RowMapping | Row):
    product_schema = ProductReadSchema.from_orm(product)
    product_schema.price_with_discount = None if not product_schema.discount else round(
        (product_schema.price / 100) * (100 - product_schema.discount), 2)
    return product_schema