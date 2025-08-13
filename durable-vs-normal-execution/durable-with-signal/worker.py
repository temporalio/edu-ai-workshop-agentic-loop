import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from activities import GenerateReportActivities
from workflow import GenerateReportWorkflow

async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("LiteLLM").setLevel(logging.WARNING) 
    
    client = await Client.connect("localhost:7233", namespace="default")
    # Run the Worker
    activities = GenerateReportActivities()
    worker: Worker = Worker(
        client,
        task_queue="durable",
        workflows=[GenerateReportWorkflow],
        activities=[activities.perform_research, activities.create_pdf_activity],
    )
    logging.info(f"Starting the worker....")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())