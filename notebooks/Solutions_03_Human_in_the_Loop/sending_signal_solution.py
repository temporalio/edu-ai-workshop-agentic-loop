async def send_user_decision_signal(client: Client, workflow_id: str) -> None:
  loop = asyncio.get_running_loop() # We usually do not need this
  handle = client.get_workflow_handle(workflow_id) # Get a handle on the Workflow Execution we want to send a Signal to.

  while True:
      print("\n" + "=" * 80)
      print(
          "Research is complete! The response will output in the terminal window with the Worker running. What would you like to do?"
      )
      print("1. Type 'keep' to approve the research and create PDF")
      print("2. Type 'edit' to modify the research")
      print("=" * 80)

      # When running input in async code, run in an executor to not block the event loop
      decision = await loop.run_in_executor(None, input, "Your decision (keep/edit/query): ")
      decision = decision.strip().lower()

      if decision in {"keep", "1"}:
          signal_data = UserDecisionSignal(decision=UserDecision.KEEP)
          await handle.signal("user_decision_signal", signal_data) # Send our Keep Signal to our Workflow Execution we have a handle on
          print("Signal sent to keep research and create PDF")
          break
      if decision in {"edit", "2"}:
          additional_prompt_input = input("Enter additional instructions for the research (optional): ").strip()
          additional_prompt = additional_prompt_input if additional_prompt_input else ""

          signal_data = UserDecisionSignal(decision=UserDecision.EDIT, additional_prompt=additional_prompt)
          # TODO Send our Signal to our Workflow Execution we have a handle on
          print("Signal sent to regenerate research")

      else:
          print("Please enter either 'keep', 'edit'")