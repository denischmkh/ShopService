import datetime
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Type, Any, AsyncGenerator, Iterable
from uuid import UUID
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from routers.auth.schemas import UserCreateSchema, UserDatabaseSchema, UserReadSchema, UserLoginSchema
from routers.email.schemas import CreateVerificationCode
from routers.store.schemas import CategoryCreateSchema, CategoryReadSchema, ProductCreateSchema, ProductReadSchema
from routers.store.utils import make_products_read_schema
from .db_connect import AsyncSessionLocal
from .models import Base, User, Product, Category, Basket, VerificationCode
from pydantic import BaseModel
import sqlalchemy as _sql
from fastapi.exceptions import HTTPException
from .dependencies import verify_password, get_password_hash


async def session_generator() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


# Context manager to get session
@asynccontextmanager
async def get_session() -> AsyncSession:
    async for session in session_generator():
        try:
            async with session.begin():
                yield session
        finally:
            await session.close()


############################################################################
#              Abstract class to give an example for child class           #
############################################################################

class BaseCRUD(ABC):
    """ Every child class must contain his SQLAlchemy model to interact with her """
    __db_model = Type[Base]

    @classmethod
    @abstractmethod
    async def create(cls, pydantic_schema: Type[BaseModel]) -> Any:
        """ Create new record by using pydantic model """
        ...

    @classmethod
    @abstractmethod
    async def read(cls, **kwargs) -> Any:
        """ Read record """
        ...

    @classmethod
    @abstractmethod
    async def delete(cls, **kwargs) -> Any:
        """ Delete record """
        ...


class UserCRUD(BaseCRUD):
    """ Controlling interaction with User """
    __db_model = User

    @classmethod
    async def read(cls, user_id: UUID | None = None, username: str | None = None,
                   email: str | None = None) -> User | None:
        async with get_session() as session:
            if user_id or username or email:
                stmt = _sql.select(cls.__db_model).where(
                    _sql.or_(cls.__db_model.username == username, cls.__db_model.id == user_id,
                             cls.__db_model.email == email))
            else:
                return None
            result = await session.execute(stmt)
            user: User = result.scalars().first()
            if user is None:
                return user
            return user

    @classmethod
    async def create(cls, user_create_schema: UserCreateSchema) -> UserDatabaseSchema:
        async with get_session() as session:
            existing_user: UserReadSchema | None = await cls.read(username=user_create_schema.username)
            if existing_user:
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Username already exists')
            existing_user_email: UserReadSchema | None = await cls.read(email=user_create_schema.email)
            if existing_user_email:
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Email already exists')
            hashed_password = get_password_hash(user_create_schema.password)
            user_database_schema = UserDatabaseSchema(**user_create_schema.dict(), hashed_password=hashed_password)
            new_user = cls.__db_model(
                **user_database_schema.dict(),
            )
            session.add(new_user)
            await session.commit()
            return user_database_schema

    @classmethod
    async def delete(cls, user_id: UUID) -> UserReadSchema | None:
        async with get_session() as session:
            stmt = _sql.select(cls.__db_model).where(cls.__db_model.id == user_id)
            result = await session.execute(stmt)
            user: User = result.scalars().first()
            if user is None:
                return user
            delete_stmt = _sql.delete(cls.__db_model).where(cls.__db_model.id == user_id)
            await session.execute(delete_stmt)
            return user

    @classmethod
    async def get_all_users(cls, page: int = 1, per_page: int = 10) -> list[UserReadSchema]:
        async with get_session() as session:
            stmt = _sql.select(cls.__db_model).offset((page - 1) * per_page).limit(per_page)
            result = await session.execute(stmt)
            users_models = result.scalars().all()
            users = [UserReadSchema.from_orm(user) for user in users_models]
            return users

    @classmethod
    async def verify_user(cls, user_data: UserLoginSchema) -> UserReadSchema | None:
        async with get_session() as session:
            if user_data.username:
                stmt = _sql.select(cls.__db_model).where(cls.__db_model.username == user_data.username)
            elif user_data.email:
                stmt = _sql.select(cls.__db_model).where(cls.__db_model.email == user_data.email)
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Missing username or email')
            result = await session.execute(stmt)
            user: User = result.scalars().first()
            if not user:
                return None
            verify: bool = verify_password(password=user_data.password, hashed_password=user.hashed_password)
            if not verify:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect password')
            return user

    @classmethod
    async def ban_user(cls, user_id: UUID) -> UserReadSchema:
        async with get_session() as session:
            stmt = _sql.select(cls.__db_model).where(cls.__db_model.id == user_id)
            result = await session.execute(stmt)
            user: User = result.scalars().first()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
            if not user.active:
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='User already banned')
            stmt = _sql.update(cls.__db_model).where(cls.__db_model.id == user_id).values(active=False)
            await session.execute(stmt)
            await session.commit()
        async with get_session() as session:
            stmt = _sql.select(cls.__db_model).where(cls.__db_model.id == user_id)
            result = await session.execute(stmt)
            user: User = result.scalars().first()
            return user

    @classmethod
    async def unban_user(cls, user_id: UUID) -> User:
        async with get_session() as session:
            stmt = _sql.select(cls.__db_model).where(cls.__db_model.id == user_id)
            result = await session.execute(stmt)
            user: User = result.scalars().first()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
            if user.active:
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='User already unbanned')
            stmt = _sql.update(cls.__db_model).where(cls.__db_model.id == user_id).values(active=True)
            await session.execute(stmt)
            await session.commit()
        async with get_session() as session:
            stmt = _sql.select(cls.__db_model).where(cls.__db_model.id == user_id)
            result = await session.execute(stmt)
            user: User = result.scalars().first()
            return user

    @classmethod
    async def verifying_user(cls, user_id: UUID) -> User:
        async with get_session() as session:
            stmt = _sql.update(cls.__db_model).where(cls.__db_model.id == user_id).values(verified_email=True)
            await session.execute(stmt)
            await session.commit()

        async with get_session() as session:
            stmt = _sql.select(cls.__db_model).where(cls.__db_model.id == user_id)
            result = await session.execute(stmt)
            user = result.scalars().first()
            return user


class VerifyCodeCRUD(BaseCRUD):
    """ Verification Codes """
    __db_model = VerificationCode

    @classmethod
    async def create(cls, code_schema: CreateVerificationCode) -> CreateVerificationCode:
        async with get_session() as session:
            stmt = _sql.select(cls.__db_model).where(cls.__db_model.users_id == code_schema.users_id)
            result = await session.execute(stmt)
            code_record = result.scalars().first()
            if not code_record:
                stmt = _sql.insert(cls.__db_model).values(**code_schema.dict())
                await session.execute(stmt)
                return code_schema
            else:
                stmt_delete_old = _sql.delete(cls.__db_model).where(cls.__db_model.users_id == code_schema.users_id)
                await session.execute(stmt_delete_old)
                await session.commit()
                await session.close()
                async with get_session() as session:
                    stmt = _sql.insert(cls.__db_model).values(**code_schema.dict())
                    await session.execute(stmt)
            return code_schema

    @classmethod
    async def read(cls, user_schema: UserReadSchema) -> int:
        async with get_session() as session:
            stmt = _sql.select(cls.__db_model).where(cls.__db_model.users_id == user_schema.id)
            result = await session.execute(stmt)
            verify_code: VerificationCode = result.scalars().first()
            if not verify_code or datetime.datetime.utcnow() > verify_code.expire_to:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail='Code invalid or expired, please request a new code')
            return int(verify_code.verify_code)

    @classmethod
    async def delete(cls, user_schema: UserReadSchema) -> UserReadSchema:
        async with get_session() as session:
            stmt = _sql.delete(cls.__db_model).where(cls.__db_model.id == user_schema.id)
            await session.execute(stmt)
            await session.commit()
            return user_schema


class CategoryCRUD(BaseCRUD):
    __db_model = Category

    @classmethod
    async def create(cls, category_create_schema: CategoryCreateSchema) -> CategoryCreateSchema:
        async with get_session() as session:
            stmt = _sql.select(cls.__db_model).where(cls.__db_model.title == category_create_schema.title)
            request = await session.execute(statement=stmt)
            result = request.scalars().first()
            if result:
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Category already exist')
            stmt = _sql.insert(cls.__db_model).values(**category_create_schema.dict())
            await session.execute(statement=stmt)
            return category_create_schema

    @classmethod
    async def read(cls, category_id: UUID) -> CategoryReadSchema:
        async with get_session() as session:
            stmt = _sql.select(cls.__db_model).where(cls.__db_model.id == category_id)
            result = await session.execute(stmt)
            category = result.scalars().first()
            if not category:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found!')
            return CategoryReadSchema.from_orm(category)

    @classmethod
    async def delete(cls, category_id: UUID) -> CategoryReadSchema | None:
        async with get_session() as session:
            stmt = _sql.select(cls.__db_model).where(cls.__db_model.id == category_id)
            result = await session.execute(stmt)
            category_schema: Category = result.scalars().first()
            if not category_schema:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found!')
            delete_stmt = _sql.delete(cls.__db_model).where(cls.__db_model.id == category_id)
            await session.execute(delete_stmt)
            return category_schema

    @classmethod
    async def get_all_categories(cls) -> list[CategoryReadSchema]:
        async with get_session() as session:
            stmt = _sql.select(cls.__db_model)
            result = await session.execute(stmt)
            categories = result.scalars().all()
            parsed_categories = [CategoryReadSchema.from_orm(category) for category in categories]
            return parsed_categories


class ProductCRUD(BaseCRUD):
    __db_model = Product

    @classmethod
    async def create(cls, product_schema: ProductCreateSchema) -> ProductReadSchema:
        async with get_session() as session:
            try:
                stmt = _sql.insert(Product).values(**product_schema.dict())
                await session.execute(stmt)
                product_price_with_discount = round((product_schema.price / 100) * (100 - product_schema.discount),
                                                    2) if product_schema.discount else None
                created_product_schema = ProductReadSchema(**product_schema.dict(),
                                                           price_with_discount=product_price_with_discount)
                return created_product_schema
            except:
                await session.rollback()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Something not wrong!')

    @classmethod
    async def read(cls, product_id: UUID) -> ProductReadSchema:
        async with get_session() as session:
            stmt = _sql.select(Product).where(Product.id == product_id)
            request = await session.execute(stmt)
            result = request.scalars().first()
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found!')
            product_schema = make_products_read_schema(result)
            return product_schema

    @classmethod
    async def delete(cls, product_id: UUID) -> ProductReadSchema:
        async with get_session() as session:
            stmt_get = _sql.select(Product).where(Product.id == product_id)
            request = await session.execute(stmt_get)
            result = request.scalars().first()
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found!')
            stmt_delete = _sql.delete(Product).where(Product.id == product_id)
            await session.execute(stmt_delete)
            product_schema = make_products_read_schema(result)
            return product_schema

    @classmethod
    async def get_all_products(cls, page: int = 1, per_page: int = 10) -> list[ProductReadSchema]:
        async with get_session() as session:
            stmt = _sql.select(cls.__db_model).offset((page - 1) * per_page).limit(per_page)
            result = await session.execute(stmt)
            products = result.scalars().all()
            return [make_products_read_schema(product) for product in products]