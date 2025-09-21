from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import Column, Integer, String, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.future import select

from app.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запуск: создание таблиц
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Завершение: можно добавить код очистки


app = FastAPI(lifespan=lifespan)


# Определяем модель Recipe
class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    cook_time = Column(Integer)
    ingredients = Column(String)
    description = Column(String)
    views = Column(Integer, default=0)


# Создаем асинхронную сессию с правильными параметрами
async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


@app.get("/recipes/{recipe_id}")
async def read_recipe(recipe_id: int, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(Recipe).where(Recipe.id == recipe_id))
    recipe = result.scalars().first()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Обновляем счетчик просмотров
    await session.execute(
        update(Recipe).where(Recipe.id == recipe_id).values(views=Recipe.views + 1)
    )
    await session.commit()

    return recipe
