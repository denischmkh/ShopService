from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse
from fastapi.exceptions import RequestValidationError
from starlette import status

from routers.auth.router import router as users_routers
from routers.store.category_router import router as categories_router
from routers.store.product_router import router as products_router
from routers.email.router import router as email_router

store_routers = APIRouter(prefix='/store')
store_routers.include_router(categories_router)
store_routers.include_router(products_router)

routers = [users_routers, email_router, store_routers]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


app = FastAPI(debug=False, title="API Service for shop", openapi_prefix='/api', lifespan=lifespan)

for router in routers:
    app.include_router(router)

@app.exception_handler(RequestValidationError)
async def exception_handler(request: Request, exc: RequestValidationError):
    response = PlainTextResponse(content=f'Source not found! Please check parameters: {exc.args} {exc.body}',
                                 status_code=status.HTTP_404_NOT_FOUND)
    return response

@app.exception_handler(HTTPException)
async def remake_exception(request: Request, exc: HTTPException):
    response = PlainTextResponse(content=f'{exc.detail}', status_code=exc.status_code)
    return response