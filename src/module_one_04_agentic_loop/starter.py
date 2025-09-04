import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from models import BookingRequest
from temporalio.client import Client
from workflow import AgenticWorkflow


async def main() -> None:
    client = await Client.connect("localhost:7233")
    goal = input("What are your trip booking details? ").strip()
    if not goal:
        goal = "Book a flight from NYC to London for tomorrow"
        print(f"Using default goal: {goal}")

    # Create the request
    request = BookingRequest(goal=goal)

    print("Starting agentic workflow...")

    handle = await client.start_workflow(
        AgenticWorkflow.run,
        request,
        id="agentic-workflow",
        task_queue="agentic-queue",
    )

    result = await handle.result()

    print(result.message)
    print("\nSteps taken by AI agent:")
    for i, step in enumerate(result.steps_taken, 1):
        print(f"   {i}. {step}")

if __name__ == "__main__":
    asyncio.run(main())
