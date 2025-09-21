import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database import Base

# from app.main import Recipe
from app.main import Recipe

# Создаем тестовую базу данных в памяти
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.mark.asyncio
async def test_create_recipe():
    # Создаем таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Тестируем создание рецепта
    async with AsyncSession(test_engine) as session:
        recipe = Recipe(
            title="Test Recipe",
            cook_time=30,
            ingredients="Test ingredients",
            description="Test description",
        )
        session.add(recipe)
        await session.commit()
        await session.refresh(recipe)

        assert recipe.id is not None
        assert recipe.title == "Test Recipe"
