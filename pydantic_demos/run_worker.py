import asyncio
import logging

from pydantic_ai.durable_exec.temporal import AgentPlugin, PydanticAIPlugin
from temporalio.client import Client
from temporalio.worker import Worker

from pydantic_demos.workflows.hello_world_workflow import PydanticHelloWorldWorkflow
from pydantic_demos.workflows.hello_world_workflow import (
    temporal_agent as hello_world_temporal_agent,
)
from pydantic_demos.workflows.interactive_research_workflow import (
    PydanticInteractiveResearchWorkflow,
)
from pydantic_demos.workflows.research_agents.clarifying_agent import (
    temporal_agent as clarifying_temporal_agent,
)
from pydantic_demos.workflows.research_agents.pdf_generator_agent import (
    temporal_agent as pdf_generator_temporal_agent,
)
from pydantic_demos.workflows.research_agents.planner_agent import (
    temporal_agent as planner_temporal_agent,
)
from pydantic_demos.workflows.research_agents.search_agent import (
    temporal_agent as search_temporal_agent,
)
from pydantic_demos.workflows.research_agents.triage_agent import (
    temporal_agent as triage_temporal_agent,
)
from pydantic_demos.workflows.research_agents.writer_agent import (
    temporal_agent as writer_temporal_agent,
)
from pydantic_demos.workflows.research_bot_workflow import PydanticResearchWorkflow
from pydantic_demos.workflows.tools_workflow import PydanticToolsWorkflow
from pydantic_demos.workflows.tools_workflow import (
    temporal_agent as tools_temporal_agent,
)


async def main():
    logging.basicConfig(level=logging.INFO)

    client = await Client.connect(
        "localhost:7233",
        plugins=[PydanticAIPlugin()],
    )

    worker = Worker(
        client,
        task_queue="pydantic-ai-task-queue",
        workflows=[
            PydanticHelloWorldWorkflow,
            PydanticToolsWorkflow,
            PydanticResearchWorkflow,
            PydanticInteractiveResearchWorkflow,
        ],
        plugins=[
            AgentPlugin(hello_world_temporal_agent),
            AgentPlugin(tools_temporal_agent),
            AgentPlugin(planner_temporal_agent),
            AgentPlugin(search_temporal_agent),
            AgentPlugin(writer_temporal_agent),
            AgentPlugin(triage_temporal_agent),
            AgentPlugin(clarifying_temporal_agent),
            AgentPlugin(pdf_generator_temporal_agent),
        ],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
