import uuid

from pydantic import BaseModel, Field

from services.store.schemas import ProductReadSchema


class BasketCreateSchema(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    products_id: uuid.UUID
    users_id: uuid.UUID
    quantity: int = Field(ge=1, default=1)


class BasketReadSchema(BaseModel):
    id: uuid.UUID
    products_id: uuid.UUID
    users_id: uuid.UUID
    quantity: int

    class Config:
        from_attributes = True


class ProductInfoFromBasket(BaseModel):
    item: ProductReadSchema
    quantity: int
    full_summa: float


class FullBasketSchema(BaseModel):
    full_summa: float
    items: list[ProductInfoFromBasket]
