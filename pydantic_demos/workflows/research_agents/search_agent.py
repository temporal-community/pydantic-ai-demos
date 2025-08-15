from pydantic_ai import Agent
from pydantic_ai.durable_exec.temporal import TemporalAgent

INSTRUCTIONS = (
    "You are a research assistant. Given a search term, you search the web for that term and "
    "produce a concise summary of the results. The summary must 1-2 paragraphs and less than 250 "
    "words. Capture the main points. Write succinctly, no need to have complete sentences or good "
    "grammar. This will be consumed by someone synthesizing a report, so its vital you capture the "
    "essence and ignore any fluff. Do not include any additional commentary other than the summary "
    "itself."
)


async def web_search(query: str) -> str:
    """
    Search the web for a given query and return summary results.

    Args:
        query: The search term to look up

    Returns:
        A summary of search results
    """
    # Simple mock implementation that would need to be replaced with actual web search
    # In a real implementation, this would use a service like Tavily, Google Search API, etc.
    return f"Search results for '{query}': Found relevant information about {query}, including key details, statistics, and current information. Multiple sources confirm important aspects related to the query."


agent = Agent(
    "gpt-4o",
    instructions=INSTRUCTIONS,
    name="search-agent",
    tools=[web_search],
)

temporal_agent = TemporalAgent(agent)
