import datetime
import uuid

from pydantic import BaseModel, Field

from services.basket.schemas import FullBasketSchema
from services.orders.utils import OrderStatus


class OrderSchema(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    basket: FullBasketSchema
    username: str
    created: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    post_index: int
    status: OrderStatus = Field(default=OrderStatus.processing)
