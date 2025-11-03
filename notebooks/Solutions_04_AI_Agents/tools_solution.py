import random
import requests

# Random number tool
RANDOM_NUMBER_TOOL_OAI: dict[str, Any] = oai_responses_tool_from_model(
    "get_random_number",
    "Get a random number between 0 and 100.",
    None)

# IP and Location tools
class GetLocationRequest(BaseModel):
    ipaddress: str = Field(description="An IP address")

GET_IP_ADDRESS_TOOL_OAI: dict[str, Any] = oai_responses_tool_from_model(
    "get_ip_address",
    "Get the IP address of the current machine.",
    None)

GET_LOCATION_TOOL_OAI: dict[str, Any] = oai_responses_tool_from_model(
    "get_location_info",
    "Get the location information for an IP address. This includes the city, state, and country.",
    GetLocationRequest)