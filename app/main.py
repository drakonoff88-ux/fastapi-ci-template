from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text
from app.schemas import Recipe, RecipeCreate

DATABASE_URL = "sqlite+aiosqlite:///./recipes.db"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
# Base = declarative_base()
Base = declarative_base()

# ---------------- Модель ----------------
class RecipeModel(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    cook_time = Column(Integer, nullable=False)
    ingredients = Column(Text, nullable=False)  # будем хранить как строку
    description = Column(Text, nullable=False)
    views = Column(Integer, default=0)


# ---------------- Lifespan ----------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


# ---------------- Dependency ----------------
async def get_db():
    async with async_session() as session:
        yield session


# ---------------- Endpoints ----------------
@app.post("/recipes/", response_model=Recipe, status_code=status.HTTP_201_CREATED)
async def create_recipe(recipe: RecipeCreate, db: AsyncSession = Depends(get_db)):
    db_recipe = RecipeModel(
        title=recipe.title,
        cook_time=recipe.cook_time,
        ingredients=",".join(recipe.ingredients),
        description=recipe.description,
    )
    db.add(db_recipe)
    await db.commit()
    await db.refresh(db_recipe)
    return Recipe(
        id=db_recipe.id,
        title=db_recipe.title,
        cook_time=db_recipe.cook_time,
        ingredients=db_recipe.ingredients.split(","),
        description=db_recipe.description,
        views=db_recipe.views,
    )
# @app.post("/recipes/", response_model=Recipe)
# async def create_recipe(recipe: RecipeCreate, db: AsyncSession = Depends(get_db)):
#     db_recipe = RecipeModel(
#         title=recipe.title,
#         cook_time=recipe.cook_time,
#         ingredients=",".join(recipe.ingredients),
#         description=recipe.description,
#     )
#     db.add(db_recipe)
#     await db.commit()
#     await db.refresh(db_recipe)
#     return Recipe(
#         id=db_recipe.id,
#         title=db_recipe.title,
#         cook_time=db_recipe.cook_time,
#         ingredients=db_recipe.ingredients.split(","),
#         description=db_recipe.description,
#         views=db_recipe.views,
#     )


@app.get("/recipes/", response_model=List[Recipe])
async def get_recipes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RecipeModel))
    recipes = result.scalars().all()
    # сортировка по views, затем по cook_time
    recipes_sorted = sorted(recipes, key=lambda r: (-r.views, r.cook_time))
    return [
        Recipe(
            id=r.id,
            title=r.title,
            cook_time=r.cook_time,
            ingredients=r.ingredients.split(","),
            description=r.description,
            views=r.views,
        )
        for r in recipes_sorted
    ]


@app.get("/recipes/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RecipeModel).where(RecipeModel.id == recipe_id))
    recipe = result.scalar_one_or_none()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # увеличиваем просмотры
    recipe.views += 1
    await db.commit()
    await db.refresh(recipe)

    return Recipe(
        id=recipe.id,
        title=recipe.title,
        cook_time=recipe.cook_time,
        ingredients=recipe.ingredients.split(","),
        description=recipe.description,
        views=recipe.views,
    )
