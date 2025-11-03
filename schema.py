from pydantic import BaseModel
from typing import List, Optional

class Ingredient(BaseModel):
    name: str
    quantity: float 
    unit: Optional[str] = ""
    
class RecipeInput(BaseModel):
    title: str
    original_servings: int
    target_servings: int
    ingredients: List[Ingredient]
    instructions: Optional[str] = ""
    
class AdjustedIngredient(BaseModel):
    name: str
    quantity: float
    unit: str
    converted_amount: Optional[float]
    converted_unit: Optional[str]
    
class RecipeOutput(BaseModel):
    title: str
    original_servings: int
    target_servings: int
    adjusted_ingredients: List[AdjustedIngredient]
    instructions: Optional[str]
    
class RecipeParseRequest(BaseModel):
    ingredient_text: str
    servings: int = 1