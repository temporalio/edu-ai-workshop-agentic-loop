# Set the instance variable of the user decision to default to WAIT
# Run this code block to load it into the program
from temporalio import workflow

# sandboxed=False is a Notebook only requirement. You normally don't do this
@workflow.defn(sandboxed=False)
class GenerateReportWorkflow:
    def __init__(self) -> None:
        self._current_prompt: str = ""
        # Instance variable to store Signal data
        self._user_decision: UserDecisionSignal = UserDecisionSignal(decision=UserDecision.WAIT) # TODO Set the default state of the user decision to be WAIT

    @workflow.run
    async def run(self, input: GenerateReportInput) -> GenerateReportOutput:
      self._current_prompt = input.prompt

      llm_call_input = LLMCallInput(prompt=self._current_prompt)
      # rest of code