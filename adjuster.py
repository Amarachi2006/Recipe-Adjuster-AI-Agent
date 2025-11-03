import os
import requests
from dotenv import load_dotenv

load_dotenv()
SPOON_KEY = os.getenv("SPOON_KEY")

def convert_with_spoonacular(name: str, amount: float, unit: str, target_unit: str = None):
    if not SPOON_KEY:
        raise ValueError("SPOON_KEY is not set in environment variables.")
    
    if not unit or unit.strip() == "":
        return None, None
    
    food_lower = name.lower()
    if any(x in food_lower for x in ["milk", "water", "oil", "juice", "cream"]):
        target_unit = "ml"
    elif any(x in food_lower for x in ["flour", "sugar", "rice", "salt", "powder", "spice"]):
        target_unit = "grams"
    else:
        target_unit = "grams"
        
    url = "https://api.spoonacular.com/recipes/convert"
    params = {
        "ingredientName": name,
        "sourceAmount": amount,
        "sourceUnit": unit,
        "targetUnit": target_unit,
        "apiKey": SPOON_KEY
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Spoonacular API error: {response.status_code} - {response.text}")
    data = response.json()
    return data.get("targetAmount"), data.get("targetUnit")

def adjust_recipe(data):
    scale = data["target_servings"] / data["original_servings"]
    adjusted = []
    
    for ingredient in data["ingredients"]:
        new_quantity = ingredient["quantity"] * scale
        converted_amount, converted_unit = convert_with_spoonacular(
            ingredient["name"], new_quantity, ingredient.get("unit", ""))
        adjusted.append({
            "name": ingredient["name"],
            "quantity": round(new_quantity, 2),
            "unit": ingredient.get("unit", ""),
            "converted_amount": round(converted_amount, 2) if converted_amount else None,
            "converted_unit": converted_unit
        })
        
    return {
        "title": data["title"],
        "original_servings": data["original_servings"],
        "target_servings": data["target_servings"],
        "adjusted_ingredients": adjusted,
        "instructions": data.get("instructions", "")
    }
    
def parse_ingredients_text(ingredient_text: str, servings: int = 1 ):
    url = "https://api.spoonacular.com/recipes/parseIngredients"
    params = {
        "apiKey": SPOON_KEY
    }

    data = {
        "ingredientList": ingredient_text,
        "servings": servings
    }
    
    response = requests.post(url, params=params, data=data)
    if response.status_code != 200:
        raise Exception(f"Spoonacular API error: {response.status_code} - {response.text}")
    
    parsed_data = response.json()
    adjusted_data = []
    for item in parsed_data:
        name = item.get("name", "")
        base_amount = item.get("amount", 0)
        unit = item.get("unit", "")
        adjusted_amount = base_amount * servings  # scale quantity manually
        adjusted_data.append({
            "name": name,
            "quantity": adjusted_amount,
            "unit": unit
        })

    return adjusted_data