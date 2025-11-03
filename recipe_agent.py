from uuid import uuid4
from pydantic import ValidationError
import traceback  

from models_a2a import TaskResult, TaskStatus, Artifact, MessagePart, A2AMessage
from adjuster import adjust_recipe, parse_ingredients_text
from schema import RecipeInput, RecipeParseRequest
from daily_tips import get_daily_tip


class RecipeAgent:

    def __init__(self):
        print("Recipe Agent Initialized.")

    async def process_message(self, message: A2AMessage) -> TaskResult:
        """
        Processes a single user message and returns a complete, final task result.
        """
        task_id = message.taskId or str(uuid4())
        data_payload = None
        
        text_payload = None
        for part in message.parts:
            if part.kind == "text":
                text_payload = part.text.strip()
                break
        
        if text_payload:
            # This is a message from a user in a chat
            text_lower = text_payload.lower()
            
            # --- Task 1: Check for Greetings  ---
            if text_lower in ["hi", "hello", "help", "info", "start"]:
                response_text = (
                    "Hello! I'm the Recipe Adjuster Agent. Here's what I can do:\n\n"
                    "1.  **Get a tip:** Just type `tip`\n"
                    "2.  **Parse ingredients:** Type `parse 2 cups flour and 1 egg`\n"
                    "3.  **Adjust a full recipe:** Paste the recipe's full JSON data."
                )
                return self._build_completed_task(
                    task_id=task_id,
                    response_text=response_text,
                    artifacts=[] 
                )

            # --- Task 2: Check for "tip" command ---
            if text_lower in ["tip", "get daily tip", "daily tip"]:
                data_payload = {"task": "get_daily_tip"}
            
            # --- Task 3: Check for "parse" command ---
            elif text_lower.startswith("parse "):
                ingredient_string = text_payload[6:].strip()
                data_payload = {
                    "ingredient_text": ingredient_string,
                    "servings": 1 
                }
                
            # --- Task 4: Check if it's JSON for "adjust" task ---
            else:
                try:
                    data_payload = json.loads(text_payload)
                except json.JSONDecodeError:
                    return self._build_error_task(task_id, 
                        "Sorry, I didn't understand. Please try:\n" +
                        "- `tip` (for a daily tip)\n" +
                        "- `parse 2 cups of flour` (to parse ingredients)\n" +
                        "- (Or paste the full JSON for adjusting a recipe)")
        
        else:
            for part in message.parts:
                if part.kind == "data":
                    data_payload = part.data
                    break

        if not data_payload:
            return self._build_error_task(task_id, "No 'data' or valid 'text' part found in message.")
        
        try:
            # --- Task 1: Check for 'get_daily_tip' ---
            if data_payload.get("task") == "get_daily_tip":
                tip = get_daily_tip()
                response_text = "Here's your daily cooking tip!"
                return self._build_completed_task(
                    task_id=task_id,
                    response_text=response_text,
                    artifacts=[Artifact(name="daily_tip", parts=[MessagePart(kind="text", text=tip)])]
                )

            # --- Task 2: Check for 'adjust_recipe' ---
            try:
                recipe_input = RecipeInput(**data_payload)
                result_data = adjust_recipe(recipe_input.model_dump())
                response_text = f"Recipe '{recipe_input.title}' adjusted for {recipe_input.target_servings} servings."
                return self._build_completed_task(
                    task_id=task_id,
                    response_text=response_text,
                    artifacts=[Artifact(name="adjusted_recipe", parts=[MessagePart(kind="data", data=result_data)])]
                )
            except ValidationError:
                pass  

            # --- Task 3: Check for 'parse_ingredients' ---
            try:
                parse_request = RecipeParseRequest(**data_payload)
                result_data = parse_ingredients_text(parse_request.ingredient_text, parse_request.servings)
                response_text = f"Successfully parsed ingredients for {parse_request.servings} servings."
                return self._build_completed_task(
                    task_id=task_id,
                    response_text=response_text,
                    artifacts=[Artifact(name="parsed_ingredients", parts=[MessagePart(kind="data", data={"ingredients": result_data})])]
                )
            except ValidationError:
                pass  

            # --- If no task matches ---
            return self._build_error_task(task_id, "The 'data' payload did not match any known task schema (adjust, parse, or get_daily_tip).")

        except Exception as e:
            error_details = traceback.format_exc()
            print(f"--- INTERNAL AGENT ERROR ---\n{error_details}\n------------------------------")
            return self._build_error_task(task_id, f"An internal error occurred: {str(e)}")


    def _build_completed_task(self, task_id: str, response_text: str, artifacts: list[Artifact]) -> TaskResult:
        response_message = A2AMessage(
            role="agent",
            parts=[MessagePart(kind="text", text=response_text)],
            taskId=task_id
        )
        return TaskResult(
            id=task_id,
            contextId=task_id,
            status=TaskStatus(
                state="completed",
                message=response_message
            ),
            artifacts=artifacts,
            history=[response_message]
        )

    def _build_error_task(self, task_id: str, error_message: str) -> TaskResult:
        response_message = A2AMessage(
            role="agent",
            parts=[MessagePart(kind="text", text=f"Error: {error_message}")],
            taskId=task_id
        )
        return TaskResult(
            id=task_id,
            contextId=task_id,
            status=TaskStatus(
                state="failed",
                message=response_message
            ),
            history=[response_message]
        )