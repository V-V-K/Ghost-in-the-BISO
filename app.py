import json
from datetime import date
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

APP_DIR = Path(__file__).parent
DEFAULT_DATA = APP_DIR / "sample_data.csv"
OLLAMA_URL = "http://localhost:11434/api/chat"

def call_ollama(model_name, messages):
    """Call Ollama's local API."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": model_name, "messages": messages, "stream": False},
            timeout=180,
        )
        response.raise_for_status()
        payload = response.json()
        return payload.get("message", {}).get("content", "The ghost returned no message.")
    except requests.exceptions.ConnectionError:
        return (
            "**The séance could not connect.** Ollama is not reachable at `http://localhost:11434`. "
            "Install and start Ollama, then run `ollama pull qwen3:4b` and try again."
        )
    except requests.exceptions.Timeout:
        return "The local model took too long to respond. Try a smaller model such as `qwen3:1.7b`."
    except Exception as exc:
        return f"**Local model error:** `{exc}`. Check that the model name exists with `ollama list`."


st.set_page_config(
    page_title="The Ghost in the BISO",
    page_icon="👻",
    layout="wide",
)

st.markdown("""
<style>
.stApp { background: radial-gradient(circle at top right, #222016 0, #101114 42%, #08090c 100%); }
h1, h2, h3 { color: #f6bd60 !important; }
div[data-testid="stMetric"] { background: #17191f; border: 1px solid #37302a; padding: 14px; border-radius: 12px; }
div[data-testid="stDataFrame"] { border: 1px solid #34343a; border-radius: 10px; }
.ghost-note { padding: 14px 16px; border-left: 3px solid #f6bd60; background: #191a1e; border-radius: 8px; }
.small-muted { color: #a6a6ad; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

st.title("👻 THE GHOST IN THE BISO")
st.caption("A local-first AI companion for security risk, audit readiness, and remediation.")
st.markdown(
    '<div class="ghost-note">“The past leaves evidence. The future inherits risk.” '
    '<br><span class="small-muted">Demo mode uses fictional data. Never upload employer-confidential data to this prototype.</span></div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("🔦 Investigation settings")
    model = st.text_input("Local Ollama model", value="qwen3:4b")
    st.caption("Runs locally through Ollama. Download the model once; afterwards inference can run offline.")
    uploaded = st.file_uploader("Optional: upload a fictional CSV risk register", type=["csv"])
    st.divider()
    st.markdown("**Local-first by design**")
    st.write("• Findings stay on this computer")
    st.write("• Python calculates metrics")
    st.write("• The local model explains the evidence")
    st.write("• No cloud AI API key is used")

@st.cache_data
def load_default():
    return pd.read_csv(DEFAULT_DATA)

try:
    if uploaded is not None:
        df = pd.read_csv(uploaded)
        data_source = "uploaded CSV"
    else:
        df = load_default()
        data_source = "built-in fictional sample"
except Exception as exc:
    st.error(f"Could not read the CSV: {exc}")
    st.stop()

required = {"finding_id", "title", "domain", "severity", "status", "owner", "days_open", "evidence_status", "business_impact"}
missing = required - set(df.columns)
if missing:
    st.error("CSV is missing required columns: " + ", ".join(sorted(missing)))
    st.stop()

df["days_open"] = pd.to_numeric(df["days_open"], errors="coerce").fillna(0).astype(int)
df["severity"] = df["severity"].astype(str).str.strip().str.title()
df["status"] = df["status"].astype(str).str.strip().str.title()
df["evidence_status"] = df["evidence_status"].astype(str).str.strip().str.title()

# Deterministic rules keep the numbers explainable and reproducible.
open_df = df[~df["status"].str.lower().isin(["closed", "resolved", "complete", "completed"])]
critical_open = open_df[open_df["severity"].str.lower().isin(["critical", "high"])]
stale_open = open_df[open_df["days_open"] >= 30]
missing_owner = open_df[open_df["owner"].fillna("").astype(str).str.strip().str.lower().isin(["", "none", "nan", "unassigned"])]
missing_evidence = open_df[~open_df["evidence_status"].str.lower().isin(["complete", "verified", "attached"])]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Open findings", len(open_df))
c2.metric("Critical / high open", len(critical_open))
c3.metric("Open ≥ 30 days", len(stale_open))
c4.metric("Evidence gaps", len(missing_evidence))

tab1, tab2, tab3, tab4 = st.tabs(["🛰️ Ghost Radar", "🕯️ Evidence Séance", "🗣️ Ask the Ghost", "📜 BISO Briefing"])

with tab1:
    st.subheader("Ghost Radar")
    left, right = st.columns([1, 1])
    with left:
        st.markdown("#### Findings by severity")
        sev = df.groupby(["severity", "status"]).size().reset_index(name="count")
        st.bar_chart(sev, x="severity", y="count", color="status")
    with right:
        st.markdown("#### Findings by domain")
        domain_counts = df.groupby("domain").size().sort_values(ascending=False)
        st.bar_chart(domain_counts)
    st.markdown("#### Findings needing attention")
    priority = open_df.copy()
    priority["rule_priority"] = priority["severity"].map(
        {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
    ).fillna(0) * 100 + priority["days_open"].clip(upper=99)
    priority = priority.sort_values("rule_priority", ascending=False)
    show_cols = ["finding_id", "title", "domain", "severity", "status", "owner", "days_open", "evidence_status"]
    st.dataframe(priority[show_cols], use_container_width=True, hide_index=True)
    st.caption(f"Source: {data_source}. Metrics are calculated by Python rules, not generated by AI.")

with tab2:
    st.subheader("Evidence Séance")
    st.write("Find the evidence gaps that could slow an audit or control review.")
    if missing_evidence.empty:
        st.success("No open evidence gaps were found by the current rule.")
    else:
        st.dataframe(
            missing_evidence[["finding_id", "title", "domain", "severity", "owner", "evidence_status", "business_impact"]],
            use_container_width=True,
            hide_index=True,
        )
    if st.button("Summon an evidence checklist", type="primary"):
        context = missing_evidence.to_dict(orient="records")
        prompt = f"""You are The Ghost in the BISO, a careful security governance assistant.
Use ONLY the fictional finding records below. Do not claim evidence exists if it is marked missing, partial, or unknown.
Create an actionable evidence checklist grouped by finding. For each item give:
1) what to request,
2) likely accountable role (not a person's name),
3) a verification question,
4) what cannot be concluded from the available data.
Do not invent compliance requirements or claim this is a formal audit opinion.
Records: {json.dumps(context, ensure_ascii=False)}"""
        with st.spinner("Consulting the local model..."):
            st.markdown(call_ollama(model, [{"role": "user", "content": prompt}]))

with tab3:
    st.subheader("Ask the Ghost")
    st.write("Ask questions about the displayed sample register. The model receives only the current dataset context.")
    question = st.text_area(
        "Your question",
        value="Which open risks should the BISO follow up on first, and what should we ask the owners?",
        height=100,
    )
    if st.button("Investigate", type="primary", key="ask"):
        records = df.to_dict(orient="records")
        system = """You are The Ghost in the BISO, a cybersecurity governance copilot with a spooky but professional voice.
Answer using only the supplied records. Distinguish observed facts from recommendations.
Never invent an owner, evidence, deadline, policy, control, or incident. If information is missing, say so.
Prioritize based on severity, age, ownership, evidence status, and business impact. Give concise next steps.
This is a demo and not an automated compliance decision. Do not ask for secrets or real corporate data."""
        prompt = f"Question: {question}\n\nFictional risk register records (JSON):\n{json.dumps(records, ensure_ascii=False)}"
        with st.spinner("The ghost is reading the evidence..."):
            st.markdown(call_ollama(model, [{"role": "system", "content": system}, {"role": "user", "content": prompt}]))

with tab4:
    st.subheader("BISO Leadership Briefing")
    st.write("Generate a short briefing from calculated metrics and fictional findings.")
    if st.button("Generate briefing", type="primary"):
        facts = {
            "source": data_source,
            "total_findings": int(len(df)),
            "open_findings": int(len(open_df)),
            "critical_or_high_open": int(len(critical_open)),
            "open_30_days_or_more": int(len(stale_open)),
            "open_missing_owner": int(len(missing_owner)),
            "open_evidence_gaps": int(len(missing_evidence)),
            "highest_priority_open_findings": priority[["finding_id", "title", "severity", "days_open", "owner", "business_impact"]].head(5).to_dict(orient="records"),
        }
        prompt = f"""Write a leadership-ready BISO risk briefing from these calculated facts.
Structure: Executive signal (2 sentences), Top concerns (bullets), Recommended follow-ups (bullets), Data limitations.
Keep it under 250 words. Be specific but do not exaggerate. Do not invent facts or imply an incident has occurred.
Use an atmospheric one-line opening, then professional business language.
Facts: {json.dumps(facts, ensure_ascii=False)}"""
        with st.spinner("Preparing the briefing..."):
            briefing = call_ollama(model, [{"role": "user", "content": prompt}])
            st.markdown(briefing)
            st.download_button(
                "Download briefing as Markdown",
                data=briefing,
                file_name="biso-ghost-briefing.md",
                mime="text/markdown",
            )

st.divider()
st.caption("Prototype only • Fictional sample data • Human review required • No connection to enterprise systems")
st.markdown(
    '<span class="small-muted">Built with Streamlit + Ollama + an open-weight local model. '
    'The interface is spooky; risk calculations remain transparent and rule-based.</span>',
    unsafe_allow_html=True,
)

