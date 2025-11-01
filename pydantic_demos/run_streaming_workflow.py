import asyncio
import uuid
from collections.abc import AsyncIterable
from dataclasses import dataclass
from typing import Union
import websockets

from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import (
    AgentStreamEvent,
    HandleResponseEvent,
    PartDeltaEvent,
    TextPartDelta,
)
from pydantic_ai.durable_exec.temporal import (
    AgentPlugin,
    PydanticAIPlugin,
    TemporalAgent,
    TemporalRunContext,
)

from temporalio import workflow
from temporalio.client import Client
from temporalio.worker import Worker

# Because the server code and workflow are defined in the same file (for convenience),
# we need to follow the sandboxing rules when importing libraries.
# Learn more here:
# https://docs.temporal.io/develop/python/python-sdk-sandbox#global-state-isolation
with workflow.unsafe.imports_passed_through():
    from fastapi import FastAPI, WebSocket
    import uvicorn

WEATHER_TASK_QUEUE = 'weather'

@dataclass
class WeatherDependencies:
    websocket_uri: str

async def event_stream_handler(
    ctx: TemporalRunContext[WeatherDependencies],
    event_stream: AsyncIterable[Union[AgentStreamEvent, HandleResponseEvent]],
):
    # The event_stream_handler may get invoked from the Workflow sandbox where IO is not allowed.
    # We only want to stream when it's invoked from an Activity.
    if not workflow.in_workflow():
        async with websockets.connect(ctx.deps.websocket_uri) as websocket:
            async for event in event_stream:
                # See the example below for more event types:
                # https://ai.pydantic.dev/agents/#streaming-events-and-final-output
                if isinstance(event, PartDeltaEvent) and isinstance(event.delta, TextPartDelta):
                    await websocket.send(event.delta.content_delta)

weather_agent = Agent(
    'gpt-4o',
    name='weather',
    instructions=f'Providing a weather forecast at the locations the user provides.',
    deps_type=WeatherDependencies,
    event_stream_handler=event_stream_handler
)

@weather_agent.tool
async def weather_forecast(ctx: RunContext, location: str) -> str:
    return f'The forecast in {location} is 24°C and sunny.'

temporal_agent = TemporalAgent(weather_agent)

@workflow.defn
class WeatherWorkflow:  
    @workflow.run
    async def run(self, prompt: str) -> str:
        await temporal_agent.run(
            prompt,
            deps=WeatherDependencies(websocket_uri="ws://localhost:8000/ws"),
        )

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        print(data, end="", flush=True)

async def run_workflow():
    client = await Client.connect(
        'localhost:7233',  
        plugins=[PydanticAIPlugin()],
    )

    async with Worker(
        client,
        task_queue=WEATHER_TASK_QUEUE,
        workflows=[WeatherWorkflow],
        plugins=[AgentPlugin(temporal_agent)],
    ):
        await client.execute_workflow(
            WeatherWorkflow.run,
            args=['What will the weather be like in Paris tomorrow?'],
            id=f'weather-{uuid.uuid4()}',
            task_queue=WEATHER_TASK_QUEUE,
        )

async def main():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="critical")
    server = uvicorn.Server(config)

    server_task = asyncio.create_task(server.serve())
    await run_workflow()
    server.should_exit = True
    await server_task


if __name__ == '__main__':
    asyncio.run(main())
    """
    Tomorrow in Paris, the weather will be sunny with a temperature of 24°C
    """
