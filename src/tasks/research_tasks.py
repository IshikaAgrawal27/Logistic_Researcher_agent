"""
research_tasks.py
=================
Thin re-export shim — delegates to the canonical task builders in
logistics_crew.py to eliminate the previous code duplication.

Previously this file defined its own build_tasks() with a different,
less-complete schema (missing Confidence field, Data Points table, etc.)
that was never actually imported anywhere.  All task logic now lives in
one place: src/agents/logistics_crew.py.
"""

from src.agents.logistics_crew import build_research_task, build_writing_task


def build_tasks(analyst, writer, query: str, output_file: str) -> list:
    """
    Convenience wrapper kept for backwards compatibility.
    Delegates to the canonical builders in logistics_crew.py.
    """
    return [
        build_research_task(query, analyst),
        build_writing_task(query, output_file, writer),
    ]
