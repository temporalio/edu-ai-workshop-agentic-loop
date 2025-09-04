from datetime import timedelta

from temporalio import workflow
from models import BookingResult, AgentGoal
from tools import AVAILABLE_TOOLS


@workflow.defn
class AgenticWorkflow:
    @workflow.run
    async def run(self, agent_goal: AgentGoal) -> BookingResult:
        llm_model = agent_goal.llm_model or "openai/gpt-4o-mini"
        llm_api_key = agent_goal.llm_api_key
        
        if not llm_api_key:
            raise ValueError("llm_api_key must be provided in AgentGoal")

        # Track execution context and steps
        context = ""
        steps_taken: list[str] = []
        max_iterations = 10

        workflow.logger.info(f"Starting agentic loop for goal: {agent_goal.description}")

        for iteration in range(max_iterations):
            workflow.logger.info(f"Agentic loop iteration {iteration + 1}")
            
            # Validate the current context/prompt aligns with agent capabilities
            # This is especially useful if the agent gets user input during execution
            is_valid = await workflow.execute_activity(
                "agent_validate_prompt",
                args=[agent_goal, agent_goal.description, llm_model, llm_api_key],
                start_to_close_timeout=timedelta(seconds=30),
            )
            
            if not is_valid:
                workflow.logger.warning(f"Validation failed at iteration {iteration + 1}")
                context += "\n\nValidation failed: Request outside of agent capabilities"
                steps_taken.append("Validation failed - skipping iteration")
                continue

            # AI decides which tool to use AND extracts parameters
            # Pass the goal description as string for simplicity
            decision = await workflow.execute_activity(
                "ai_select_tool_with_params",
                args=[agent_goal.description, AVAILABLE_TOOLS, context, llm_model, llm_api_key],
                start_to_close_timeout=timedelta(seconds=30),
            )

            tool_result = decision.get("tool", "")
            selected_tool = tool_result if isinstance(tool_result, str) else ""
            workflow.logger.info(f"AI selected tool: {selected_tool}")
            param_result = decision.get("parameters", {})
            parameters = param_result if isinstance(param_result, dict) else {}

            if selected_tool.upper() == "DONE":
                workflow.logger.info("AI determined goal is complete")
                break

            if selected_tool not in AVAILABLE_TOOLS:
                workflow.logger.error(f"AI selected unknown tool: {selected_tool}")
                context += f"\nError: Unknown tool '{selected_tool}'"
                continue

            workflow.logger.info(f"Executing tool: {selected_tool} with params: {parameters}")

            try:
                result: str = await workflow.execute_activity(
                    selected_tool,
                    args=[parameters],
                    start_to_close_timeout=timedelta(seconds=30),
                )

                context += f"\n\nExecuted: {selected_tool}"
                if parameters:
                    params_str = ", ".join([f"{k}={v}" for k, v in parameters.items()])
                    context += f" with ({params_str})"
                context += f"\nResult: {result}"

                # Track the step
                step_desc = f"{selected_tool}"
                if parameters:
                    step_desc += f" ({', '.join([f'{k}={v}' for k, v in parameters.items()])})"
                step_desc += f": {result[:80]}..."
                steps_taken.append(step_desc)

                workflow.logger.info(f"Tool result: {result[:200]}...")

            except Exception as e:
                error_msg = f"Error executing {selected_tool}: {e!s}"
                workflow.logger.error(error_msg)
                context += f"\n{error_msg}"
                steps_taken.append(f"{selected_tool} failed: {e!s}")

        # Prepare final result
        if not steps_taken:
            steps_taken = ["No actions were taken"]

        # Determine success based on whether booking was completed
        success = any("book_flight" in step and "failed" not in step for step in steps_taken)

        message = f"{'Successfully completed' if success else 'Partially completed'}: {agent_goal.description}"

        return BookingResult(
            message=message,
            steps_taken=steps_taken
        )