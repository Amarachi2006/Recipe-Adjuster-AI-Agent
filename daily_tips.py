import random 
from datetime import datetime

DAILY_TIPS = [
    "Day 1: Always read your recipe fully before you start cooking.",
    "Day 2: Use a sharp knife — it’s safer and cleaner.",
    "Day 3: Salt your pasta water generously!",
    "Day 4: Taste as you cook to adjust seasoning early.",
    "Day 5: Let meat rest before cutting it.",
    "Day 6: Store herbs in water like flowers to keep them fresh.",
    "Day 7: Clean as you go — less stress at the end.",
    "Day 8: Add a splash of acid (lemon or vinegar) to brighten dishes.",
    "Day 9: Keep your cutting board steady with a damp towel.",
    "Day 10: Don’t overcrowd your pan — it prevents proper browning.",
    "Day 11: Toast nuts and spices for deeper flavor.",
    "Day 12: Save pasta water to help thicken sauces.",
    "Day 13: Chill cookie dough before baking for better texture.",
    "Day 14: Preheat pans before adding oil or food.",
    "Day 15: Use fresh garlic instead of powdered for stronger aroma.",
    "Day 16: Dry ingredients before frying for crispier results.",
    "Day 17: Don’t open the oven too often — it drops the temperature.",
    "Day 18: Use unsalted butter to control seasoning precisely.",
    "Day 19: Keep your workspace organized — mise en place matters!",
    "Day 20: Always measure baking ingredients accurately.",
    "Day 21: Deglaze pans with wine or broth for rich sauces.",
    "Day 22: Let dough rest — gluten needs time to relax.",
    "Day 23: Blanch vegetables to preserve color and nutrients.",
    "Day 24: Add salt gradually, not all at once.",
    "Day 25: Freeze leftover herbs in olive oil cubes.",
    "Day 26: Never reuse marinade as a sauce without boiling it.",
    "Day 27: Use room-temperature ingredients for even baking.",
    "Day 28: Invest in a kitchen thermometer for perfect doneness.",
    "Day 29: Cut meat against the grain for tenderness.",
    "Day 30: Keep citrus zest handy — it boosts flavor instantly.",
    "Day 31: Trust your senses — smell, sight, and taste are your best tools!"
]

def get_daily_tip():
    day = datetime.now().day
    random.seed(day)
    return random.choice(DAILY_TIPS)