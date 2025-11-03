import sys
import uuid
from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter

async def start_agent(query: str):
    client = await Client.connect(
        "localhost:7233",
        data_converter=pydantic_data_converter,
    )

    result = await client.execute_workflow(
        AgentWorkflow.run,
        query,
        id=f"my-workflow-id-{uuid.uuid4()}",
        task_queue="chaotic-agent-python-task-queue",
    )
    print(f"Result: {result}")
    return result
