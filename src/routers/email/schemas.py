import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from routers.email.utils import create_verify_code, verify_code_expire


class CreateVerificationCode(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    verify_code: int = Field(default_factory=create_verify_code)
    users_id: uuid.UUID
    expire_to: datetime = Field(default_factory=verify_code_expire)


class ReadVerificationCode(BaseModel):
    id: uuid.UUID
    verify_code: int
    users_id: uuid.UUID
    expire_to: datetime
    class Config:
        from_attributes = True