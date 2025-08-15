from pydantic_ai import Agent
from pydantic_ai.durable_exec.temporal import TemporalAgent
from temporalio import workflow

agent = Agent(
    "gpt-4",
    instructions="You only respond in haikus.",
    name="Assistant",
)

temporal_agent = TemporalAgent(agent)


@workflow.defn
class PydanticHelloWorldWorkflow:
    @workflow.run
    async def run(self, prompt: str) -> str:
        result = await temporal_agent.run(prompt)
        return result.output
