from temporalio import workflow
from datetime import timedelta
import json

@workflow.defn(sandboxed=False)
class AgentWorkflow:
    @workflow.run
    async def run(self, input: str) -> str:

        input_list = [{"type": "message", "role": "user", "content": input}]

        while True:

            print(80 * "=")

            # consult the LLM
            result = await workflow.execute_activity(
                create,
                OpenAIResponsesRequest(
                    model="gpt-4o-mini",
                    instructions=HELPFUL_AGENT_SYSTEM_INSTRUCTIONS,
                    input=input_list,
                    tools=get_tools(),
                ),
                start_to_close_timeout=timedelta(seconds=30),
            )

            item = result.output[0]

            if item.type == "function_call":
                result = await self._handle_function_call(item, result, input_list)

                # add the tool call result to the input list for context
                input_list.append({"type": "function_call_output",
                                    "call_id": item.call_id,
                                    "output": result})

            else:
                print(f"No tools needed, responding with a message: {result.output_text}")
                return result.output_text


    async def _handle_function_call(self, item, result, input_list):
        # serialize the LLM output - the decision the LLM made to call a tool
        i = result.output[0]
        input_list += [
            i.model_dump() if hasattr(i, "model_dump") else i
        ]
        # execute dynamic activity with the tool name chosen by the LLM
        args = json.loads(item.arguments) if isinstance(item.arguments, str) else item.arguments

        result = await workflow.execute_activity(
            item.name,
            args,
            start_to_close_timeout=timedelta(seconds=30),
        )

        print(f"Made a tool call to {item.name}")

        return result
