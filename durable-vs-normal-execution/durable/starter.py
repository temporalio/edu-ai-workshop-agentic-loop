import asyncio

from workflow import GenerateReportWorkflow, GenerateReportInput
from temporalio.client import Client

async def main() -> None:
    client = await Client.connect("localhost:7233")

    print("Welcome to the Research Report Generator!")
    prompt = input("Enter your research topic or question: ").strip()

    if not prompt:
        prompt = "Give me 5 fun and fascinating facts about tardigrades. Make them interesting and educational!"
        print(f"No prompt entered. Using default: {prompt}")

    handle = await client.start_workflow(
        GenerateReportWorkflow.run,
        GenerateReportInput(prompt=prompt),
        id="generate-research-report-workflow",
        task_queue="durable",
    )

    print(f"Started workflow. Workflow ID: {handle.id}, RunID {handle.result_run_id}")
    result = await handle.result()
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())