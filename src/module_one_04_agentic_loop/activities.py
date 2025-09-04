import inspect
import json
import os
import sys
from typing import Sequence

from temporalio import activity, workflow
import temporalio.common

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

with workflow.unsafe.imports_passed_through():
    from litellm import completion
    from config import OPENAI_API_KEY

from models import ToolDefinition


class AgentActivities:
    @activity.defn
    async def ai_select_tool_with_params(
        self,
        goal: str, 
        available_tools: dict[str, ToolDefinition], 
        context: str
    ) -> dict[str, str | dict[str, str | int]]:
        """AI agent selects tool AND extracts parameters in one call.

        Returns: {"tool": "tool_name", "parameters": {...}}
        """
        # Build tool descriptions with parameters
        tools_description = []
        for name, tool_def in available_tools.items():
            tool_str = f"Tool: {name}\n"
            tool_str += f"Description: {tool_def.description}\n"
            tool_str += "Arguments: " + ", ".join(
                [f"{arg.name} ({arg.type}): {arg.description}" for arg in tool_def.arguments]
            )
            tools_description.append(tool_str)
        
        tools_text = "\n\n".join(tools_description)
        
        prompt = f"""You are an AI agent working to achieve this goal: {goal}

Available tools:
{tools_text}

Current context:
{context if context else "Just starting - no actions taken yet"}

Based on the goal and context, decide the next action.
Extract any parameters from the goal or context.

Return a JSON object with:
- "tool": the tool name to use (or "DONE" if complete)
- "parameters": an object with the required parameters

Examples:
{{"tool": "search_flights", "parameters": {{"origin": "NYC", "destination": "London", "date": "March 15"}}}}
{{"tool": "book_flight", "parameters": {{"flight_id": "AA123", "seat_class": "economy"}}}}
{{"tool": "DONE", "parameters": {{}}}}

Return ONLY the JSON object, no other text."""
        
        response = completion(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            api_key=OPENAI_API_KEY
        )
        
        decision_text = response.choices[0].message.content.strip()
        activity.logger.info(f"AI decision: {decision_text}")
        
        try:
            return json.loads(decision_text)
        except json.JSONDecodeError:
            if "DONE" in decision_text.upper():
                return {"tool": "DONE", "parameters": {}}
            return {"tool": decision_text, "parameters": {}}

@activity.defn(dynamic=True)
async def dynamic_tool_activity(args: Sequence[temporalio.common.RawValue]) -> str:
    """Dynamic activity handler that executes tools based on activity type.

    This activity is called dynamically when the workflow executes an activity
    with an unknown activity type. It looks up the tool handler from the registry
    and executes it with the provided arguments.
    """
    from tools import get_handler
    
    # Get the activity type which will be our tool name
    tool_name = activity.info().activity_type
    
    # Extract the arguments from the raw value
    tool_args = activity.payload_converter().from_payload(args[0].payload, dict)
    
    activity.logger.info(f"Running dynamic tool '{tool_name}' with args: {tool_args}")
    
    # Delegate to the relevant function
    handler = get_handler(tool_name)
    if inspect.iscoroutinefunction(handler):
        result = await handler(tool_args)
    else:
        result = handler(tool_args)
    
    activity.logger.info(f"Tool '{tool_name}' result: {result}")
    return result

agent_activities = AgentActivities()