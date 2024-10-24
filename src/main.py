from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from fastapi import FastAPI, APIRouter

from services.auth.router import router as users_routers
from services.store.category_router import router as categories_router
from services.store.product_router import router as products_router
from services.email.router import router as email_router
from services.basket.router import router as basket_router
from services.orders.router import router as order_router

store_routers = APIRouter(prefix='/store')
store_routers.include_router(categories_router)
store_routers.include_router(products_router)

routers = [users_routers, email_router, store_routers, basket_router, order_router]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


app = FastAPI(debug=False, title="API Service for shop", openapi_prefix='/api', lifespan=lifespan)

for router in routers:
    app.include_router(router)


