import uuid
from typing import Annotated
from uuid import UUID

from starlette import status

from routers.auth.service import get_current_user, get_current_verified_user, is_admin_current_user
from .schemas import CategoryReadSchema, CategoryCreateSchema, ProductCreateSchema, ProductReadSchema
from sql_app.crud import CategoryCRUD, ProductCRUD
from sql_app.models import Category, User
from fastapi import Form, Depends, HTTPException, UploadFile, File

from ..S3_Storage.storage import S3Client, get_s3_storage
from ..auth.schemas import UserReadSchema


class CategoryLogic:
    @staticmethod
    async def get_all_categories() -> list[CategoryReadSchema]:
        categories = await CategoryCRUD.read()
        categories_schemas = [CategoryReadSchema.from_orm(category) for category in categories]
        return categories_schemas

    @staticmethod
    def create_category_form(title: str = Form(..., min_length=2, max_length=30)):
        category_form = CategoryCreateSchema(title=title)
        return category_form

    @staticmethod
    async def create_new_category(
            category_form: Annotated[CategoryCreateSchema, Depends(create_category_form)]) -> CategoryCreateSchema:
        result = await CategoryCRUD.create(category_form)
        return result

    @staticmethod
    async def delete_category(category_id: UUID):
        result = await CategoryCRUD.delete(category_id)
        return result


class ProductLogic:
    @staticmethod
    async def create_product(
            s3_storage: Annotated[S3Client, Depends(get_s3_storage)],
            image: Annotated[UploadFile, File()],
            title: str = Form(...),
            description: str | None = Form(default=None),
            price: float = Form(...),
            discount: int | None = Form(default=None),
            category_id: UUID = Form(...),
    ) -> ProductReadSchema:
        product_id = uuid.uuid4()
        image_url = await s3_storage.upload_file(file=image, file_name=str(product_id))
        product_create_schema = ProductCreateSchema(id=product_id,
                                                    title=title,
                                                    description=description,
                                                    price=round(float(price), 2),
                                                    image=image_url,
                                                    discount=discount,
                                                    categories_id=category_id)
        new_product: ProductReadSchema = await ProductCRUD.create(product_create_schema)
        return new_product
