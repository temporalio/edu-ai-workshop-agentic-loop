from temporalio import workflow

@workflow.defn(sandboxed=False) # sandboxed=False is a Notebook only requirement. You normally don't do this)
class GenerateReportWorkflow:
    def __init__(self) -> None:
        self._current_prompt: str = ""
        # Instance variable to store Signal data
        self._user_decision: UserDecisionSignal = UserDecisionSignal(decision=UserDecision.WAIT)

    # Define the Signal handler
    @workflow.signal
    async def user_decision_signal(self, decision_data: UserDecisionSignal) -> None:
        # Update instance variable when Signal is received
        self._user_decision = decision_data

    @workflow.run
    async def run(self, input: GenerateReportInput) -> GenerateReportOutput:
      self._current_prompt = input.prompt

      llm_call_input = LLMCallInput(
          prompt=self._current_prompt,
          llm_api_key=input.llm_api_key,
          llm_model=input.llm_research_model,
      )
      # rest of code here