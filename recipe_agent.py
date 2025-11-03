# agents/recipe_agent.py

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
        for part in message.parts:
            if part.kind == "data":
                data_payload = part.data
                break

        if not data_payload:
            return self._build_error_task(task_id, "No 'data' part found in message. Please provide a data payload.")

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