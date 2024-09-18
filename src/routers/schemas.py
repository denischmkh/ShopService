from pydantic import BaseModel, field_validator, Field
import uuid
import datetime
from fastapi.exceptions import HTTPException


#####################################################
#      Schemas to create and read Categories        #
#####################################################


class CategoryReadSchema(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class CategoryCreateSchema(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    title: str = Field(min_length=2, max_length=30)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


#####################################################
#      Schemas to create and read Products          #
#####################################################

class ProductCreateSchema(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    title: str = Field(min_length=2, max_length=30)
    description: str | None = Field(max_length=300)
    price: float
    image: str
    discount: int | None = Field(None)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    categories_id: uuid.UUID

    @field_validator('price', mode='before')
    @classmethod
    def validate_price(cls, price: float):
        if price < 0:
            raise HTTPException(status_code=422, detail='Price must be a positive value.')

        if price > 9999999.99:
            raise HTTPException(status_code=422, detail='Price exceeds the maximum allowed value of 9999999.99')

        if round(price, 2) != price:
            raise HTTPException(status_code=422, detail='Price must have at most two decimal places.')

        return price

    @field_validator('discount', mode='before')
    @classmethod
    def validate_discount(cls, value):
        if value is not None:
            if value < 0 or value > 99:
                raise HTTPException(status_code=422, detail='Discount must be between 0 and 99, or None.')
        return value


class ProductReadSchema(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    price: float
    image: str
    discount: int | None
    created_at: datetime.datetime
    categories_id: uuid.UUID


#####################################################
#      Schemas to create and read Basket            #
#####################################################

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
