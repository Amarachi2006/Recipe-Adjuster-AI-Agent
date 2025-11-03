# Recipe Adjuster AI Agent

RecipeAdjuster AI parses and scales your recipes in seconds. Just send ingredients and servings—it returns accurate measurements, conversions, and cooking-ready data you can use instantly. This agent is built with FastAPI and can be interacted with via a simple API or as an A2A-compliant agent.

## Features

-   **Recipe Scaling:** Adjusts ingredient quantities from original to target servings.
-   **Ingredient Parsing:** Parses a simple string of ingredients into a structured JSON format.
-   **Unit Conversion:** Automatically converts units to metric (grams or ml) using the Spoonacular API.
-   **Daily Cooking Tips:** Get a random daily cooking tip.
-   **A2A Compliant:** Interacts as a task-oriented A2A agent.
-   **Simple API:** Provides straightforward endpoints for adjusting and parsing recipes.

## Getting Started

### Prerequisites

-   Python 3.8+
-   An API key from [Spoonacular](https://spoonacular.com/food-api)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/Recipe-Adjuster-AI-Agent.git
    cd Recipe-Adjuster-AI-Agent
    ```

2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure your environment:**
    -   Create a `.env` file in the root of the project.
    -   Add your Spoonacular API key to the `.env` file:
        ```
        SPOON_KEY=your_spoonacular_api_key
        ```

## Usage

### API Endpoints

The application runs a FastAPI server with the following endpoints:

#### `POST /adjust`

Adjusts a recipe based on the provided JSON data.

**Request Body:**

```json
{
    "title": "Classic Pancakes",
    "original_servings": 4,
    "target_servings": 8,
    "ingredients": [
        { "name": "flour", "quantity": 1.5, "unit": "cups" },
        { "name": "sugar", "quantity": 2, "unit": "tablespoons" },
        { "name": "baking powder", "quantity": 2, "unit": "teaspoons" },
        { "name": "salt", "quantity": 0.5, "unit": "teaspoons" },
        { "name": "milk", "quantity": 1.25, "unit": "cups" },
        { "name": "egg", "quantity": 1, "unit": "" },
        { "name": "butter", "quantity": 3, "unit": "tablespoons" }
    ],
    "instructions": "Mix dry ingredients, then wet. Cook on a hot griddle."
}
```

**Success Response (200 OK):**

```json
{
    "title": "Classic Pancakes",
    "original_servings": 4,
    "target_servings": 8,
    "adjusted_ingredients": [
        { "name": "flour", "quantity": 3.0, "unit": "cups", "converted_amount": 360.0, "converted_unit": "grams" },
        { "name": "sugar", "quantity": 4.0, "unit": "tablespoons", "converted_amount": 50.0, "converted_unit": "grams" },
        ...
    ],
    "instructions": "Mix dry ingredients, then wet. Cook on a hot griddle."
}
```

#### `POST /parse`

Parses a string of ingredients for a given number of servings.

**Request Body:**

```json
{
    "ingredient_text": "2 cups flour, 1 egg, and 1/2 cup of sugar",
    "servings": 2
}
```

**Success Response (200 OK):**

```json
{
    "parsed_ingredients": [
        { "name": "flour", "quantity": 4.0, "unit": "cups" },
        { "name": "egg", "quantity": 2.0, "unit": "" },
        { "name": "sugar", "quantity": 1.0, "unit": "cup" }
    ]
}
```

### A2A Agent Interaction

You can interact with the agent using the `/a2a/recipe` endpoint. The agent understands the following text commands:

-   `tip`: Get a daily cooking tip.
-   `parse <ingredients>`: Parses the ingredient string. For example: `parse 2 cups flour and 1 egg`
-   `help` or `info`: Get a list of commands.

You can also send a JSON payload to the agent to adjust a recipe.

## Configuration

-   **`SPOON_KEY`**: Your Spoonacular API key. This is required for ingredient parsing and unit conversion.
-   **`PORT`**: The port to run the FastAPI application on. Defaults to `5001`.

## Running the Application

To run the application, use the following command:

```bash
uvicorn main:app --reload
```

The application will be available at `http://127.0.0.1:5001`.
