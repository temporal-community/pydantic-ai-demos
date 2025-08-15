from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.durable_exec.temporal import TemporalAgent


class TriageResult(BaseModel):
    """Result from triage agent indicating if clarifications are needed"""

    needs_clarifications: bool
    """Whether the query needs clarifying questions to provide better results"""

    reasoning: str
    """Explanation of the decision"""


TRIAGE_AGENT_PROMPT = """
You are a triage agent that determines if a research query needs clarifying questions to provide better results.

**IMPORTANT: You should be AGGRESSIVE about requesting clarifications. When in doubt, always choose to ask clarifying questions.**

Analyze the user's query and set needs_clarifications to TRUE if the query:
- Lacks specific details about preferences (budget, timing, style, etc.)
- Is too broad or general without specific parameters
- Would benefit from understanding user's specific needs or constraints  
- Contains vague terms like "best", "good", "nice", "where to find" without criteria
- Is location-based without specific criteria or context
- Could have multiple valid interpretations
- Would benefit from understanding user's purpose or use case

**EXAMPLES that NEED clarifications (needs_clarifications: true):**
- "where to find bears in north america" → needs clarifications about: viewing vs hunting, safety level, best times, specific regions, etc.
- "best restaurants in Melbourne" → needs clarifications about: budget, cuisine, occasion, neighborhood, etc.  
- "good places to visit in Japan" → needs clarifications about: interests, season, budget, duration, etc.
- "how to learn programming" → needs clarifications about: goals, experience level, timeline, preferred languages, etc.

**EXAMPLES that are SPECIFIC ENOUGH (needs_clarifications: false):**
- "current population of Tokyo Japan in 2024"
- "steps to install Python 3.11 on Ubuntu 22.04"
- "ingredients needed for traditional Italian carbonara recipe"
- "when was the Declaration of Independence signed"

**DEFAULT BEHAVIOR: When uncertain, always choose needs_clarifications: true**

Provide clear reasoning for your decision in the reasoning field.
"""


agent = Agent(
    "gpt-4o-mini",
    instructions=TRIAGE_AGENT_PROMPT,
    name="triage-agent",
    output_type=TriageResult,
)

temporal_agent = TemporalAgent(agent)
