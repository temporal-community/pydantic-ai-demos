import asyncio
import uuid

from pydantic_ai.durable_exec.temporal import PydanticAIPlugin
from temporalio.client import Client

from pydantic_demos.workflows.tools_workflow import PydanticToolsWorkflow


async def main():
    client = await Client.connect(
        "localhost:7233",
        plugins=[PydanticAIPlugin()],
    )

    result = await client.execute_workflow(
        PydanticToolsWorkflow.run,
        args=["What's the weather like in San Francisco?"],
        id=f"pydantic-tools-{uuid.uuid4()}",
        task_queue="pydantic-ai-task-queue",
    )
    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
