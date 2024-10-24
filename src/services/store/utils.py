from typing import Annotated

from fastapi import UploadFile, File, HTTPException
from sqlalchemy import RowMapping, Row
from starlette import status

from services.store.schemas import ProductReadSchema, ProductCreateSchema
from sql.models import Product


def make_products_read_schema(product: RowMapping | Row | ProductCreateSchema) -> ProductReadSchema:
    if isinstance(product, ProductCreateSchema):
        product_schema = ProductReadSchema(**product.dict())
    else:
        product_schema = ProductReadSchema.from_orm(product)
    product_schema.price_with_discount = None if not product_schema.discount else round(
        (product_schema.price / 100) * (100 - product_schema.discount), 2)
    return product_schema


def image_format_validator(image: Annotated[UploadFile, File()]):
    file_name = image.filename.lower()
    if file_name.endswith('.png') or file_name.endswith('.jpg') or file_name.endswith('.webp'):
        return image
    else:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Invalid photo format')
