# Research Agent Components

This directory contains research agent components used by two distinct research workflows in this demo project. The agents demonstrate different patterns of orchestration, from simple linear execution to complex multi-agent interactions with user clarifications.

## Two Research Workflows

This project includes two research workflows that showcase different levels of complexity:

### Basic Research Workflow
- **File**: `../research_bot_workflow.py`
- **Manager**: `../simple_research_manager.py` (PydanticSimpleResearchManager)
- **Purpose**: Demonstrates simple agent orchestration in a linear pipeline
- **Usage**: `uv run pydantic_demos/run_research_workflow.py "your research query"`

### Interactive Research Workflow  
- **File**: `../interactive_research_workflow.py`
- **Manager**: `../interactive_research_manager.py` (PydanticInteractiveResearchManager)
- **Purpose**: Advanced workflow with intelligent question generation and user interaction
- **Usage**: `uv run pydantic_demos/run_interactive_research_workflow.py "your research query"`

The interactive workflow is based on patterns from the [OpenAI Deep Research API cookbook](https://cookbook.openai.com/examples/deep_research_api/introduction_to_deep_research_api_agents).

## Basic Research Flow

```
User Query → Planner Agent → Search Agent(s) → Writer Agent → Markdown Report
              (gpt-4o)        (parallel)       (o3-mini)
```

### Agent Roles in Basic Flow:

**Planner Agent** (`planner_agent.py`)
- Analyzes the user query and generates 5-20 strategic web search terms
- Uses `gpt-4o` for comprehensive search planning
- Outputs structured `WebSearchPlan` with search terms and reasoning
- Each search item includes `reason` (justification) and `query` (search term)

**Search Agent** (`search_agent.py`)
- Executes web searches using `WebSearchTool()` with required tool usage
- Produces 2-3 paragraph summaries (max 300 words) per search
- Focuses on capturing main points concisely for report synthesis
- Handles search failures gracefully and returns consolidated results
- Uses no LLM model directly - just processes search tool results

**Writer Agent** (`writer_agent.py`)
- Uses `o3-mini` model for high-quality report synthesis
- Generates comprehensive 5-10 page reports (800-2000 words)
- Returns structured `ReportData` with:
  - `short_summary`: 2-3 sentence overview
  - `markdown_report`: Full detailed report
  - `follow_up_questions`: Suggested research topics
- Creates detailed sections with analysis, examples, and conclusions

## Interactive Research Flow

```
User Query
    └──→ Triage Agent (gpt-4o-mini)
              └──→ Decision: Clarification Needed?
                            │
                ├── Yes → Clarifying Agent (gpt-4o-mini)
                │             └──→ Generate Questions
                │                          └──→ User Input
                │                                     └──→ Query Enrichment (Manager)
                │                                                   └──→ Enriched Query
                │                                                             │
                │                                                             └──→ Planner Agent (gpt-4o)
                │                                                                          ├──→ Search Agent(s) (parallel)
                │                                                                          └──→ Writer Agent (o3-mini)
                │                                                                                     └──→ PDF Generator Agent
                │                                                                                                └──→ Report + PDF
                │
                └── No → Direct Research
                               └──→ Planner Agent (gpt-4o)
                                            ├──→ Search Agent(s) (parallel)
                                            └──→ Writer Agent (o3-mini)
                                                       └──→ PDF Generator Agent
                                                                  └──→ Report + PDF
```

### Agent Roles in Interactive Flow:

**Triage Agent** (`triage_agent.py`)
- Analyzes query specificity and determines if clarifications are needed using Pydantic AI
- Routes to either clarifying questions or direct research
- Uses `gpt-4o-mini` for fast, cost-effective decision making
- Looks for vague terms, missing context, or broad requests

**Clarifying Agent** (`clarifying_agent.py`)
- Uses `gpt-4o-mini` model for question generation
- Generates 2-3 targeted questions to gather missing information
- Focuses on preferences, constraints, and specific requirements
- Returns structured output (`Clarifications` model with `questions` list)
- Integrates with Temporal workflow updates for user interaction

**Query Enrichment** (Interactive Research Manager)
- Combines original query with user responses to clarifying questions
- Implemented in `interactive_research_manager.py` via `_enrich_query()` method
- Creates enriched query with additional context from clarifications
- No separate agent required - handled by workflow orchestration layer

**PDF Generator Agent** (`pdf_generator_agent.py`)
- Uses `gpt-4o-mini` for intelligent formatting analysis and styling decisions
- Calls the `generate_pdf` activity with 30-second timeout for actual PDF creation
- Returns structured output (`PDFReportData`) including:
  - `success`: Boolean indicating generation status
  - `formatting_notes`: AI-generated notes about styling decisions
  - `pdf_file_path`: Path to generated PDF file (if successful)
  - `error_message`: Detailed error information (if failed)
- Graceful error handling with detailed feedback
- Professional PDF styling with proper typography and layout
- Files saved to `pdf_output/` directory with timestamped names

## Agent Architecture

The research agents use Pydantic AI for natural language processing with OpenAI models:

- **Consistent API**: All agents use Pydantic AI's `Agent` class with `TemporalAgent` wrapper
- **Type Safety**: Pydantic models ensure structured input/output handling
- **Tool Integration**: Seamless integration of external tools (web search) 
- **Error Handling**: Robust error handling with graceful degradation

This pattern allows complex multi-agent workflows where agents can execute independently with well-defined interfaces, enabling sophisticated research orchestration with minimal coordination overhead.

## Research Agent Components

All agents in this directory are used by one or both research workflows:

- **`planner_agent.py`** - Web search planning (used by both workflows)
- **`search_agent.py`** - Web search execution (used by both workflows)
- **`writer_agent.py`** - Report generation (used by both workflows)
- **`pdf_generator_agent.py`** - PDF generation (interactive workflow only)
- **`triage_agent.py`** - Query analysis and routing (interactive workflow only)
- **`clarifying_agent.py`** - Question generation (interactive workflow only)
- **`research_models.py`** - Pydantic models for workflow state (interactive workflow only)

## Usage Examples

### Running Basic Research
```bash
# Start worker first
uv run pydantic_demos/run_worker.py &

# Run basic research
uv run pydantic_demos/run_research_workflow.py "Best sustainable energy solutions for small businesses"
```

### Running Interactive Research
```bash
# Start worker first  
uv run pydantic_demos/run_worker.py &

# Run interactive research
uv run pydantic_demos/run_interactive_research_workflow.py "Travel recommendations for Japan"
```

The interactive workflow will ask clarifying questions like:
- What's your budget range?
- When are you planning to travel?
- What type of activities interest you most?
- Any dietary restrictions or accessibility needs?

## Model Configuration

**Cost-Optimized Models:**
- **Triage Agent**: `gpt-4o-mini` - Fast routing decisions
- **Clarifying Agent**: `gpt-4o-mini` - Question generation

**Research Models:**
- **Planner Agent**: `gpt-4o` - Complex search strategy
- **Search Agent**: Uses web search APIs (no LLM)
- **Writer Agent**: `o3-mini` - High-quality report synthesis
- **PDF Generator Agent**: `gpt-4o-mini` - PDF formatting decisions + WeasyPrint for generation

This configuration balances cost efficiency for routing/clarification logic while using more powerful models for core research tasks.