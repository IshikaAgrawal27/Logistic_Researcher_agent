"""
app.py  —  Streamlit UI for the Autonomous Logistics Researcher Agent
Run with:  streamlit run app.py
"""

import os
import re
import glob
import time
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Logistics Intelligence Agent",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Root & body ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #1f2937;
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 2rem 2.5rem; max-width: 1200px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #f8fafc;
    border-right: 1px solid #e2e8f0;
}
[data-testid="stSidebar"] * { color: #334155 !important; }
[data-testid="stSidebar"] .stRadio label {
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    font-weight: 500;
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    transition: all 0.2s ease;
    cursor: pointer;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background-color: #e2e8f0;
    color: #0f172a !important;
}

/* ── Hero header ── */
.hero-title {
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    font-size: 2.25rem;
    color: #0f172a;
    letter-spacing: -0.025em;
    line-height: 1.2;
    margin-bottom: 0.25rem;
}
.hero-sub {
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    font-weight: 500;
    color: #64748b;
    margin-bottom: 2rem;
}

/* ── Stat cards ── */
.stat-row { display: flex; gap: 1rem; margin-bottom: 2rem; }
.stat-card {
    flex: 1;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    transition: transform 0.2s, box-shadow 0.2s;
}
.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}
.stat-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 0.5rem;
    letter-spacing: 0.05em;
}
.stat-value {
    font-family: 'Inter', sans-serif;
    font-size: 1.75rem;
    font-weight: 700;
    color: #0f172a;
}

/* ── Section headers ── */
.section-header {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 1.25rem;
    color: #0f172a;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 0.5rem;
    margin-bottom: 1.5rem;
    width: 100%;
}

/* ── Query input override ── */
.stTextArea textarea {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    background: #ffffff !important;
    color: #1e293b !important;
    padding: 1rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
}
.stTextArea textarea:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
}

/* ── Buttons ── */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    background: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
}
.stButton > button:hover {
    background: #f8fafc !important;
    border-color: #94a3b8 !important;
    color: #0f172a !important;
}
.stButton > button:active {
    background: #f1f5f9 !important;
}

/* ── Report card ── */
.report-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #3b82f6;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    transition: all 0.2s ease;
}
.report-card:hover { 
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); 
    border-left-color: #2563eb;
}
.report-title {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
    color: #0f172a;
    margin-bottom: 0.25rem;
}
.report-meta {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    color: #64748b;
}

/* ── Output box ── */
.output-box {
    background: #f8fafc;
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    font-family: 'Courier New', Courier, monospace;
    font-size: 0.875rem;
    color: #334155;
    line-height: 1.6;
    white-space: pre-wrap;
    max-height: 400px;
    overflow-y: auto;
    border: 1px solid #e2e8f0;
    box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.02);
}

/* ── Status badges ── */
.badge {
    display: inline-block;
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    padding: 0.2rem 0.6rem;
    border-radius: 9999px;
}
.badge-blue  { background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; }
.badge-green { background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }
.badge-amber { background: #fffbeb; color: #d97706; border: 1px solid #fde68a; }

/* ── Divider ── */
.thin-line {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 1.5rem 0;
}

/* ── Answer box ── */
.answer-box {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    font-size: 0.95rem;
    color: #1e293b;
    line-height: 1.6;
    box-shadow: 0 1px 3px 0 rgba(0,0,0,0.05);
}

/* ── Log line ── */
.log-line { color: #3b82f6; }
.log-done { color: #16a34a; }
.log-err  { color: #dc2626; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ─────────────────────────────────────────────────────────────────

def clean_markdown(text: str) -> str:
    text = text.strip()
    if text.startswith("```markdown"):
        text = text[11:]
    elif text.startswith("```md"):
        text = text[5:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()[:60]).strip("-")

def get_reports() -> list[dict]:
    files = sorted(glob.glob("knowledge_repo/*.md"), reverse=True)
    reports = []
    for f in files:
        name = os.path.basename(f)
        size = os.path.getsize(f)
        mtime = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M")
        reports.append({"name": name, "path": f, "size": size, "modified": mtime})
    return reports

def knowledge_base_exists() -> bool:
    chroma_dir = "./chroma_db"
    return os.path.isdir(chroma_dir) and bool(os.listdir(chroma_dir))

# FIX: decorated with @st.cache_data so the ChromaDB connection + embedding
# model init only runs once per 60-second window, not on every Streamlit
# rerun/interaction.
@st.cache_data(ttl=60)
def count_chunks() -> int:
    try:
        from langchain_chroma import Chroma
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        emb = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
        db = Chroma(persist_directory="./chroma_db", embedding_function=emb)
        return db._collection.count()
    except Exception:
        return 0

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0 0.5rem;'>
        <div style='font-family:Inter,sans-serif;font-size:1.25rem;
                    font-weight:700;color:#0f172a;letter-spacing:-0.02em;'>
            LogisticsAI
        </div>
        <div style='font-family:Inter,sans-serif;font-size:0.75rem;
                    font-weight:500;color:#64748b;letter-spacing:0.05em;
                    text-transform:uppercase;margin-top:4px;'>
            Intelligence Agent
        </div>
    </div>
    <hr style='border:none;border-top:1px solid #e2e8f0;margin:0.8rem 0 1.2rem;'/>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["Live Research", "Query Knowledge Base", "Report Library", "Settings"],
        label_visibility="collapsed",
    )

    st.markdown("<hr style='border:none;border-top:1px solid #e2e8f0;margin:1.2rem 0;'/>",
                unsafe_allow_html=True)

    reports = get_reports()
    kb_ok   = knowledge_base_exists()

    st.markdown(f"""
    <div style='font-family:Inter,sans-serif;font-size:0.75rem;
                font-weight:500;color:#64748b;line-height:2;letter-spacing:0.02em;'>
        <div style='display:flex;justify-content:space-between;'><span>REPORTS</span><span style='color:#0f172a;font-weight:600;'>{len(reports)}</span></div>
        <div style='display:flex;justify-content:space-between;'><span>KB STATUS</span><span style='color:{"#16a34a" if kb_ok else "#dc2626"};font-weight:600;'>
            {"READY" if kb_ok else "EMPTY"}</span></div>
        <div style='display:flex;justify-content:space-between;'><span>SERPER</span><span style='color:{"#16a34a" if os.getenv("SERPER_API_KEY") else "#d97706"};font-weight:600;'>
            {"ACTIVE" if os.getenv("SERPER_API_KEY") else "DDG FALLBACK"}</span></div>
    </div>
    """, unsafe_allow_html=True)

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='hero-title'>Logistics Intelligence</div>
<div class='hero-sub'>Autonomous Research Agent · Powered by Gemini + CrewAI</div>
""", unsafe_allow_html=True)

# ── Stat bar ─────────────────────────────────────────────────────────────────
chunks = count_chunks() if kb_ok else 0
total_size = sum(r["size"] for r in reports) // 1024

st.markdown(f"""
<div class='stat-row'>
    <div class='stat-card'>
        <div class='stat-label'>Reports Generated</div>
        <div class='stat-value'>{len(reports)}</div>
    </div>
    <div class='stat-card'>
        <div class='stat-label'>KB Chunks Indexed</div>
        <div class='stat-value'>{chunks}</div>
    </div>
    <div class='stat-card'>
        <div class='stat-label'>Repo Size</div>
        <div class='stat-value'>{total_size}<span style='font-size:1rem;color:#64748b;'> KB</span></div>
    </div>
    <div class='stat-card'>
        <div class='stat-label'>Search Engine</div>
        <div class='stat-value' style='font-size:1rem;margin-top:4px;'>
            {"Serper.dev" if os.getenv("SERPER_API_KEY") else "DuckDuckGo"}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='thin-line'/>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Live Research
# ════════════════════════════════════════════════════════════════════════════
if "Live Research" in page:
    st.markdown("<div class='section-header'>Run Live Agent Research</div>",
                unsafe_allow_html=True)

    # Example queries
    st.markdown("**Quick-load an example query:**")
    examples = [
        "Analyze Red Sea shipping disruptions and impact on Europe-Asia freight rates",
        "What is the current Panama Canal drought impact on transit times?",
        "Report on global container port congestion levels in 2025",
        "Compare air freight vs ocean freight rate trends for Asia-US routes",
    ]
    cols = st.columns(2)
    for i, ex in enumerate(examples):
        with cols[i % 2]:
            # FIX: only append ellipsis when the label is actually truncated
            label = ex[:55] + ("..." if len(ex) > 55 else "")
            if st.button(label, key=f"ex_{i}"):
                st.session_state["query_input"] = ex

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    query = st.text_area(
        "Research Query",
        value=st.session_state.get("query_input", ""),
        height=100,
        placeholder="e.g. Analyze the impact of current Red Sea disruptions on European container shipping rates...",
        label_visibility="collapsed",
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        run_btn = st.button("Run Agent")

    if run_btn:
        if not query.strip():
            st.warning("Please enter a research query.")
        else:
            timestamp   = datetime.now().strftime("%Y%m%d_%H%M")
            output_file = f"{timestamp}_{slugify(query)}.md"

            st.markdown(f"""
            <div style='margin:1rem 0 0.5rem;display:flex;align-items:center;'>
                <span class='badge badge-amber'>RUNNING</span>
                <span style='font-family:Inter,sans-serif;font-size:0.8rem;
                             color:#d97706;font-weight:500;margin-left:8px;'>
                    → knowledge_repo/{output_file}
                </span>
            </div>
            """, unsafe_allow_html=True)

            log_placeholder = st.empty()
            result_placeholder = st.empty()

            log_lines = [
                "[ ANALYST ] Initialising Logistics Analyst agent...",
                "[ ANALYST ] Connecting to search tools...",
                "[ ANALYST ] Running web search pass 1...",
                "[ ANALYST ] Extracting data points and sources...",
                "[ ANALYST ] Running web search pass 2 (refinement)...",
                "[ ANALYST ] Verifying cross-references...",
                "[ WRITER  ] Technical Writer receiving research payload...",
                "[ WRITER  ] Synthesising into structured Markdown report...",
                "[ WRITER  ] Applying schema: Summary → Findings → Data → Sources...",
                f"[ SYSTEM  ] Saving report → knowledge_repo/{output_file}",
            ]

            # Animate log lines
            shown = []
            for line in log_lines:
                shown.append(line)
                log_placeholder.markdown(
                    "<div class='output-box'>" +
                    "\n".join(f"<span class='log-line'>{l}</span>" for l in shown) +
                    "</div>",
                    unsafe_allow_html=True,
                )
                time.sleep(0.4)

            # Actually run the agent
            try:
                from src.agents.logistics_crew import run_research
                result = run_research(query, output_file)

                # Auto-index
                try:
                    from src.rag.indexer import index_knowledge_repo
                    index_knowledge_repo()
                    shown.append("[ INDEXER ] New report indexed into ChromaDB ✓")
                    # Bust the chunk count cache so the stat bar updates
                    count_chunks.clear()
                except Exception:
                    pass

                shown.append("[ DONE    ] Research complete ✓")
                log_placeholder.markdown(
                    "<div class='output-box'>" +
                    "\n".join(
                        f"<span class='{'log-done' if '✓' in l else 'log-line'}'>{l}</span>"
                        for l in shown
                    ) + "</div>",
                    unsafe_allow_html=True,
                )

                st.markdown(f"""
                <div style='margin-top:1rem;display:flex;align-items:center;'>
                    <span class='badge badge-green'>COMPLETE</span>
                    <span style='font-family:Inter,sans-serif;font-size:0.8rem;
                                 color:#16a34a;font-weight:500;margin-left:8px;'>
                        Report saved successfully
                    </span>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<div class='section-header' style='margin-top:1.5rem;'>Report Output</div>",
                            unsafe_allow_html=True)
                st.markdown(clean_markdown(result))

                st.download_button(
                    label="Download Report",
                    data=result,
                    file_name=output_file,
                    mime="text/markdown",
                )

            except Exception as e:
                shown.append(f"[ ERROR ] {e}")
                log_placeholder.markdown(
                    "<div class='output-box'>" +
                    "\n".join(
                        f"<span class='{'log-err' if 'ERROR' in l else 'log-line'}'>{l}</span>"
                        for l in shown
                    ) + "</div>",
                    unsafe_allow_html=True,
                )
                st.error(f"Agent run failed: {e}")

# ════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Query Knowledge Base
# ════════════════════════════════════════════════════════════════════════════
elif "Query Knowledge Base" in page:
    st.markdown("<div class='section-header'>Query Local Knowledge Base</div>",
                unsafe_allow_html=True)

    if not kb_ok:
        st.markdown("""
        <div style='background:#fff7ed;border:1px solid #fdba74;border-radius:8px;
                    padding:1rem 1.25rem;font-size:0.95rem;color:#9a3412;'>
            <strong>Knowledge base is empty.</strong><br>
            Run at least one Live Research session first, then come back here
            to query across all your saved reports instantly — no web calls needed.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;
                    padding:1rem 1.25rem;font-size:0.95rem;color:#166534;
                    margin-bottom:1.5rem;'>
            <strong>{chunks} chunks</strong> indexed from <strong>{len(reports)} reports</strong>
            — ready for instant retrieval.
        </div>
        """, unsafe_allow_html=True)

        k = st.slider("Chunks to retrieve (k)", min_value=2, max_value=10, value=4,
                      help="More chunks = broader context but slower synthesis.")

        question = st.text_area(
            "Question",
            height=90,
            placeholder="e.g. What were the main freight rate findings across all my reports?",
            label_visibility="collapsed",
        )

        if st.button("Query Knowledge Base"):
            if not question.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Retrieving from local knowledge base..."):
                    try:
                        from src.rag.retriever import query_local
                        answer = query_local(question, k=k)

                        st.markdown("<div class='section-header' style='margin-top:1.2rem;'>Answer</div>",
                                    unsafe_allow_html=True)
                        st.markdown(clean_markdown(answer))
                    except Exception as e:
                        st.error(f"Query failed: {e}")

# ════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Report Library
# ════════════════════════════════════════════════════════════════════════════
elif "Report Library" in page:
    st.markdown("<div class='section-header'>Report Library</div>",
                unsafe_allow_html=True)

    if not reports:
        st.info("No reports yet. Run a Live Research session to generate your first report.")
    else:
        search = st.text_input("Filter reports", placeholder="Search by filename...",
                               label_visibility="collapsed")
        filtered = [r for r in reports if search.lower() in r["name"].lower()] \
                   if search else reports

        st.markdown(f"<div style='font-family:Inter,sans-serif;font-size:0.85rem;font-weight:500;"
                    f"color:#64748b;margin-bottom:1.25rem;'>"
                    f"Showing {len(filtered)} of {len(reports)} reports</div>",
                    unsafe_allow_html=True)

        for r in filtered:
            size_kb = r["size"] // 1024 or 1
            slug    = r["name"].replace(".md", "").replace("_", " ")

            st.markdown(f"""
            <div class='report-card'>
                <div class='report-title'>{slug}</div>
                <div class='report-meta'>
                    {r['modified']} &nbsp;·&nbsp; {size_kb} KB
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander(f"View — {r['name']}"):
                try:
                    with open(r["path"], "r", encoding="utf-8") as f:
                        content = f.read()
                    st.markdown(clean_markdown(content))
                    st.download_button(
                        label="Download",
                        data=content,
                        file_name=r["name"],
                        mime="text/markdown",
                        key=f"dl_{r['name']}",
                    )
                except Exception as e:
                    st.error(f"Could not read file: {e}")

# ════════════════════════════════════════════════════════════════════════════
# PAGE 4 — Settings
# ════════════════════════════════════════════════════════════════════════════
elif "Settings" in page:
    st.markdown("<div class='section-header'>Settings & Tools</div>",
                unsafe_allow_html=True)

    # API status
    st.markdown("**API Key Status**")
    gemini_ok = bool(os.getenv("GOOGLE_API_KEY"))
    serper_ok = bool(os.getenv("SERPER_API_KEY"))

    st.markdown(f"""
    <div style='display:flex;gap:1rem;margin-bottom:1.5rem;'>
        <div class='stat-card' style='flex:1;'>
            <div class='stat-label'>Gemini API Key</div>
            <div style='font-family:Inter,sans-serif;font-size:0.9rem;font-weight:600;
                        color:{"#16a34a" if gemini_ok else "#dc2626"};margin-top:4px;'>
                {"● SET" if gemini_ok else "● NOT SET"}
            </div>
        </div>
        <div class='stat-card' style='flex:1;'>
            <div class='stat-label'>Serper API Key</div>
            <div style='font-family:Inter,sans-serif;font-size:0.9rem;font-weight:600;
                        color:{"#16a34a" if serper_ok else "#d97706"};margin-top:4px;'>
                {"● SET" if serper_ok else "● USING DUCKDUCKGO"}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='thin-line'/>", unsafe_allow_html=True)

    # Re-index
    st.markdown("**Knowledge Base Management**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Re-index Knowledge Repo"):
            with st.spinner("Indexing all reports..."):
                try:
                    from src.rag.indexer import index_knowledge_repo
                    n = index_knowledge_repo()
                    count_chunks.clear()  # bust the cache after re-index
                    st.success(f"Indexed {n} chunks from {len(reports)} reports.")
                except Exception as e:
                    st.error(f"Indexing failed: {e}")

    with col2:
        if st.button("Clear Knowledge Base"):
            import shutil
            if os.path.isdir("./chroma_db"):
                shutil.rmtree("./chroma_db")
                count_chunks.clear()  # bust the cache after clearing
                st.success("ChromaDB cleared. Re-index to rebuild.")
            else:
                st.info("No knowledge base found.")

    st.markdown("<hr class='thin-line'/>", unsafe_allow_html=True)

    # Project info
    st.markdown("**Project Info**")
    st.markdown(f"""
    <div style='font-family:Inter,sans-serif;font-size:0.85rem;font-weight:500;
                color:#475569;line-height:2;display:grid;grid-template-columns:120px 1fr;gap:0.5rem;'>
        <div style='color:#94a3b8;font-weight:600;'>FRAMEWORK</div><div>CrewAI + LangChain</div>
        <div style='color:#94a3b8;font-weight:600;'>LLM</div><div>Gemini 1.5 Flash</div>
        <div style='color:#94a3b8;font-weight:600;'>VECTOR DB</div><div>ChromaDB (local)</div>
        <div style='color:#94a3b8;font-weight:600;'>EMBEDDINGS</div><div>Google embedding-001</div>
        <div style='color:#94a3b8;font-weight:600;'>REPORTS DIR</div><div>./knowledge_repo/</div>
        <div style='color:#94a3b8;font-weight:600;'>CHROMA DIR</div><div>./chroma_db/</div>
    </div>
    """, unsafe_allow_html=True)
