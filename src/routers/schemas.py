from pydantic import BaseModel, field_validator, Field
import uuid
import datetime
from fastapi.exceptions import HTTPException


#####################################################
#      Schemas to create and read Products          #
#####################################################




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
