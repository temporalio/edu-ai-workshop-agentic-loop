import asyncio
from datetime import timedelta
from dataclasses import dataclass

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities import GenerateReportActivities

@dataclass
class GenerateReportInput:
    prompt: str

@workflow.defn
class GenerateReportWorkflow:

    @workflow.run
    async def run(self, input: GenerateReportInput) -> str:
        
        try:
            research_facts = await workflow.execute_activity(
                GenerateReportActivities.perform_research,
                input.prompt,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_attempts=3,
                    backoff_coefficient=2.0, 
                )
            )
            
            print("Research complete!")
            
            await asyncio.sleep(3)
            
        except Exception as e:
            workflow.logger.error(f"Research failed: {e}")
            return f"Failed to generate research: {e}"
        
        print("Starting PDF creation...")
        print("Kill the worker process (Ctrl+C) in the next 10 seconds to test durability!")
        print("Then restart the Worker.")
        
        # Give time to kill worker before starting PDF activity
        await asyncio.sleep(10)
        
        try:
            pdf_filename = await workflow.execute_activity(
                GenerateReportActivities.create_pdf_activity,
                research_facts,
                start_to_close_timeout=timedelta(seconds=20),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_attempts=3,
                    backoff_coefficient=2.0,
                )
            )
            
            return f"Successfully created research report PDF: {pdf_filename}"
        
        except Exception as e:
            workflow.logger.error(f"PDF generation failed: {e}")
            return f"Failed to create PDF: {e}"