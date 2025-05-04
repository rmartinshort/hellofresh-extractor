from pydantic import BaseModel, Field
from typing import List


class Ingredient(BaseModel):
    name: str
    amount: str


class ExtractedMealTitle(BaseModel):
    title: str


class ExtractedMeal(BaseModel):
    title: str
    ingredients: List[Ingredient]
    preparation_time: str
    cooking_time: str
    calories: str


class JudgeModel(BaseModel):
    winner: str = Field(
        description="Indicate which model is better. Should be 'A', 'B' or 'tie'"
    )
    reasoning: str = Field(description="Your short explanation of your choice of model")
