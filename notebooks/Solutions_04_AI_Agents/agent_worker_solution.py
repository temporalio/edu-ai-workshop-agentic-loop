from concurrent.futures import ThreadPoolExecutor
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.contrib.pydantic import pydantic_data_converter

async def run_agent_worker():
    client = await Client.connect(
        "localhost:7233",
        data_converter=pydantic_data_converter,
    )

    worker = Worker(
        client,
        task_queue="chaotic-agent-python-task-queue",
        workflows=[AgentWorkflow],
        activities=[create, dynamic_tool_activity],
        activity_executor=ThreadPoolExecutor(max_workers=10),
    )

    print("Starting agent worker...")
    await worker.run()
