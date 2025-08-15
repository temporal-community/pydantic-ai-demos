import asyncio

from pydantic_ai.durable_exec.temporal import PydanticAIPlugin
from temporalio.client import Client

from pydantic_demos.workflows.hello_world_workflow import PydanticHelloWorldWorkflow


async def main():
    client = await Client.connect(
        "localhost:7233",
        plugins=[PydanticAIPlugin()],
    )

    result = await client.execute_workflow(
        PydanticHelloWorldWorkflow.run,
        args=["Tell me about recursion in programming."],
        id="pydantic-hello-world-workflow-id",
        task_queue="pydantic-ai-task-queue",
    )
    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
