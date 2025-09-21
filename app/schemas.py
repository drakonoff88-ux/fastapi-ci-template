from typing import List

from pydantic import BaseModel


class RecipeBase(BaseModel):
    title: str
    cook_time: int
    ingredients: List[str]
    description: str


class RecipeCreate(RecipeBase):
    pass


class Recipe(RecipeBase):
    id: int
    views: int

    model_config = {"from_attributes": True}  # вместо orm_mode
