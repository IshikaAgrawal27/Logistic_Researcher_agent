import os
from typing import Optional

from langchain_community.tools import DuckDuckGoSearchRun
from crewai.tools import BaseTool

# FIX: SerperDevTool was instantiated at module level unconditionally.
# This caused an immediate crash on import whenever SERPER_API_KEY was not set.
# It is now instantiated lazily inside the function, only when the key exists.

def _get_serper_tool():
    """Lazily import and instantiate SerperDevTool only when API key is present."""
    from crewai_tools import SerperDevTool  # noqa: PLC0415
    return SerperDevTool()


# DuckDuckGo wrapper — always available, no API key required
class DuckDuckGoTool(BaseTool):
    name: str = "DuckDuckGo Web Search"
    description: str = (
        "Search the web for current logistics news, freight rate data, "
        "maritime reports, and supply chain intelligence. Input a specific query."
    )

    def _run(self, query: str) -> str:
        return DuckDuckGoSearchRun().run(query)

    async def _arun(self, query: str) -> Optional[str]:
        return self._run(query)


duck_tool = DuckDuckGoTool()

# Export whichever tool is available based on environment
if os.getenv("SERPER_API_KEY"):
    serper_tool = _get_serper_tool()
    SEARCH_TOOLS = [serper_tool]
else:
    SEARCH_TOOLS = [duck_tool]   # free fallback
