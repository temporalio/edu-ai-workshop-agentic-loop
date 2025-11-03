HELPFUL_AGENT_SYSTEM_INSTRUCTIONS = """
You are a helpful agent that can use tools to help the user.
You will be given a task and a list of tools to use.
You may or may not need to use the tools to complete the task.
If no tools are needed, respond in haikus.
"""

# Create the tool list for the agent
def get_tools():
    return [WEATHER_ALERTS_TOOL_OAI, 
            RANDOM_NUMBER_TOOL_OAI,
            GET_LOCATION_TOOL_OAI,
            GET_IP_ADDRESS_TOOL_OAI]