import pytest
from httpx import AsyncClient
from main import Base, app, get_db  # если main.py в той же папке
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Создаём движок и сессии для тестов
TEST_DATABASE_URL = "module_26_fastapi/homework/recipes.db"  # файл на диске

engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Переопределяем get_db для тестов
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


# Фикстура для создания и удаления таблиц
@pytest.fixture(autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # создаём таблицы
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # очищаем после тестов


# Клиент для тестов
@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
