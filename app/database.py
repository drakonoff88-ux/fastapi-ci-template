from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

DATABASE_URL = "sqlite+aiosqlite:///./recipes.db"

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Заменяем sessionmaker на async_sessionmaker для асинхронной работы
async_session_maker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

Base = declarative_base()


# Исправляем тип возвращаемого значения на AsyncGenerator
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.orm import declarative_base, sessionmaker
#
# DATABASE_URL = "sqlite+aiosqlite:///./recipes.db"
#
# engine = create_async_engine(DATABASE_URL, echo=True, future=True)
#
# async_session_maker = sessionmaker(
#     bind=engine,
#     expire_on_commit=False,
#     autoflush=False,
#     class_=AsyncSession,
# )
#
# Base = declarative_base()
#
#
# async def get_session() -> AsyncSession:
#     async with async_session_maker() as session:
#         yield session
