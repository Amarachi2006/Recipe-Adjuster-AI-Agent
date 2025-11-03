import os
import httpx
from dotenv import load_dotenv

load_dotenv()
SPOON_KEY = os.getenv("SPOON_KEY")

async def convert_with_spoonacular(name: str, amount: float, unit: str, target_unit: str = None):
    if not SPOON_KEY:
        raise ValueError("SPOON_KEY is not set in environment variables.")

    if not unit or unit.strip() == "":
        return None, None

    food_lower = name.lower()
    
    # Determine target unit
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
        "apiKey": SPOON_KEY,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
        
        if response.status_code != 200:
            print(f"Spoonacular API error: {response.status_code} - {response.text}")
            return None, None
            
        data = response.json()
        return data.get("targetAmount"), data.get("targetUnit")
    except Exception as e:
        print(f"HTTPX request failed: {e}")
        return None, None


async def adjust_recipe(data):
    scale = data["target_servings"] / data["original_servings"]
    adjusted = []

    for ingredient in data["ingredients"]:
        new_quantity = ingredient["quantity"] * scale
        
        converted_amount, converted_unit = await convert_with_spoonacular(
            ingredient.get("name"), new_quantity, ingredient.get("unit")
        )
        
        adjusted.append(
            {
                "name": ingredient.get("name"),
                "quantity": round(new_quantity, 2),
                "unit": ingredient.get("unit", ""),
                "converted_amount": round(converted_amount, 2) if converted_amount else None,
                "converted_unit": converted_unit,
            }
        )

    return {
        "title": data["title"],
        "original_servings": data["original_servings"],
        "target_servings": data["target_servings"],
        "adjusted_ingredients": adjusted,
        "instructions": data.get("instructions", ""),
    }

async def parse_ingredients_text(ingredient_text: str, servings: int = 1):
    if not SPOON_KEY:
        raise ValueError("SPOON_KEY is not set in environment variables.")

    url = "https://api.spoonacular.com/recipes/parseIngredients"
    params = {
        "apiKey": SPOON_KEY,
        "servings": servings
    }
    
    data = {
        'ingredientList': ingredient_text,
        'servings': servings
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, params=params, data=data)
        
        if response.status_code != 200:
            print(f"Spoonacular API error: {response.status_code} - {response.text}")
            return []

        parsed_data = response.json()
        adjusted_data = []
        
        for item in parsed_data:
            adjusted_data.append(
                {
                    "name": item.get("name", ""),
                    "quantity": item.get("amount", 0),
                    "unit": item.get("unit", ""),
                }
            )
        return adjusted_data
    except Exception as e:
        print(f"HTTPX request failed: {e}")
        return []