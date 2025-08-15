# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains four standalone demos showcasing Pydantic AI integrated with Temporal workflows. The project demonstrates different patterns of agent orchestration, from simple single-agent workflows to complex multi-agent research systems with interactive user clarifications.

## Key Directories

- `pydantic_demos/workflows/` - Contains all workflow implementations
  - `hello_world_workflow.py` - Simple haiku-generating agent (Pydantic AI)
  - `tools_workflow.py` - Weather tool demo (Pydantic AI)
  - `research_bot_workflow.py` - Simple research workflow using PydanticSimpleResearchManager (Pydantic AI)
  - `interactive_research_workflow.py` - Interactive research workflow using PydanticInteractiveResearchManager
  - `simple_research_manager.py` - Simplified research orchestrator for basic workflow (Pydantic AI)
  - `interactive_research_manager.py` - Interactive research orchestrator for interactive workflow (Pydantic AI)
  - `pdf_generation_activity.py` - PDF generation activity using WeasyPrint
  - `research_agents/` - Research agent components for Pydantic AI
    - `research_models.py` - Data models for research interactions
    - `triage_agent.py` - Query analysis agent
    - `clarifying_agent.py` - Question generation agent
    - `planner_agent.py` - Research planning agent
    - `search_agent.py` - Web search agent
    - `writer_agent.py` - Report writing agent
    - `pdf_generator_agent.py` - PDF generation agent
- `pydantic_demos/run_*_workflow.py` - Client runners for each demo
- `pydantic_demos/run_worker.py` - Worker that registers all Pydantic AI workflows

## Architecture Overview

### Core Components

**Temporal Workflows**: All demos use Temporal's durable execution engine for reliable orchestration. Each workflow is registered in `run_worker.py` and has a corresponding client runner.

**Pydantic AI Integration**: Uses the `pydantic-ai` package for agent integration within Temporal workflows.

**Multi-Agent Research System**: The research demos implement a sophisticated multi-agent pipeline:
- **Triage Agent**: Analyzes queries and determines if clarifications are needed
- **Clarifying Agent**: Generates follow-up questions for better research parameters
- **Planner Agent**: Creates web search plans
- **Search Agent**: Performs web searches
- **Writer Agent**: Compiles final research reports
- **PDF Generator Agent**: Converts markdown reports to professionally formatted PDFs

Note: Query enrichment (combining user responses with original queries) is handled by the Interactive Research Manager via the `_enrich_query()` method, not by a separate agent.

### Workflow Patterns

**Simple Execution Pattern**: Direct workflow execution (Hello World, Tools, Simple Research)
```python
result = await client.execute_workflow(WorkflowClass.run, args, id="workflow-id", task_queue="pydantic-ai-task-queue")
```

**Interactive Long-Running Pattern**: Used in Interactive Research
- Uses `@workflow.update` for user interactions
- Uses `@workflow.query` for status checking
- Uses `@workflow.signal` for workflow termination
- Implements `workflow.wait_condition()` for long-running workflows

### Research Manager Architecture

**PydanticSimpleResearchManager** (`simple_research_manager.py`) - Used by basic research workflow:
- **Direct Flow**: Simple planner → search → writer pipeline
- **No Clarifications**: Streamlined for demonstration purposes  
- **Agent Coordination**: Basic orchestration without user interaction
- **No PDF Generation**: Markdown-only output for simplicity

**PydanticInteractiveResearchManager** (`interactive_research_manager.py`) - Used by interactive workflow:
- **Direct Flow**: `_run_direct()` for simple research
- **Clarification Flow**: `run_with_clarifications_start()` and `run_with_clarifications_complete()` for interactive research
- **Agent Coordination**: Manages the pipeline of triage → clarification → query enrichment → planner → search → writer → PDF generation
- **PDF Generation**: Optional PDF generation with graceful degradation

### Data Models

The `research_models.py` file defines key data structures:
- `ResearchInteraction`: Tracks state of interactive research sessions
- `ClarificationInput`/`SingleClarificationInput`: User input models
- `UserQueryInput`: Initial query input model

## Development Commands

### Environment Setup
The project uses `uv` for dependency management. Always ensure dependencies are synced:

```bash
# Install dependencies
uv sync

# Development dependencies are automatically included via [dependency-groups]
```

### Running Workflows with Workers

#### Standard Workflow Execution Pattern

For any workflow, use this pattern (adjust timeout based on workflow complexity):

```bash
# Start worker in background
uv run pydantic_demos/run_worker.py &
WORKER_PID=$!
echo "Worker started with PID: $WORKER_PID"

# Wait for worker initialization
sleep [TIME]

# Run the workflow (adjust timeout as needed)
echo "Running [workflow_name] workflow..."
timeout [SECONDS] uv run pydantic_demos/run_[workflow_name]_workflow.py

# Clean up worker
echo "Workflow completed, stopping worker..."
kill $WORKER_PID 2>/dev/null || true
wait $WORKER_PID 2>/dev/null || true
echo "Worker stopped"
```

#### Specific Workflow Examples

##### Hello World Workflow (Quick test - Pydantic AI)
```bash
uv run pydantic_demos/run_worker.py &
WORKER_PID=$!
echo "Worker started with PID: $WORKER_PID"
sleep 2
echo "Running hello world workflow..."
uv run pydantic_demos/run_hello_world_workflow.py
echo "Workflow completed, stopping worker..."
kill $WORKER_PID 2>/dev/null || true
wait $WORKER_PID 2>/dev/null || true
echo "Worker stopped"
```

##### Tools Workflow (Weather demo - Pydantic AI)
```bash
uv run pydantic_demos/run_worker.py &
WORKER_PID=$!
echo "Worker started with PID: $WORKER_PID"
sleep 2
echo "Running tools workflow..."
timeout 60 uv run pydantic_demos/run_tools_workflow.py
echo "Workflow completed, stopping worker..."
kill $WORKER_PID 2>/dev/null || true
wait $WORKER_PID 2>/dev/null || true
echo "Worker stopped"
```

##### Research Workflow (Takes ~1-2 minutes - Pydantic AI)
```bash
uv run pydantic_demos/run_worker.py &
WORKER_PID=$!
echo "Worker started with PID: $WORKER_PID"
sleep 5
echo "Running research workflow..."
timeout 120 uv run pydantic_demos/run_research_workflow.py
echo "Workflow completed, stopping worker..."
kill $WORKER_PID 2>/dev/null || true
wait $WORKER_PID 2>/dev/null || true
echo "Worker stopped"
```

##### Interactive Research Workflow - Basic Mode
```bash
uv run pydantic_demos/run_worker.py &
WORKER_PID=$!
echo "Worker started with PID: $WORKER_PID"
sleep 5
echo "Running interactive research workflow..."
timeout 180 uv run pydantic_demos/run_interactive_research_workflow.py "Tell me about quantum computing"
echo "Workflow completed, stopping worker..."
kill $WORKER_PID 2>/dev/null || true
wait $WORKER_PID 2>/dev/null || true
echo "Worker stopped"
```

##### Interactive Research Workflow - With Clarifications
```bash
uv run pydantic_demos/run_worker.py &
WORKER_PID=$!
echo "Worker started with PID: $WORKER_PID"
sleep 5
echo "Running interactive research workflow..."
timeout 180 uv run pydantic_demos/run_interactive_research_workflow.py "Tell me about quantum computing"
echo "Workflow completed, stopping worker..."
kill $WORKER_PID 2>/dev/null || true
wait $WORKER_PID 2>/dev/null || true
echo "Worker stopped"
```

#### Worker Management

##### Kill All Workers (if something goes wrong)
```bash
pkill -f "run_worker.py" || true
```

##### Check for Running Workers
```bash
ps aux | grep "run_worker.py" | grep -v grep || echo "No worker processes found"
```

### Code Quality
```bash
# Format code
uv run -m black .
uv run -m isort .

# Type checking
uv run -m mypy --check-untyped-defs --namespace-packages .
uv run pyright .
```

## Key Development Patterns

### Adding New Workflows

1. Create workflow class in `pydantic_demos/workflows/`
2. Register in `run_worker.py` workflows list
3. Create client runner in `pydantic_demos/run_*_workflow.py`
4. Update README.md with new demo

### Interactive Workflow Pattern

For workflows requiring user interaction:
1. Use `@workflow.update` for user input operations
2. Use `@workflow.query` for status checking
3. Implement `workflow.wait_condition()` for long-running operations
4. Use proper state management with dataclasses

### Multi-Agent Orchestration

The research system demonstrates agent coordination:
1. Each agent has its own module in `research_agents/`
2. **PydanticSimpleResearchManager** coordinates basic pipeline (planner → search → writer)
3. **PydanticInteractiveResearchManager** coordinates complex pipeline with clarifications and PDF generation
4. Use agents directly for agent execution
5. Implement proper error handling and fallbacks
6. **PDF Generation**: Available only in interactive research workflow

## Environment Requirements

- **Python**: 3.10+
- **Temporal Server**: Must be running on `localhost:7233`
- **OpenAI API Key**: Set as `OPENAI_API_KEY` environment variable
- **Dependencies**: Managed via `uv` (see `pyproject.toml`)
- **PDF Generation Dependencies**: WeasyPrint and system libraries (optional)

### PDF Generation Setup

The research workflows support optional PDF generation using WeasyPrint. If WeasyPrint dependencies are not available, workflows gracefully degrade to markdown-only output.

#### System Dependencies by Platform

**macOS:**
```bash
# Option 1: Install WeasyPrint directly
brew install weasyprint

# Option 2: Install system dependencies for pip
brew install pango glib gtk+3 libffi
export DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib
```

**Linux (Ubuntu/Debian):**
```bash
# Option 1: Install WeasyPrint directly
sudo apt install weasyprint

# Option 2: Install system dependencies for pip
sudo apt install python3-pip libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0
```

**Linux (Fedora):**
```bash
# Option 1: Install WeasyPrint directly
sudo dnf install weasyprint

# Option 2: Install system dependencies for pip
sudo dnf install python-pip pango
```

**Windows:**
1. Install Python from Microsoft Store
2. Install MSYS2 from https://www.msys2.org/
3. In MSYS2 shell: `pacman -S mingw-w64-x86_64-pango`
4. Set environment variable: `WEASYPRINT_DLL_DIRECTORIES=C:\msys64\mingw64\bin`

#### PDF Generation Features

- **Automatic Styling**: Professional CSS styling with proper typography
- **Graceful Degradation**: Workflows continue without PDF when dependencies missing
- **File Organization**: PDFs saved to `pdf_output/` directory
- **Timestamp Naming**: Unique filenames with timestamps to avoid conflicts

## Testing Approach

When testing workflow changes:
1. Start with hello world to verify basic setup
2. Test specific workflow with appropriate timeout
3. Monitor output for serialization errors
4. Clean up workers between tests
5. Test PDF generation independently using `python test_pdf_generation.py`
6. Check `pdf_output/` directory for generated PDFs

## Workflow Timeouts by Type

- **Hello World**: 30 seconds (simple haiku generation)
- **Tools Workflow**: 60 seconds (single tool usage)
- **Simple Research**: 120 seconds (web searches + report generation)
- **Interactive Research**: 180+ seconds (includes user interaction time + PDF generation)

Note: Interactive Research may take longer due to user response time for clarifying questions. PDF generation in interactive workflow adds ~10-30 seconds depending on report length.

## Development Memories

- Remember you can check vscode for problems before running tests or code