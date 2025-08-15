from __future__ import annotations

from dataclasses import dataclass

from pydantic_ai import Agent
from pydantic_ai.durable_exec.temporal import TemporalAgent
from temporalio import workflow


@dataclass
class Weather:
    city: str
    temperature_range: str
    conditions: str


async def get_weather(city: str) -> Weather:
    """
    Get the weather for a given city.
    """
    return Weather(city=city, temperature_range="14-20C", conditions="Sunny with wind.")


agent = Agent(
    "gpt-4",
    instructions="You are a helpful agent.",
    name="tools-agent",
    tools=[get_weather],
)

temporal_agent = TemporalAgent(agent)


@workflow.defn
class PydanticToolsWorkflow:
    @workflow.run
    async def run(self, question: str) -> str:
        result = await temporal_agent.run(question)
        return result.output
