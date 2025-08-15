from __future__ import annotations

import asyncio

from temporalio import workflow

from pydantic_demos.workflows.research_agents.planner_agent import (
    WebSearchItem,
    WebSearchPlan,
)
from pydantic_demos.workflows.research_agents.planner_agent import (
    temporal_agent as planner_temporal_agent,
)
from pydantic_demos.workflows.research_agents.search_agent import (
    temporal_agent as search_temporal_agent,
)
from pydantic_demos.workflows.research_agents.writer_agent import ReportData
from pydantic_demos.workflows.research_agents.writer_agent import (
    temporal_agent as writer_temporal_agent,
)


class PydanticSimpleResearchManager:
    def __init__(self):
        self.search_agent = search_temporal_agent
        self.planner_agent = planner_temporal_agent
        self.writer_agent = writer_temporal_agent

    async def run(self, query: str) -> str:
        search_plan = await self._plan_searches(query)
        search_results = await self._perform_searches(search_plan)
        report = await self._write_report(query, search_results)
        return report.markdown_report

    async def _plan_searches(self, query: str) -> WebSearchPlan:
        result = await self.planner_agent.run(f"Query: {query}")
        return result.output

    async def _perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
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
        return results

    async def _search(self, item: WebSearchItem) -> str | None:
        input_str = f"Search term: {item.query}\nReason for searching: {item.reason}"
        try:
            result = await self.search_agent.run(input_str)
            return str(result.output)
        except Exception:
            return None

    async def _write_report(self, query: str, search_results: list[str]) -> ReportData:
        input_str = (
            f"Original query: {query}\nSummarized search results: {search_results}"
        )

        result = await self.writer_agent.run(input_str)
        return result.output
