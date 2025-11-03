from temporalio import activity
from typing import Sequence
from temporalio.common import RawValue
import inspect
from pydantic import BaseModel

# Tool handler registry - maps tool names to functions
def get_handler(tool_name: str):
    if tool_name == "get_location_info":
        return get_location_info
    if tool_name == "get_ip_address":
        return get_ip_address
    if tool_name == "get_weather_alerts":
        return get_weather_alerts
    if tool_name == "get_random_number":
        return get_random_number

@activity.defn(dynamic=True)
async def dynamic_tool_activity(args: Sequence[RawValue]) -> dict:

    tool_name = activity.info().activity_type

    tool_args = activity.payload_converter().from_payload(args[0].payload, dict)
    activity.logger.info(f"Running dynamic tool '{tool_name}' with args: {tool_args}")

    handler = get_handler(tool_name)

    # Check the handler signature to determine how to call it
    sig = inspect.signature(handler)
    params = list(sig.parameters.values())

    if len(params) == 0:
        call_args = []
    else:
        ann = params[0].annotation
        if isinstance(tool_args, dict) and isinstance(ann, type) and issubclass(ann, BaseModel):
            call_args = [ann(**tool_args)]
        else:
            call_args = [tool_args]

    result = await handler(*call_args) if inspect.iscoroutinefunction(handler) else handler(*call_args)

    activity.logger.info(f"Tool '{tool_name}' result: {result}")
    return result
