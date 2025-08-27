## Demo Draft

### Setup Instructions

Before running the demos, ensure you have the correct Python version and dependencies installed:

#### Install Python 3.13 with uv
This project requires Python 3.13. If you don't have it installed, use uv to install it:

```bash
# Install Python 3.13 using uv
uv python install 3.13

# Verify the version
uv python list
```

The project is already configured to use Python 3.13 via the `.python-version` file, so uv will automatically use the correct version when you run commands in this directory.

#### Install Dependencies
Install the project dependencies using uv:

```bash
# Install all dependencies (including dev dependencies)
uv sync
```

### Instructor Instructions 

### Normal Execution Demo
1. Demonstrate why Temporal is a great framework for LLMs first. Go in the `normal` directory and run the file with `python app.py`.
2. Enter a research topic or question in the CLI. 
3. When the countdown starts, kill the process with 'CTRL+C'.
4. Now point out that when we restart the process now, we start from the beginning - the state is lost, the LLM does not remember the prompt that you prompted it with. Point out that imagine this is a more intensive process, if you got most of the way through, you have probably utilized a good amount of tokens. If you restart, you'll have to unnecessarily use more tokens.

### Durable Execution Demo
1. We will now showcase how this is different with Temporal. Route to the `durable` directory. 
2. Open three terminal windows.
3. In one terminal window, start the Temporal server with `temporal server start-dev --ui-port 8080 --db-filename clusterdata.db`.
4. In another terminal window, run the worker with `python worker.py`. You'll see some output indicating that the Worker has been started.
5. In the third terminal window, execute your Workflow with `python starter.py`.
6. You'll be prompted to enter a research topic or question in the CLI. 
7. Once you do, in the terminal window with the Worker running, you'll see that the research has complete. Kill the process with 'CTRL+C'.
8. Now point out that when we restart the process (by rerunning the Worker with `python worker.py`), you won't lose your state or progress, you'll continue from where you left off. You'll see that the PDF report generation has continued right where you left off. You can show the PDF that will appear in the `durable` directory.
9. Also point out that you intentionally threw an error in the Activities to showcase retries. Show this both in the code and say that in our case, this is just an error we are intentionally throwing, but this could just as easily be an internal service that isn't responding or a network outage. 
10. Showcase the retries in the Web UI too. Point out that in practice, your code will continue retrying until whatever issue the activity has encountered has resolved itself, whether that is the network coming back online or an internal service starting to respond again. By leveraging the durability of Temporal and out of the box retry capabilities, you have avoided writing retry and timeout logic yourself and saved your downstream services from being unnecessarily overwhelmed.

### Human in the Loop Demo (Signals)
1. We will now showcase how we can leverage human in the loop with Temporal Signals. Route to the `durable-with-signal` directory. 
2. In one terminal window, run your Worker with `python worker.py`.
3. In another terminal window, execute your Workflow with `python starter.py`.
4. You'll be prompted to enter a research topic or question in the CLI. 
5. Once you do, in the terminal window with the Worker running, you'll see the research output. 
6. Back in the terminal window when you started your Workflow Execution, you'll see that you are prompted to choose one of the two options:
    a. Approve of this research and if you would like it to create a PDF (type 'keep' to send a Signal to the Workflow to create the PDF).
    b. Modify the research by adding extra info to the prompt (type 'edit' to modify the prompt and send another Signal to the Workflow to prompt the LLM again).
7. Demonstrate the modification by typing 'edit'.
8. Enter additional instructions and see the new output in the terminal window with your Worker running. Now type 'keep' and show that the PDF has been created.