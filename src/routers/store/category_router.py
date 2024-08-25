from fastapi import APIRouter

router = APIRouter(prefix='/categories', tags=['Categories routers'])


@router.get("/")
async def read_items():
    return {"message": "List of items"}