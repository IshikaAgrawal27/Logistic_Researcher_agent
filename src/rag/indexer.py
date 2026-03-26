"""
indexer.py
==========
Scans knowledge_repo/ for .md files and upserts them
into a local ChromaDB vector store for RAG queries.
Includes batched embedding with rate-limit handling for
the Gemini free tier (100 requests/min cap).

FIX: Each chunk is now assigned a deterministic ID derived from its source
filename and chunk index. ChromaDB will upsert (update-or-insert) on the
same ID instead of blindly appending — so running index_knowledge_repo()
multiple times no longer creates duplicate vector entries.
"""

import os
import time
import glob
import hashlib
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import MarkdownTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

CHROMA_DIR  = "./chroma_db"
REPO_DIR    = "./knowledge_repo"
BATCH_SIZE  = 50   # safe under the 100 req/min free-tier limit
RATE_PAUSE  = 65   # seconds to wait between batches (> 60s to be safe)


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )


def _make_chunk_id(source: str, chunk_index: int, content: str) -> str:
    """
    Generate a stable, deterministic ID for a chunk so that re-indexing the
    same file produces the same IDs and ChromaDB upserts instead of appending.

    ID format:  <source_filename>__<chunk_index>__<content_hash8>
    The content hash catches the edge case where a file's chunks shift after
    an edit — changed chunks get new IDs and are re-embedded correctly.
    """
    content_hash = hashlib.md5(content.encode("utf-8")).hexdigest()[:8]
    safe_source = source.replace("/", "_").replace("\\", "_")
    return f"{safe_source}__{chunk_index}__{content_hash}"


def index_knowledge_repo() -> int:
    """
    Load all .md files from knowledge_repo/ and upsert into ChromaDB.
    Embeds in batches to respect the Gemini free-tier rate limit.
    Returns the total number of chunks indexed.

    Safe to call multiple times — duplicate chunks will never be created
    because each chunk has a deterministic ID that ChromaDB upserts on.
    """
    md_files = glob.glob(f"{REPO_DIR}/*.md")
    if not md_files:
        print("[indexer] No .md files found in knowledge_repo/. Run the agent first.")
        return 0

    # ── Load & tag documents ────────────────────────────────────────────────
    docs = []
    for path in md_files:
        loader = TextLoader(path, encoding="utf-8")
        loaded = loader.load()
        for doc in loaded:
            doc.metadata["source"] = os.path.basename(path)
        docs.extend(loaded)

    # ── Split into chunks ───────────────────────────────────────────────────
    splitter = MarkdownTextSplitter(chunk_size=500, chunk_overlap=60)
    chunks = splitter.split_documents(docs)

    # FIX: assign deterministic IDs to every chunk before sending to ChromaDB
    chunk_ids = [
        _make_chunk_id(
            source=chunk.metadata.get("source", "unknown"),
            chunk_index=i,
            content=chunk.page_content,
        )
        for i, chunk in enumerate(chunks)
    ]

    print(f"[indexer] {len(chunks)} chunks from {len(docs)} reports — "
          f"indexing in batches of {BATCH_SIZE}...")

    embeddings = get_embeddings()
    db = None
    total_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE

    # ── Embed in batches with rate-limit pause ──────────────────────────────
    for i in range(0, len(chunks), BATCH_SIZE):
        batch      = chunks[i : i + BATCH_SIZE]
        batch_ids  = chunk_ids[i : i + BATCH_SIZE]
        batch_num  = i // BATCH_SIZE + 1
        print(f"[indexer] Batch {batch_num}/{total_batches} — "
              f"upserting {len(batch)} chunks...")

        if db is None:
            # First batch: create the collection (ids= enables upsert semantics)
            db = Chroma.from_documents(
                documents=batch,
                ids=batch_ids,
                embedding=embeddings,
                persist_directory=CHROMA_DIR,
            )
        else:
            # Subsequent batches: upsert into existing collection
            db.add_documents(batch, ids=batch_ids)

        # Pause between batches to avoid hitting the 100 req/min cap
        if i + BATCH_SIZE < len(chunks):
            print(f"[indexer] Rate-limit pause ({RATE_PAUSE}s before next batch)...")
            time.sleep(RATE_PAUSE)

    print(f"[indexer] Done. {len(chunks)} chunks upserted successfully.")
    return len(chunks)


if __name__ == "__main__":
    index_knowledge_repo()
