from dataclasses import dataclass
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities import GenerateReportActivities


@dataclass
class GenerateReportInput:
    prompt: str


@dataclass
class UserDecisionSignal:
    decision: str
    additional_prompt: str | None = None


@workflow.defn
class GenerateReportWorkflow:
    def __init__(self) -> None:
        self._user_decision: UserDecisionSignal | None = None

    @workflow.signal
    async def user_decision_signal(self, decision_data: UserDecisionSignal) -> None:
        self._user_decision = decision_data

    @workflow.run
    async def run(self, input: GenerateReportInput) -> str:
        current_prompt = input.prompt

        while True:
            try:
                research_facts: str = await workflow.execute_activity(  # type: ignore[call-overload]
                    GenerateReportActivities.perform_research,
                    current_prompt,
                    start_to_close_timeout=timedelta(seconds=30),
                )

                print("Research complete!")
                print(f"Research content: {research_facts}")

                print("Waiting for user decision. Send signal with 'keep' to create PDF or 'edit' to modify research.")
                await workflow.wait_condition(lambda: self._user_decision is not None)

                user_decision = self._user_decision
                self._user_decision = None

            except Exception as e:
                workflow.logger.error(f"Research failed: {e}")
                return f"Failed to generate research: {e}"
            else:
                assert user_decision is not None  # Guaranteed by wait_condition above
                if user_decision.decision == "keep":
                    print("User approved the research. Creating PDF...")
                    break
                if user_decision.decision == "edit":
                    print("User requested research modification.")
                    if user_decision.additional_prompt:
                        current_prompt = f"{input.prompt}\n\nAdditional instructions: {user_decision.additional_prompt}"
                        print(f"Regenerating research with updated prompt: {current_prompt}")
                    else:
                        print("No additional instructions provided. Regenerating with original prompt.")
                        current_prompt = input.prompt
                    continue
                workflow.logger.error(f"Invalid decision received: {user_decision.decision}")
                return f"Invalid decision received: {user_decision.decision}"

        try:
            pdf_filename: str = await workflow.execute_activity(  # type: ignore[call-overload]
                GenerateReportActivities.create_pdf_activity,
                research_facts,
                start_to_close_timeout=timedelta(seconds=20),
                retry_policy=RetryPolicy(
                    initial_interval=timedelta(seconds=1),
                    maximum_attempts=3,
                    backoff_coefficient=2.0,
                ),
            )

        except Exception as e:
            workflow.logger.error(f"PDF generation failed: {e}")
            return f"Failed to create PDF: {e}"
        else:
            return f"Successfully created research report PDF: {pdf_filename}"
