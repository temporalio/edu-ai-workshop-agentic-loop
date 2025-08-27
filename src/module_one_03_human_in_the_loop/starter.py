import asyncio

from temporalio.client import Client
from workflow import GenerateReportInput, GenerateReportWorkflow, UserDecisionSignal

async def query_research_result(client: Client, workflow_id: str) -> None:
    handle = client.get_workflow_handle(workflow_id)
    
    try:
        research_result = await handle.query(GenerateReportWorkflow.get_research_result)
        if research_result:
            print(f"Research Result: {research_result[:200]}...")  # Show first 200 chars
        else:
            print("Research Result: Not yet available")
            
    except Exception as e:
        print(f"Query failed: {e}")

async def send_user_decision_signal(client: Client, workflow_id: str) -> None:
    handle = client.get_workflow_handle(workflow_id)

    while True:
        print("\n" + "=" * 50)
        print(
            "Research is complete! The response will output in the terminal window with the Worker running. What would you like to do?"
        )
        print("1. Type 'keep' to approve the research and create PDF")
        print("2. Type 'edit' to modify the research")
        print("3. Type 'query' to check workflow status and research result. If querying, wait 5 seconds first to fetch result.")
        print("=" * 50)

        decision = input("Your decision (keep/edit/query): ").strip().lower()

        if decision == "keep":
            signal_data = UserDecisionSignal(decision="keep")
            await handle.signal("user_decision_signal", signal_data)
            print("Signal sent to keep research and create PDF")
            break
        if decision == "edit":
            additional_prompt_input = input("Enter additional instructions for the research (optional): ").strip()
            additional_prompt = additional_prompt_input if additional_prompt_input else None

            signal_data = UserDecisionSignal(decision="edit", additional_prompt=additional_prompt)
            await handle.signal("user_decision_signal", signal_data)
            print("Signal sent to regenerate research")
        elif decision == "query":
            await query_research_result(client, workflow_id)

        else:
            print("Please enter either 'keep', 'edit', or 'query'")


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

    signal_task = asyncio.create_task(send_user_decision_signal(client, handle.id))

    try:
        result = await handle.result()
        signal_task.cancel()
        print(f"Result: {result}")
    except Exception as e:
        signal_task.cancel()
        print(f"Workflow failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
