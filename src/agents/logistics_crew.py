"""
logistics_crew.py
=================
Defines the two core agents (Logistics Analyst & Technical Writer),
attaches search tools, and exposes a `run_research()` function that
assembles and kicks off the CrewAI crew.

Usage
-----
    from src.agents.logistics_crew import run_research

    result = run_research(
        query="Analyze the impact of current drought conditions on Panama Canal transit times",
        output_file="20240101_1200_panama-canal-drought.md",
    )
"""

import os
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai.tools import BaseTool

# ---------------------------------------------------------------------------
# 0. Environment
# ---------------------------------------------------------------------------

load_dotenv()

_GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
_SERPER_API_KEY = os.getenv("SERPER_API_KEY")

if not _GOOGLE_API_KEY:
    raise EnvironmentError(
        "GOOGLE_API_KEY is not set. "
        "Add it to your .env file before running the agent."
    )

# ---------------------------------------------------------------------------
# 1. LLM
# ---------------------------------------------------------------------------

# FIX: was "gemini-2.5-flash" which does not exist — corrected to "gemini-2.5-flash"
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=_GOOGLE_API_KEY,
    temperature=0.3,                    # low temp = factual, consistent output
    convert_system_message_to_human=True,
)

# ---------------------------------------------------------------------------
# 2. Search Tools
# ---------------------------------------------------------------------------

class DuckDuckGoTool(BaseTool):
    """
    Free, no-API-key search tool backed by DuckDuckGo.
    Falls back to this when SERPER_API_KEY is not configured.
    """
    name: str = "DuckDuckGo Web Search"
    description: str = (
        "Search the live web for logistics news, freight rate data, maritime "
        "reports, port congestion updates, and supply chain intelligence. "
        "Input: a specific, targeted search query string."
    )

    def _run(self, query: str) -> str:
        runner = DuckDuckGoSearchRun()
        return runner.run(query)

    async def _arun(self, query: Optional[str] = None) -> str:
        return self._run(query)


def _build_search_tools() -> list:
    """
    Returns the best available search tool.
    Prefers Serper.dev (higher quality) when SERPER_API_KEY is present,
    otherwise falls back to DuckDuckGo (free, no key needed).

    FIX: moved from module-level execution into a callable function so it is
    only invoked when run_research() is actually called, not at import time.
    """
    if _SERPER_API_KEY:
        print("[logistics_crew] Using Serper.dev for web search.")
        return [SerperDevTool()]
    print("[logistics_crew] SERPER_API_KEY not found — falling back to DuckDuckGo.")
    return [DuckDuckGoTool()]


# ---------------------------------------------------------------------------
# 3. Agent factory  (built lazily inside run_research to avoid eager tool init)
# ---------------------------------------------------------------------------

def _build_agents():
    """
    Instantiate agents with freshly-built search tools.
    Called once per run_research() invocation so tool init errors surface at
    runtime with a clear traceback rather than silently at import time.
    """
    search_tools = _build_search_tools()

    analyst = Agent(
        role="Senior Logistics Analyst",
        goal=(
            "Autonomously search the web to find authoritative, current intelligence "
            "on logistics KPIs, freight rate indices, supply chain disruptions, port "
            "congestion, vessel traffic, and maritime/trade regulations. "
            "Always prioritise primary sources: BIMCO, Freightos Baltic Index, "
            "Lloyd's List, World Bank logistics data, and official port authority "
            "bulletins. Extract concrete, quantified data points wherever possible."
        ),
        backstory=(
            "You are a veteran supply chain intelligence professional with 15 years "
            "tracking global freight markets across Asia-Pacific, Trans-Atlantic, "
            "and Latin American corridors. You know exactly which sources to trust, "
            "how to identify stale or biased reporting, and how to extract granular "
            "metrics — TEU counts, voyage transit times, demurrage costs, load "
            "factors, and bunker fuel prices — from raw industry reports. "
            "When your first search returns insufficient data, you reformulate your "
            "query and try again rather than guessing."
        ),
        llm=llm,
        tools=search_tools,
        verbose=True,
        allow_delegation=False,
        max_iter=5,
        memory=False,
    )

    writer = Agent(
        role="Logistics Technical Writer",
        goal=(
            "Transform raw logistics research data into a polished, structured "
            "Markdown report that is immediately usable by supply chain planners "
            "and executives. Every claim must be source-attributed. Quantitative "
            "metrics must be presented in a scannable table or structured list. "
            "The output must follow the repository schema exactly so it is "
            "RAG-indexable downstream."
        ),
        backstory=(
            "You specialise in synthesising complex logistics intelligence into "
            "executive-ready briefs for freight forwarders, 3PLs, and shippers. "
            "Your reports follow a strict schema and are renowned for their clarity "
            "and accuracy. You never invent statistics, always flag unverified claims "
            "with [UNVERIFIED], and you proactively note data gaps so the reader "
            "knows exactly what is and is not confirmed."
        ),
        llm=llm,
        tools=[],
        verbose=True,
        allow_delegation=False,
        memory=False,
    )

    return analyst, writer


# ---------------------------------------------------------------------------
# 4. Task factory
# ---------------------------------------------------------------------------

def build_research_task(query: str, agent: Agent) -> Task:
    """
    Task 1 — Web research.
    The Logistics Analyst searches for data and returns a structured
    facts/sources/gaps payload for the writer to consume.
    """
    return Task(
        description=(
            f"Conduct deep-dive web research on the following logistics query:\n\n"
            f"QUERY: {query}\n\n"
            "Instructions:\n"
            "1. Run at least 3 targeted searches using specific, varied keywords.\n"
            "2. For each search, record: the source name, URL, publication date, "
            "   and the exact data points (numbers, dates, percentages, proper nouns).\n"
            "3. Cross-reference at least two sources for any statistic before "
            "   accepting it as verified.\n"
            "4. If initial results are thin or outdated (>6 months old), "
            "   refine your search terms and run additional queries.\n"
            "5. Return your findings in this exact format:\n\n"
            "   FACTS:\n"
            "   - [fact 1] (Source: [name], [URL], [date])\n"
            "   - [fact 2] ...\n\n"
            "   DATA_POINTS:\n"
            "   - Metric | Value | Unit | Source\n\n"
            "   SOURCES:\n"
            "   1. [name] — [URL]\n\n"
            "   GAPS:\n"
            "   - [anything you could not verify or find]\n"
        ),
        expected_output=(
            "A structured FACTS / DATA_POINTS / SOURCES / GAPS payload "
            "containing verified logistics intelligence with full source attribution."
        ),
        agent=agent,
    )


def build_writing_task(query: str, output_file: str, agent: Agent) -> Task:
    """
    Task 2 — Report synthesis.
    The Technical Writer turns the analyst's payload into a Markdown report
    and saves it to the knowledge_repo directory.
    """
    today = datetime.now().strftime("%Y-%m-%d")

    return Task(
        description=(
            "Using the research output from the Logistics Analyst, produce a "
            "professional Markdown intelligence report. Follow this schema exactly:\n\n"
            "---\n"
            f"# [Concise Descriptive Title]\n"
            f"**Date:** {today}  \n"
            f"**Query:** {query}  \n"
            "**Confidence:** [High / Medium / Low — based on source quality]\n"
            "---\n\n"
            "## Executive Summary\n"
            "3–5 sentences covering the most critical finding and its immediate "
            "implication for logistics operations.\n\n"
            "## Key Findings\n"
            "- Each finding on its own bullet, cited inline as (Source N).\n"
            "- Flag any unverified claims with [UNVERIFIED].\n\n"
            "## Data Points\n"
            "| Metric | Value | Unit | Date | Source |\n"
            "|--------|-------|------|------|--------|\n"
            "| ...    | ...   | ...  | ...  | ...    |\n\n"
            "## Implications for Logistics Planners\n"
            "Practical takeaways: routing adjustments, booking windows, "
            "cost forecasts, or contingency considerations.\n\n"
            "## Data Gaps & Caveats\n"
            "List anything that could not be confirmed, along with suggested "
            "follow-up research actions.\n\n"
            "## Sources\n"
            "Numbered list of all URLs cited in this report.\n\n"
            f"Save the completed report to: knowledge_repo/{output_file}"
        ),
        expected_output=(
            f"A complete, schema-compliant Markdown report saved to "
            f"knowledge_repo/{output_file}"
        ),
        agent=agent,
        output_file=f"knowledge_repo/{output_file}",
    )


# ---------------------------------------------------------------------------
# 5. Crew factory & main entry point
# ---------------------------------------------------------------------------

def run_research(query: str, output_file: str) -> str:
    """
    Assemble and run the Logistics Research Crew.

    Parameters
    ----------
    query : str
        The logistics research question or topic to investigate.
    output_file : str
        Filename (without directory prefix) for the Markdown report,
        e.g. "20240101_1200_panama-canal.md".

    Returns
    -------
    str
        The final synthesised report text as returned by CrewAI.
    """
    os.makedirs("knowledge_repo", exist_ok=True)

    # FIX: agents (and therefore tools) are built lazily here, not at import time
    logistics_analyst, technical_writer = _build_agents()

    tasks = [
        build_research_task(query, logistics_analyst),
        build_writing_task(query, output_file, technical_writer),
    ]

    crew = Crew(
        agents=[logistics_analyst, technical_writer],
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
        memory=False,
    )

    print(f"\n[logistics_crew] Kicking off crew for query: '{query}'")
    result = crew.kickoff()

    print(f"\n[logistics_crew] Research complete. Report: knowledge_repo/{output_file}")
    return str(result)


# ---------------------------------------------------------------------------
# 6. Quick standalone test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_query = (
        "Analyze the impact of current drought conditions "
        "on Panama Canal transit times and container shipping rates"
    )
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"{timestamp}_panama-canal-drought.md"

    output = run_research(query=test_query, output_file=filename)
    print("\n--- Preview (first 600 chars) ---")
    print(output[:600])
