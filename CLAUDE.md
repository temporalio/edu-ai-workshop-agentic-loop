# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Temporal workshop demonstrating the difference between normal execution and durable execution for AI/LLM workloads. The project showcases how Temporal provides durability, fault tolerance, and human-in-the-loop capabilities for LLM-based applications.

## Repository Structure

The main demonstration code is in `src/` with three implementations:
- `src/module_one_01_ai_agent/` - Traditional Python execution without durability
- `src/module_one_02_adding_durability/` - Temporal-based durable execution with automatic retries
- `src/module_one_03_human_in_the_loop/` - Temporal with human-in-the-loop using Signals

## Required Setup

### Python Environment
This project requires Python 3.13. Install with uv:
```bash
uv python install 3.13
uv sync
```

### Configuration
Create a `config.py` file in the root directory:
```python
OPENAI_API_KEY = "your-openai-api-key"
```

## Development Commands

The project uses `just` for development automation:

```bash
just check          # Run all checks (lint, format-check, typecheck)
just fix            # Auto-fix linting and formatting issues
just lint           # Run ruff linter with fixes
just format         # Format code with ruff
just format-check   # Check formatting without changes
just typecheck      # Run mypy type checking
just clean          # Remove Python cache files
just install        # Install production dependencies
just install-dev    # Install all dependencies including dev
just temporal       # Start Temporal development server
just demo-1         # Run the AI Agent demo (module 1)
just demo-2         # Run the durable execution starter (module 2)
just demo-2-worker  # Run the worker for module 2
```

## Dependencies

Key libraries:
- `temporalio` - Temporal Python SDK for durable workflows
- `litellm` - LLM abstraction layer for OpenAI calls
- `reportlab` - PDF generation
- `uv` - Package manager and Python version management
- `ruff` - Fast Python linter and formatter
- `mypy` - Static type checking (strict mode enabled)

## Running the Demos

### Normal Execution Demo (Module 1)
```bash
just demo-1
# OR manually:
uv run src/module_one_01_ai_agent/app.py
```

### Durable Execution Demo (Module 2)
Terminal 1 - Start Temporal server:
```bash
just temporal
# OR manually:
temporal server start-dev --ui-port 8080
```

Terminal 2 - Run worker:
```bash
just demo-2-worker
# OR manually:
uv run src/module_one_02_adding_durability/worker.py
```

Terminal 3 - Start workflow:
```bash
just demo-2
# OR manually:
uv run src/module_one_02_adding_durability/starter.py
```

### Human-in-the-Loop Demo (Module 3)
Terminal 1 - Temporal server (if not already running):
```bash
just temporal
```

Terminal 2 - Run worker:
```bash
uv run src/module_one_03_human_in_the_loop/worker.py
```

Terminal 3 - Start workflow:
```bash
uv run src/module_one_03_human_in_the_loop/starter.py
```

## Key Architectural Concepts

### Normal Execution (`src/module_one_01_ai_agent/`)
- Single process execution in `app.py`
- No state persistence
- Process interruption loses all progress
- Manual retry logic needed

### Durable Execution (`src/module_one_02_adding_durability/`)
- **Workflow** (`workflow.py`): Orchestrates the execution, handles failures
- **Activities** (`activities.py`): Contains the actual business logic (LLM calls, PDF creation)
- **Worker** (`worker.py`): Executes workflows and activities
- **Starter** (`starter.py`): Initiates workflow execution
- **Models** (`models.py`): Data structures for workflow parameters
- Automatic retries with configurable policies
- State persists across worker restarts
- Activities deliberately fail first 2 attempts to demonstrate retry mechanism

### Signal-based Human-in-the-Loop (`src/module_one_03_human_in_the_loop/`)
- Extends durable execution with Temporal Signals
- Workflow waits for user decision via Signal
- User can approve research or request modifications
- Signal payload includes decision type and optional additional prompt

## Important Implementation Details

1. All activities use `@activity.defn` decorator
2. Workflows use `@workflow.defn` class decorator with `@workflow.run` method
3. Activities import unsafe operations within `workflow.unsafe.imports_passed_through()` context
4. Retry policies configured with exponential backoff
5. PDF creation activity intentionally fails first 2 attempts to demonstrate retry behavior
6. Signal handlers must be methods decorated with `@workflow.signal`
7. Type checking is strict - all modules must pass `mypy --strict` with specific overrides for external libraries
8. Code formatting enforced by `ruff` with 120 character line limit

## Temporal Web UI

Access at http://localhost:8080 when Temporal server is running to:
- View workflow executions
- Monitor activity retries
- Inspect workflow history
- Debug execution issues