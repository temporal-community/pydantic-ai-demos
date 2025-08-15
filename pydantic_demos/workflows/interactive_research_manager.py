from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Optional

from temporalio import workflow

from pydantic_demos.workflows.research_agents.clarifying_agent import (
    temporal_agent as clarifying_agent,
)
from pydantic_demos.workflows.research_agents.pdf_generator_agent import (
    temporal_agent as pdf_generator_agent,
)
from pydantic_demos.workflows.research_agents.planner_agent import (
    WebSearchItem,
    WebSearchPlan,
)
from pydantic_demos.workflows.research_agents.planner_agent import (
    temporal_agent as planner_agent,
)
from pydantic_demos.workflows.research_agents.search_agent import (
    temporal_agent as search_agent,
)
from pydantic_demos.workflows.research_agents.triage_agent import (
    temporal_agent as triage_agent,
)
from pydantic_demos.workflows.research_agents.writer_agent import ReportData
from pydantic_demos.workflows.research_agents.writer_agent import (
    temporal_agent as writer_agent,
)


@dataclass
class ClarificationResult:
    """Result from initial clarification check"""

    needs_clarifications: bool
    questions: Optional[list[str]] = None
    research_output: Optional[str] = None
    report_data: Optional[ReportData] = None


class PydanticInteractiveResearchManager:
    """Interactive research manager using Pydantic AI agents"""

    def __init__(self):
        # Agents are already instantiated as temporal_agents in their modules
        pass

    async def run(self, query: str, use_clarifications: bool = False) -> str:
        """
        Run research with optional clarifying questions flow

        Args:
            query: The research query
            use_clarifications: If True, uses multi-agent flow with clarifying questions
        """
        if use_clarifications:
            # This method is for backwards compatibility, just use direct flow
            report = await self._run_direct(query)
            return report.markdown_report
        else:
            report = await self._run_direct(query)
            return report.markdown_report

    async def _run_direct(self, query: str) -> ReportData:
        """Original direct research flow"""
        workflow.logger.info(f"Starting direct research for: {query}")

        search_plan = await self._plan_searches(query)
        search_results = await self._perform_searches(search_plan)
        report = await self._write_report(query, search_results)

        return report

    async def run_with_clarifications_start(self, query: str) -> ClarificationResult:
        """Start clarification flow and return whether clarifications are needed"""
        workflow.logger.info(f"Starting clarification check for: {query}")

        # Use triage agent to determine if clarifications are needed
        triage_result = await triage_agent.run(query)
        triage_output = triage_result.output

        workflow.logger.info(
            f"Triage decision: needs_clarifications={triage_output.needs_clarifications}"
        )

        if triage_output.needs_clarifications:
            # Generate clarifying questions
            clarifications_result = await clarifying_agent.run(query)
            clarifications = clarifications_result.output

            return ClarificationResult(
                needs_clarifications=True, questions=clarifications.questions
            )
        else:
            # No clarifications needed, continue with research
            workflow.logger.info(
                "No clarifications needed, proceeding with direct research"
            )
            search_plan = await self._plan_searches(query)
            search_results = await self._perform_searches(search_plan)
            report = await self._write_report(query, search_results)
            return ClarificationResult(
                needs_clarifications=False,
                research_output=report.markdown_report,
                report_data=report,
            )

    async def run_with_clarifications_complete(
        self, original_query: str, questions: list[str], responses: dict[str, str]
    ) -> ReportData:
        """Complete research using clarification responses"""
        workflow.logger.info(
            f"Completing research with clarifications for: {original_query}"
        )

        # Enrich the query with clarification responses
        enriched_query = self._enrich_query(original_query, questions, responses)

        workflow.logger.info(f"Enriched query: {enriched_query}")

        # Now run the full research pipeline with the enriched query
        search_plan = await self._plan_searches(enriched_query)
        search_results = await self._perform_searches(search_plan)
        report = await self._write_report(enriched_query, search_results)

        return report

    def _enrich_query(
        self, original_query: str, questions: list[str], responses: dict[str, str]
    ) -> str:
        """Combine original query with clarification responses"""
        enriched = f"Original query: {original_query}\n\nAdditional context from clarifications:\n"
        for i, question in enumerate(questions):
            answer = responses.get(f"question_{i}", "No specific preference")
            enriched += f"- {question}: {answer}\n"
        return enriched

    async def _plan_searches(self, query: str) -> WebSearchPlan:
        """Plan web searches using the planner agent"""
        workflow.logger.info(f"Planning searches for: {query}")

        result = await planner_agent.run(f"Query: {query}")
        search_plan = result.output

        workflow.logger.info(f"Generated {len(search_plan.searches)} search queries")
        return search_plan

    async def _perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        """Perform web searches in parallel"""
        workflow.logger.info(f"Performing {len(search_plan.searches)} web searches")

        num_completed = 0
        tasks = [
            asyncio.create_task(self._search(item)) for item in search_plan.searches
        ]
        results = []
        for task in workflow.as_completed(tasks):
            result = await task
            if result is not None:
                results.append(result)
            num_completed += 1
            workflow.logger.info(
                f"Completed search {num_completed}/{len(search_plan.searches)}"
            )

        workflow.logger.info(f"Completed all searches, got {len(results)} results")
        return results

    async def _search(self, item: WebSearchItem) -> str | None:
        """Perform a single web search"""
        input_str = f"Search term: {item.query}\nReason for searching: {item.reason}"
        try:
            result = await search_agent.run(input_str)
            return result.output
        except Exception as e:
            workflow.logger.warning(f"Search failed for '{item.query}': {e}")
            return None

    async def _write_report(self, query: str, search_results: list[str]) -> ReportData:
        """Generate the final research report"""
        workflow.logger.info("Writing research report")

        input_str = (
            f"Original query: {query}\nSummarized search results: {search_results}"
        )

        # Generate markdown report
        result = await writer_agent.run(input_str)
        report_data = result.output

        workflow.logger.info("Research report completed")
        return report_data

    async def _generate_pdf_report(self, report_data: ReportData) -> str | None:
        """Generate PDF from markdown report, return file path"""
        try:
            workflow.logger.info("Generating PDF report")

            pdf_result = await pdf_generator_agent.run(
                f"Convert this markdown report to PDF:\n\n{report_data.markdown_report}"
            )

            pdf_output = pdf_result.output
            if pdf_output.success:
                workflow.logger.info(
                    f"PDF generated successfully: {pdf_output.pdf_file_path}"
                )
                return pdf_output.pdf_file_path
            else:
                workflow.logger.warning(
                    f"PDF generation failed: {pdf_output.error_message}"
                )
        except Exception as e:
            workflow.logger.warning(f"PDF generation failed with exception: {e}")

        return None
