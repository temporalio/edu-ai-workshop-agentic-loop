from temporalio import workflow
from datetime import timedelta

@workflow.defn(sandboxed=False)
class GenerateReportWorkflow:

    def __init__(self) -> None:
        self._current_prompt: str = ""
        # Instance variable to store the Signal in
        self._user_decision: UserDecisionSignal = UserDecisionSignal(decision=UserDecision.WAIT)

    # Method to handle the Signal
    @workflow.signal
    async def user_decision_signal(self, decision_data: UserDecisionSignal) -> None:
        # Update the instance variable with the received Signal data
        self._user_decision = decision_data

    @workflow.run
    async def run(self, input: GenerateReportInput) -> GenerateReportOutput:
        self._current_prompt = input.prompt

        llm_call_input = LLMCallInput(prompt=self._current_prompt)

        continue_user_input_loop = True

        while continue_user_input_loop:
            research_facts = await workflow.execute_activity(
                llm_call,
                llm_call_input,
                start_to_close_timeout=timedelta(seconds=30),
            )

            # Waiting for Signal with user decision
            await workflow.wait_condition(lambda: self._user_decision.decision != UserDecision.WAIT)

            if self._user_decision.decision == UserDecision.KEEP:
                workflow.logger.info("User approved the research. Creating PDF...")
                continue_user_input_loop = False
            elif self._user_decision.decision == UserDecision.EDIT:
                workflow.logger.info("User requested research modification.")
                if self._user_decision.additional_prompt != "":
                    self._current_prompt = (
                        f"{self._current_prompt}\n\nAdditional instructions: {self._user_decision.additional_prompt}"
                    )
                    workflow.logger.info(f"Regenerating research with updated prompt: {self._current_prompt}")
                else:
                    workflow.logger.info("No additional instructions provided. Regenerating with original prompt.")
                llm_call_input.prompt = self._current_prompt
                self._user_decision = UserDecisionSignal(decision=UserDecision.WAIT)

        pdf_generation_input = PDFGenerationInput(content=research_facts["choices"][0]["message"]["content"])

        pdf_filename: str = await workflow.execute_activity(
            create_pdf,
            pdf_generation_input,
            start_to_close_timeout=timedelta(seconds=20),
        )

        return GenerateReportOutput(result=f"Successfully created research report PDF: {pdf_filename}")