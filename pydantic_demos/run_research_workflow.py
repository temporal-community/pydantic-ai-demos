import argparse
import asyncio
from pathlib import Path

from pydantic_ai.durable_exec.temporal import PydanticAIPlugin
from temporalio.client import Client

from pydantic_demos.workflows.research_bot_workflow import PydanticResearchWorkflow


async def main():
    parser = argparse.ArgumentParser(description="Run Pydantic AI research workflow")
    parser.add_argument(
        "query",
        nargs="?",
        default="Caribbean vacation spots in April, optimizing for surfing, hiking and water sports",
        help="Research query to execute",
    )

    args = parser.parse_args()

    # Create client connected to server at the given address
    try:
        client = await Client.connect(
            "localhost:7233",
            plugins=[PydanticAIPlugin()],
        )
        print(f"🔗 Connected to Temporal server")
    except Exception as e:
        print(f"❌ Failed to connect to Temporal server: {e}")
        print(f"   Make sure Temporal server is running on localhost:7233")
        return

    query = args.query
    print(f"🤖 Starting Pydantic AI research: {query}")
    print(f"🔍 Research in progress...")
    print(f"   📋 Planning searches")
    print(f"   🌐 Gathering information")
    print(f"   ✍️  Compiling report")
    print(f"   ⏳ Please wait...")

    # Execute a workflow with silent retry logic for network issues
    result = None
    retry_timeout = 300  # 5 minutes total
    start_time = asyncio.get_event_loop().time()

    while True:
        try:
            result = await client.execute_workflow(
                PydanticResearchWorkflow.run,
                args=[query],
                id="pydantic-research-workflow",
                task_queue="pydantic-ai-task-queue",
            )
            break  # Success, exit retry loop

        except Exception:
            # Check if we've exceeded the 5-minute timeout
            elapsed_time = asyncio.get_event_loop().time() - start_time
            if elapsed_time >= retry_timeout:
                return  # Exit silently after 5 minutes

            # Silent retry with minimal delay for fast recovery
            await asyncio.sleep(5)

    if result:
        print(f"\n🎉 Pydantic AI research completed!")

        # Save markdown report
        markdown_file = Path("pydantic_research_report.md")
        markdown_file.write_text(result.markdown_report)
        print(f"📄 Report saved to: {markdown_file}")

        print(f"\n📋 Summary: {result.short_summary}")

        print(f"\n🔍 Follow-up questions:")
        for i, question in enumerate(result.follow_up_questions, 1):
            print(f"   {i}. {question}")

        print(f"\n📄 Research Result:")
        print("=" * 60)
        print(result.markdown_report)


if __name__ == "__main__":
    asyncio.run(main())
