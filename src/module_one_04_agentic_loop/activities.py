import json
import os

from temporalio import activity

from models import ToolDefinition, AgentGoal


@activity.defn
async def agent_validate_prompt(
    agent_goal: AgentGoal,
    user_prompt: str,
    llm_model: str,
    llm_api_key: str
) -> bool:
        """Validate that the user's prompt aligns with the agent's capabilities.
        
        This ensures the request matches what the agent can do with its available tools.
        """
        from litellm import completion
        
        # Build a description of what the agent can do
        capabilities = f"Agent: {agent_goal.agent_name}\n"
        capabilities += f"Purpose: {agent_goal.description}\n"
        capabilities += "Available tools:\n"
        for tool in agent_goal.tools:
            capabilities += f"  - {tool.name}: {tool.description}\n"
        
        validation_prompt = f"""Given this agent's capabilities:
{capabilities}

And this user request:
"{user_prompt}"

Can this agent fulfill this request with its available tools? 
Respond with only YES or NO."""
        
        response = completion(
            model=llm_model,
            messages=[{"role": "user", "content": validation_prompt}],
            temperature=0.1,
            api_key=llm_api_key
        )
        
        result = response.choices[0].message.content.strip().upper()
        activity.logger.info(f"Prompt validation result: {result}")
        
        return "YES" in result


@activity.defn
async def ai_select_tool_with_params(
    goal: str | AgentGoal,  # Can accept either a string or AgentGoal
    available_tools: dict[str, ToolDefinition], 
    context: str,
    llm_model: str,
    llm_api_key: str
) -> dict[str, str | dict[str, str | int]]:
        """AI agent selects tool AND extracts parameters in one call.
        """
        from litellm import completion
    
        if isinstance(goal, AgentGoal):
            agent_goal = goal
            goal_text = agent_goal.description
            # Use the agent's tools if provided, otherwise use passed tools
            if agent_goal.tools:
                tools_to_use = {tool.name: tool for tool in agent_goal.tools}
            else:
                tools_to_use = available_tools
        else:
            agent_goal = None
            goal_text = goal
            tools_to_use = available_tools
        
        # Build tool descriptions with parameters
        tools_description = []
        for name, tool_def in tools_to_use.items():
            if isinstance(tool_def, ToolDefinition):
                tool_str = f"Tool: {name}\n"
                tool_str += f"Description: {tool_def.description}\n"
                tool_str += "Arguments: " + ", ".join(
                    [f"{arg.name} ({arg.type}): {arg.description}" for arg in tool_def.arguments]
                )
                tools_description.append(tool_str)
        
        tools_text = "\n\n".join(tools_description)
        
        # Build prompt with optional AgentGoal context
        if agent_goal:
            # Use richer context from AgentGoal
            prompt = f"""{agent_goal.starter_prompt if agent_goal.starter_prompt else ''}

You are {agent_goal.agent_name if agent_goal.agent_name else 'an AI agent'}.
Goal: {goal_text}

{f"Example interactions: {agent_goal.example_conversation_history}" if agent_goal.example_conversation_history else ""}

Available tools:
{tools_text}

Current context:
{context if context else "Just starting - no actions taken yet"}

Based on the goal and context, decide the next action.
Return a JSON object with:
- "tool": the tool name to use (or "DONE" if complete)  
- "parameters": an object with the required parameters

Return ONLY the JSON object."""
        else:
            # Simple prompt for string goal
            prompt = f"""You are an AI agent working to achieve this goal: {goal_text}

Available tools:
{tools_text}

Current context:
{context if context else "Just starting - no actions taken yet"}

Based on the goal and context, decide the next action.
Return a JSON object with:
- "tool": the tool name to use (or "DONE" if complete)
- "parameters": an object with the required parameters

Examples:
{{"tool": "search_flights", "parameters": {{"origin": "NYC", "destination": "London", "date": "March 15"}}}}
{{"tool": "book_flight", "parameters": {{"flight_id": "AA123", "seat_class": "economy"}}}}
{{"tool": "DONE", "parameters": {{}}}}

Return ONLY the JSON object."""
        
        response = completion(
            model=llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            api_key=llm_api_key
        )
        
        decision_text = response.choices[0].message.content.strip()
        activity.logger.info(f"AI decision: {decision_text}")
        
        # Remove markdown code blocks if present
        if decision_text.startswith("```"):
            # Remove starting ```json or ```
            decision_text = decision_text.split("\n", 1)[1] if "\n" in decision_text else decision_text[3:]
            # Remove ending ```
            if decision_text.endswith("```"):
                decision_text = decision_text[:-3].strip()
        
        try:
            return json.loads(decision_text)
        except json.JSONDecodeError:
            if "DONE" in decision_text.upper():
                return {"tool": "DONE", "parameters": {}}
            return {"tool": decision_text, "parameters": {}}

# Tool activities - register each tool as a separate activity
@activity.defn(name="search_flights")
async def search_flights_activity(params: dict) -> str:
    """Activity wrapper for search_flights tool."""
    from tools import search_flights
    return await search_flights(params)

@activity.defn(name="check_seat_availability")
async def check_seat_availability_activity(params: dict) -> str:
    """Activity wrapper for check_seat_availability tool."""
    from tools import check_seat_availability
    return await check_seat_availability(params)

@activity.defn(name="calculate_total_cost")
async def calculate_total_cost_activity(params: dict) -> str:
    """Activity wrapper for calculate_total_cost tool."""
    from tools import calculate_total_cost
    return await calculate_total_cost(params)

@activity.defn(name="book_flight")
async def book_flight_activity(params: dict) -> str:
    """Activity wrapper for book_flight tool."""
    from tools import book_flight
    return await book_flight(params)

@activity.defn(name="send_confirmation") 
async def send_confirmation_activity(params: dict) -> str:
    """Activity wrapper for send_confirmation tool."""
    from tools import send_confirmation
    return await send_confirmation(params)