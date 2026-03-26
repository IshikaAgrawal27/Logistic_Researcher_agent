"""
retriever.py
============
Query the local ChromaDB vector store before hitting the live web.
Uses modern LangChain v0.2+ imports (no deprecated langchain.chains).
"""

import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

CHROMA_DIR = "./chroma_db"


def get_db() -> Chroma:
    # FIX: was "models/gemini-2.5-flash" — that is a generation model, NOT an embedding
    # model.  The correct embedding model identifier is "models/gemini-embedding-001".
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
    )


LOGISTICS_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a senior logistics intelligence analyst.
Use ONLY the context below (sourced from verified research reports) to answer
the question. If the context does not contain enough information, say:
"Insufficient data in knowledge base — recommend running a live agent query."

Context:
{context}

Question: {question}

Answer (include source report names where relevant):
""",
)


def format_docs(docs) -> str:
    return "\n\n---\n\n".join([doc.page_content for doc in docs])


def query_local(question: str, k: int = 4) -> str:
    """
    Query the local ChromaDB knowledge base using modern LCEL chain syntax.

    Parameters
    ----------
    question : str   The logistics question to answer.
    k        : int   Number of nearest chunks to retrieve (default 4).

    Returns
    -------
    str   Answer synthesised from local reports.
    """
    db = get_db()

    retriever = db.as_retriever(search_kwargs={"k": k})

    # FIX: was "gemini-2.5-flash" — corrected to "gemini-2.5-flash" to match
    # the model used throughout the rest of the project (logistics_crew.py).
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.2,
        convert_system_message_to_human=True,
    )

    # Modern LCEL chain — replaces deprecated RetrievalQA
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | LOGISTICS_PROMPT
        | llm
        | StrOutputParser()
    )

    # Fetch source doc names separately for display
    source_docs = retriever.invoke(question)
    sources = list({doc.metadata.get("source", "unknown") for doc in source_docs})

    answer = rag_chain.invoke(question)

    print("\n[retriever] Sources used:")
    for s in sources:
        print(f"  - {s}")

    return answer


if __name__ == "__main__":
    q = "What are the latest freight rate impacts on Asia-Europe routes?"
    print(query_local(q))
