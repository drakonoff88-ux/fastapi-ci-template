import pytest
from httpx import AsyncClient
from main import app
from database import Base, engine


@pytest.fixture(autouse=True, scope="module")
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_create_recipe():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/recipes/",
            json={
                "title": "Борщ",
                "cook_time": 90,
                "ingredients": ["Свекла", "Капуста", "Картофель"],
                "description": "Вкусный украинский борщ",
            },
        )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Борщ"
    assert data["views"] == 0


@pytest.mark.asyncio
async def test_read_recipes():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/recipes/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["title"] == "Борщ"


@pytest.mark.asyncio
async def test_read_recipe_detail():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/recipes/1")
    assert response.status_code == 200
    data = response.json()
    assert data["views"] == 1  # просмотр увеличился
