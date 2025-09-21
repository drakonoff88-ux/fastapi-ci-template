from typing import List

from pydantic import BaseModel


# ---------------- Базовая модель ----------------
class RecipeBase(BaseModel):
    title: str
    cook_time: int
    ingredients: List[str]
    description: str


# ---------------- Для создания ----------------
class RecipeCreate(RecipeBase):
    pass


# ---------------- Для вывода ----------------
class Recipe(RecipeBase):
    id: int
    views: int

    model_config = {"from_attributes": True}  # Pydantic v2


# Чтобы старые импорты работали
RecipeOut = Recipe
