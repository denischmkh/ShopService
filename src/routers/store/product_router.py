from fastapi import APIRouter

router = APIRouter(prefix='/products', tags=['Products routers'])



@router.get("/")
async def read_items():
    return {"message": "List of items"}