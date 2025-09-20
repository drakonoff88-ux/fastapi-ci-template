from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from main import get_db, RecipeModel  # импорт модели и сессии
from models_schemas import RecipeOut, RecipeCreate

router = APIRouter()


@router.post("/recipes/", response_model=RecipeOut)
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
    return RecipeOut(
        id=db_recipe.id,
        title=db_recipe.title,
        cook_time=db_recipe.cook_time,
        ingredients=db_recipe.ingredients.split(","),
        description=db_recipe.description,
        views=db_recipe.views,
    )


@router.get("/recipes/", response_model=list[RecipeOut])
async def get_recipes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RecipeModel))
    recipes = result.scalars().all()
    recipes_sorted = sorted(recipes, key=lambda r: (-r.views, r.cook_time))
    return [
        RecipeOut(
            id=r.id,
            title=r.title,
            cook_time=r.cook_time,
            ingredients=r.ingredients.split(","),
            description=r.description,
            views=r.views,
        )
        for r in recipes_sorted
    ]


@router.get("/recipes/{recipe_id}", response_model=RecipeOut)
async def get_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RecipeModel).where(RecipeModel.id == recipe_id))
    recipe = result.scalar_one_or_none()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    recipe.views += 1
    await db.commit()
    await db.refresh(recipe)

    return RecipeOut(
        id=recipe.id,
        title=recipe.title,
        cook_time=recipe.cook_time,
        ingredients=recipe.ingredients.split(","),
        description=recipe.description,
        views=recipe.views,
    )
