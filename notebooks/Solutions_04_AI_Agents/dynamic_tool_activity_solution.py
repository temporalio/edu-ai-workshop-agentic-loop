from temporalio import activity
import inspect

# Tool handler registry - maps tool names to their functions
TOOL_HANDLERS = {
    "get_weather_alerts": get_weather_alerts,
}

@activity.defn(dynamic=True)
async def dynamic_tool_activity(args) -> str:
    """Dynamically execute any registered tool based on the activity name."""

    tool_name = activity.info().activity_type

    print(f"Executing dynamic tool: {tool_name}")

    # Get the handler function for this tool
    handler = TOOL_HANDLERS.get(tool_name)
    if not handler:
        raise ValueError(f"Unknown tool: {tool_name}")

    # Check if handler expects parameters
    sig = inspect.signature(handler)

    if len(sig.parameters) == 0:
        # Handler takes no arguments
        result = await handler() if inspect.iscoroutinefunction(handler) else handler()
    else:
        # Handler expects arguments - convert dict to the expected type
        param_type = list(sig.parameters.values())[0].annotation
        if param_type != inspect.Parameter.empty and hasattr(param_type, 'model_validate'):
            # It's a Pydantic model
            args = param_type.model_validate(args)

        result = await handler(args) if inspect.iscoroutinefunction(handler) else handler(args)

    print(f"Tool result: {result[:100]}..." if len(str(result)) > 100 else f"Tool result: {result}")
    return result
