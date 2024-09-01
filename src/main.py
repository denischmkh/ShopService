from fastapi import FastAPI, APIRouter
from routers.auth.router import router as users_routers
from routers.store.category_router import router as categories_router
from routers.store.product_router import router as products_router

app = FastAPI(debug=False, title="API Service for shop", prefix='/api')

store_routers = APIRouter(prefix='/store')
store_routers.include_router(categories_router)
store_routers.include_router(products_router)

routers = [users_routers, store_routers]



for router in routers:
    app.include_router(router)





