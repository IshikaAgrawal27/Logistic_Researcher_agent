# Autonomous Logistics Researcher Agent

An AI agent that researches logistics topics (freight rates, port congestion, supply-chain disruptions) using live web search, then stores reports in a local RAG knowledge base for instant offline querying.

---

## Quick Start

### 1. Prerequisites
- Python 3.10 or 3.11 (Python 3.12 works too)
- A **Google Gemini API key** → https://aistudio.google.com/apikey (free tier available)

### 2. Clone / unzip the project
```bash
unzip Logistic_Researcher_agent-fixed.zip
cd Logistic_Researcher_agent-fixed
```

### 3. Create & activate a virtual environment
```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Set up your API key
Copy `.env.example` to `.env` and fill in your key:
```bash
cp .env.example .env
# then edit .env and replace "your_google_api_key_here" with your real key
```

Your `.env` should look like:
```
GOOGLE_API_KEY=AIzaSy...your_actual_key...
```

### 6. Run the app

**Option A — Streamlit UI (recommended)**
```bash
streamlit run app.py
```
Then open http://localhost:8501 in your browser.

**Option B — Command-line interface**
```bash
python main.py
```

---

## How It Works

| Mode | What it does |
|------|-------------|
| **Live Research** | Sends your query to two AI agents (Analyst + Writer) who search the web and produce a Markdown report saved in `knowledge_repo/` |
| **Query Knowledge Base** | Answers your question instantly from previously saved reports using RAG (no web call, no API cost) |
| **Re-index** | Scans `knowledge_repo/` and re-embeds all `.md` files into ChromaDB |

---

## Bugs Fixed (from original)

| File | Bug | Fix |
|------|-----|-----|
| `src/rag/retriever.py` | Used `models/gemini-2.5-flash` as the **embedding** model — wrong, that is a generation model and causes an API error | Changed to `models/gemini-embedding-001` (the correct embedding model) |
| `src/rag/retriever.py` | LLM was `gemini-2.5-flash`; inconsistent with the rest of the project | Changed to `gemini-2.5-flash` to match `logistics_crew.py` |
| `src/tools/search_tools.py` | `SerperDevTool()` instantiated at **module level** without checking for `SERPER_API_KEY` — crashed on import if key was absent | Now instantiated lazily, only when key is present; falls back to DuckDuckGo automatically |
| Project root | No `.env` file or example — users had no guidance on required keys | Added `.env.example` |

---

## Optional: Serper.dev (Better Search)

The agent defaults to free DuckDuckGo search. For higher-quality results, get a free API key at https://serper.dev and add it to your `.env`:
```
SERPER_API_KEY=your_serper_api_key_here
```

---

## Project Structure

```
├── app.py                  # Streamlit UI
├── main.py                 # CLI entry point
├── requirements.txt
├── .env.example            # Copy to .env and fill in keys
├── knowledge_repo/         # Saved research reports (.md files)
├── chroma_db/              # Local vector store (auto-created)
└── src/
    ├── agents/
    │   └── logistics_crew.py   # CrewAI agents & crew setup
    ├── rag/
    │   ├── indexer.py          # Embeds reports into ChromaDB
    │   └── retriever.py        # RAG query chain
    ├── tasks/
    │   └── research_tasks.py   # Task definitions
    └── tools/
        └── search_tools.py     # Web search tool wrappers
```
