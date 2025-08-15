#!/usr/bin/env python3
"""
Client runner for Pydantic AI Interactive Research Workflow

This demonstrates the interactive research workflow with clarifying questions
using Pydantic AI agents.
"""

import argparse
import asyncio
import uuid

from pydantic_ai.durable_exec.temporal import PydanticAIPlugin
from temporalio.client import Client

from pydantic_demos.workflows.interactive_research_workflow import (
    PydanticInteractiveResearchWorkflow,
)
from pydantic_demos.workflows.research_agents.research_models import UserQueryInput


async def main():
    parser = argparse.ArgumentParser(description="Run interactive research workflow")
    parser.add_argument("query", help="Research query")
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Skip clarifying questions and do direct research (default is interactive)",
    )
    args = parser.parse_args()

    client = await Client.connect(
        "localhost:7233",
        plugins=[PydanticAIPlugin()],
    )

    workflow_id = f"pydantic-interactive-research-{uuid.uuid4()}"

    if args.non_interactive:
        # Non-interactive mode - skip clarifications and do direct research
        print(f"Starting direct research for: {args.query}")
        result = await client.execute_workflow(
            PydanticInteractiveResearchWorkflow.run,
            args=[args.query, False],  # initial_query, use_clarifications=False
            id=workflow_id,
            task_queue="pydantic-ai-task-queue",
        )

        print("\n" + "=" * 60)
        print("RESEARCH COMPLETED")
        print("=" * 60)
        print(f"\nSummary: {result.short_summary}")
        print(f"\nMarkdown Report:\n{result.markdown_report}")

        if result.follow_up_questions:
            print(f"\nFollow-up Questions:")
            for i, question in enumerate(result.follow_up_questions, 1):
                print(f"{i}. {question}")

        if result.pdf_file_path:
            print(f"\nPDF Report saved to: {result.pdf_file_path}")
        else:
            print("\nPDF generation was skipped or failed")

    else:
        # DEFAULT INTERACTIVE MODE - Always ask clarifying questions when needed
        print(f"Starting interactive research for: {args.query}")

        # Start the workflow
        handle = await client.start_workflow(
            PydanticInteractiveResearchWorkflow.run,
            args=[],  # No initial query for interactive mode
            id=workflow_id,
            task_queue="pydantic-ai-task-queue",
        )

        # Start research with the query
        print("Initializing research...")
        status = await handle.execute_update(
            PydanticInteractiveResearchWorkflow.start_research,
            UserQueryInput(query=args.query),
        )

        # Check if clarifications are needed
        if status.clarification_questions:
            print(f"\nI need some clarifications to provide better research results:")
            print("-" * 50)

            # Collect answers to clarifying questions one by one
            from pydantic_demos.workflows.research_agents.research_models import (
                SingleClarificationInput,
            )

            for i, question in enumerate(status.clarification_questions):
                print(f"\nQuestion {i + 1}: {question}")
                answer = input("Your answer: ").strip()

                if not answer:
                    answer = "No specific preference"

                # Send single clarification
                status = await handle.execute_update(
                    PydanticInteractiveResearchWorkflow.provide_single_clarification,
                    SingleClarificationInput(question_index=i, answer=answer),
                )
                print(f"✓ Answer recorded for question {i + 1}")

            print(f"\nAll clarifications collected. Starting enhanced research...")
        else:
            print("No clarifications needed. Proceeding with research...")

        # Wait for research completion
        result = await handle.result()

        print("\n" + "=" * 60)
        print("INTERACTIVE RESEARCH COMPLETED")
        print("=" * 60)
        print(f"\nOriginal Query: {args.query}")

        if status.clarification_questions:
            print("\nClarifications Provided:")
            for i, question in enumerate(status.clarification_questions):
                answer = status.clarification_responses.get(f"question_{i}", "N/A")
                print(f"Q: {question}")
                print(f"A: {answer}\n")

        print(f"Summary: {result.short_summary}")
        print(f"\nMarkdown Report:\n{result.markdown_report}")

        if result.follow_up_questions:
            print(f"\nFollow-up Questions:")
            for i, question in enumerate(result.follow_up_questions, 1):
                print(f"{i}. {question}")

        if result.pdf_file_path:
            print(f"\nPDF Report saved to: {result.pdf_file_path}")
        else:
            print("\nPDF generation was skipped or failed")


if __name__ == "__main__":
    asyncio.run(main())
