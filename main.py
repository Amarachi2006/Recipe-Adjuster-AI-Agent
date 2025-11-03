# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from models_a2a import JSONRPCRequest, JSONRPCResponse

from recipe_agent import RecipeAgent
from schema import RecipeInput, RecipeParseRequest
from adjuster import adjust_recipe, parse_ingredients_text
from daily_tips import get_daily_tip

load_dotenv()

recipe_agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup"""
    global recipe_agent
    recipe_agent = RecipeAgent()
    yield

app = FastAPI(
    title="Recipe Adjuster AI Agent",
    description="An A2A-compliant agent for scaling and parsing recipes.",
    version="1.0.0",
    lifespan=lifespan
)



@app.post("/a2a/recipe")
async def a2a_endpoint(request: Request):
    """Main A2A endpoint for the recipe agent"""
    try:
        body = await request.json()
        
        if body.get("jsonrpc") != "2.0" or "id" not in body:
            pass
        
        rpc_request = JSONRPCRequest(**body)
        
        if rpc_request.method != "message/send":
            pass

        result = await recipe_agent.process_message(
            message=rpc_request.params.message
        )
        
        return {
            "jsonrpc": "2.0",
            "id": rpc.request.id,
            "result": result.model_dump(exclude_none=True)
        }

    except Exception as e:
        import traceback
        print("A2A ERROR:", traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": body.get("id") if "body" in locals() else None,
                "error": {"code": -32603, "message": "Internal error", "data": {"details": str(e)}}
            }
        )


@app.post("/adjust")
def adjust_endpoint(recipe: RecipeInput):
    adjusted_recipe = adjust_recipe(recipe.model_dump())
    return adjusted_recipe

@app.post("/parse")
def parse_endpoint(request: RecipeParseRequest):
    data = request.model_dump()
    ingredient_text = data.get("ingredient_text", "")
    servings = data.get("servings", 1)
    parsed = parse_ingredients_text(ingredient_text, servings)
    return {"parsed_ingredients": parsed}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 5001))
    uvicorn.run(app, host="0.0.0.0", port=port)