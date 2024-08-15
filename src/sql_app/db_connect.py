from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from src.config import DB_USER, DB_PORT, DB_PASS, DB_HOST, DB_NAME

DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

async_engine = create_async_engine(url=DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False)
