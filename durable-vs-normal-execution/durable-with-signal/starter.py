import asyncio

from workflow import GenerateReportWorkflow, GenerateReportInput, UserDecisionSignal
from temporalio.client import Client

async def send_user_decision_signal(client: Client, workflow_id: str) -> None:
    handle = client.get_workflow_handle(workflow_id)
    
    while True:
        print("\n" + "="*50)
        print("Research is complete! The response will output in the terminal window with the Worker running. What would you like to do?")
        print("1. Type 'keep' to approve the research and create PDF")
        print("2. Type 'edit' to modify the research")
        print("="*50)
        
        decision = input("Your decision (keep/edit): ").strip().lower()
        
        if decision == "keep":
            signal_data = UserDecisionSignal(decision="keep")
            await handle.signal("user_decision_signal", signal_data)
            print("Signal sent to keep research and create PDF")
            break
        elif decision == "edit":
            additional_prompt = input("Enter additional instructions for the research (optional): ").strip()
            additional_prompt = additional_prompt if additional_prompt else None
            
            signal_data = UserDecisionSignal(
                decision="edit",
                additional_prompt=additional_prompt
            )
            await handle.signal("user_decision_signal", signal_data)
            print("Signal sent to regenerate research")
        else:
            print("Please enter either 'keep' or 'edit'")

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