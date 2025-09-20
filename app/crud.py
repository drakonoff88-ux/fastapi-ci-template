from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from models_schemas import Recipe
from schemas import RecipeCreate


async def get_recipes(db: AsyncSession):
    result = await db.execute(
        select(Recipe).order_by(desc(Recipe.views), Recipe.cook_time)
    )
    return result.scalars().all()


async def get_recipe(db: AsyncSession, recipe_id: int):
    recipe = await db.get(Recipe, recipe_id)
    if recipe:
        recipe.views += 1
        await db.commit()
        await db.refresh(recipe)
    return recipe


async def create_recipe(db: AsyncSession, recipe: RecipeCreate):
    db_recipe = Recipe(
        title=recipe.title,
        cook_time=recipe.cook_time,
        ingredients="|".join(recipe.ingredients),
        description=recipe.description,
    )
    db.add(db_recipe)
    await db.commit()
    await db.refresh(db_recipe)
    return db_recipe
