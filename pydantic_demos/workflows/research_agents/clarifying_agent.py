from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.durable_exec.temporal import TemporalAgent


class Clarifications(BaseModel):
    """Structured output for clarifying questions"""

    questions: list[str]
    """List of clarifying questions to ask the user"""


CLARIFYING_AGENT_PROMPT = """
Generate 2-3 concise clarifying questions to gather more context for research.

GUIDELINES:
1. **Be concise while gathering all necessary information** 
   - Ask 2-3 clarifying questions to gather more context for research
   - Make sure to gather all the information needed to carry out the research task in a concise, well-structured manner
   - Use bullet points or numbered lists if appropriate for clarity
   - Don't ask for unnecessary information, or information that the user has already provided

2. **Maintain a Friendly and Non-Condescending Tone**
   - For example, instead of saying "I need a bit more detail on Y," say, "Could you share more detail on Y?"

3. **Adhere to Safety Guidelines**
   - Only ask for information that's relevant to the research task

Focus on gathering the most important context that will significantly improve the research results.
"""


agent = Agent(
    "gpt-4o-mini",
    instructions=CLARIFYING_AGENT_PROMPT,
    name="clarifying-agent",
    output_type=Clarifications,
)

temporal_agent = TemporalAgent(agent)
