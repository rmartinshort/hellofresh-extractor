from pydantic import BaseModel
from typing import List


class Ingredient(BaseModel):
    name: str
    amount: str


class ExtractedMealTitle(BaseModel):
    title: str


class ExtractedMeal(BaseModel):
    title: str
    ingredients: List[Ingredient]
