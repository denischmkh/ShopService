from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi import status
from fastapi.exceptions import HTTPException
from src.routers.auth.router import router as users_routers


routers = [users_routers]

app = FastAPI(debug=True, title="API Service for shop")

for router in routers:
    app.include_router(router)





