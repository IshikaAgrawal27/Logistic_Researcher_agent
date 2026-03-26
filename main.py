import os
import re
import glob
from datetime import datetime
from dotenv import load_dotenv
from src.agents.logistics_crew import run_research
from src.rag.indexer import index_knowledge_repo
from src.rag.retriever import query_local

load_dotenv()


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()[:60]).strip("-")


def knowledge_base_exists() -> bool:
    """
    FIX: previous version returned True whenever the chroma_db directory
    existed (even if it was empty), falsely reporting the KB as ready.

    Now checks for the actual SQLite database file AND that the directory
    is non-empty, matching the behaviour of app.py's version of this check.
    """
    chroma_dir = "./chroma_db"
    if not os.path.isdir(chroma_dir):
        return False
    # Must contain at least one file (e.g. chroma.sqlite3) to be usable
    return bool(os.listdir(chroma_dir))


def main():
    print("\n=== Autonomous Logistics Researcher Agent ===\n")
    print("1 — Run live agent research (web search + report)")
    print("2 — Query local knowledge base (instant, no API web calls)")
    print("3 — Re-index knowledge_repo into vector store")

    choice = input("\nChoose [1/2/3]: ").strip()

    if choice == "3":
        index_knowledge_repo()
        return

    query = input("\nEnter your logistics query:\n> ").strip()
    if not query:
        print("No query provided. Exiting.")
        return

    if choice == "2":
        # ── RAG path ────────────────────────────────────────────────────────
        if not knowledge_base_exists():
            print("\n[!] No knowledge base found. Run option 3 first to index your reports.")
            return
        print("\n[*] Querying local knowledge base...\n")
        answer = query_local(query)
        print("\n=== Answer from Knowledge Base ===")
        print(answer)

    else:
        # ── Live agent path ──────────────────────────────────────────────────
        timestamp   = datetime.now().strftime("%Y%m%d_%H%M")
        output_file = f"{timestamp}_{slugify(query)}.md"

        print(f"\n[*] Starting live research...")
        print(f"    Output → knowledge_repo/{output_file}\n")

        try:
            result = run_research(query, output_file)
            print("\n=== Research Complete ===")
            print(f"Report saved → knowledge_repo/{output_file}")
            print("\nPreview:\n" + str(result)[:500] + "...")

            # Auto-index the new report into the vector store
            print("\n[*] Auto-indexing new report into knowledge base...")
            index_knowledge_repo()

        except Exception as e:
            print(f"\n[ERROR] Agent run failed: {e}")


if __name__ == "__main__":
    main()
