# rag_engine.py
from google.cloud import bigquery
import os
import google.generativeai as genai

# Force Gemini to use API key (NOT ADC)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))



# ============================================
# CONFIG
# ============================================

BQ_PROJECT = "datauni-analytics"
BQ_DATASET = "metadata"

bq = bigquery.Client(project=BQ_PROJECT)


# ============================================
# QUESTION CLASSIFICATION
# ============================================

# rag_engine.py

def fetch_rag_diagnostics(question: str, domain: str | None = None) -> dict:
    """
    INTENT-LEVEL diagnostics only.
    Must NEVER accept chart_id or fetch data.
    """
    rag_type = classify_rag_question(question)

    return {
        "rag_type": rag_type,
        "skip_chart_navigation": rag_type in {
            "diagnostic",
            "action",
            "interpretation",
            "definition",
            "chart_explanation",
            "chart_discovery",
        },
        "domain": domain,
    }



def classify_rag_question(text: str) -> str | None:
    t = (text or "").lower()

    if any(w in t for w in [
        "why", "reason", "what caused", "explain increase", "explain decrease",
        "increase", "decrease", "drop", "spike", "changed"
    ]):
        return "diagnostic"

    if any(w in t for w in [
        "what should", "what do we check", "next step", "how do we fix"
    ]):
        return "action"

    if any(w in t for w in [
        "is this good", "is this bad", "healthy", "normal", "ok to"
    ]):
        return "interpretation"

    if any(w in t for w in [
        "what is", "define", "meaning of", "explain metric"
    ]):
        return "definition"

    if any(w in t for w in [
        "what does this chart", "what am i looking at"
    ]):
        return "chart_explanation"

    if any(w in t for w in [
        "which chart", "what chart", "where do i see"
    ]):
        return "chart_discovery"

    return None


def should_skip_chart_navigation(q: str) -> bool:
    """
    Diagnostic / explanatory questions should NOT trigger chart navigation.
    """
    return classify_rag_question(q) in {
        "diagnostic",
        "action",
        "interpretation",
        "definition",
        "chart_explanation",
        "chart_discovery",
    }


# ============================================
# BIGQUERY HELPER (POSITIONAL PARAMS)
# ============================================

def run_bq(query: str, *params):
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(f"p{i}", "STRING", v)
            for i, v in enumerate(params)
        ]
    )

    job = bq.query(query, job_config=job_config)
    return [dict(row) for row in job.result()]


# ============================================
# RETRIEVERS
# ============================================

def get_diagnostics(domain: str, chart_id: str):
    """
    chart → primary_metrics → diagnostics
    """
    query = """
    WITH chart_metrics AS (
        SELECT DISTINCT metric
        FROM `metadata.rag_charts`,
        UNNEST(primary_metrics) AS metric
        WHERE chart_id = @p0
          AND domain = @p1
    )
    SELECT
        d.metric_key,
        d.change_type,
        d.likely_causes,
        d.checks_to_perform,
        d.exec_friendly_summary
    FROM `metadata.rag_diagnostics` d
    JOIN chart_metrics c
      ON d.metric_key = c.metric
    WHERE d.domain = @p1
    ORDER BY d.metric_key, d.change_type
    """
    return run_bq(query, chart_id, domain)


def get_metric_definition(domain: str, chart_id: str):
    query = """
    SELECT
      metric_name,
      definition,
      calculation_summary
    FROM `metadata.rag_metrics`
    WHERE domain = @p0
      AND metric_key IN (
        SELECT metric
        FROM `metadata.rag_charts`,
        UNNEST(primary_metrics) AS metric
        WHERE chart_id = @p1
      )
    """
    return run_bq(query, domain, chart_id)


def get_metric_interpretation(domain: str, chart_id: str):
    query = """
    SELECT
      metric_name,
      interpretation_notes
    FROM `metadata.rag_metrics`
    WHERE domain = @p0
      AND metric_key IN (
        SELECT metric
        FROM `metadata.rag_charts`,
        UNNEST(primary_metrics) AS metric
        WHERE chart_id = @p1
      )
    """
    return run_bq(query, domain, chart_id)


def get_chart_explanation(domain: str, chart_id: str):
    query = """
    SELECT
        chart_id,
        when_to_use,
        caveats
    FROM `metadata.rag_charts`
    WHERE chart_id = @p0
      AND domain = @p1
    """
    return run_bq(query, chart_id, domain)



def get_chart_discovery(domain: str, chart_id: str):
    """
    Simple discovery: show relevant charts in the domain.
    (Can be enhanced later to be metric-driven.)
    """
    query = """
    SELECT
      chart_id,
      when_to_use,
      caveats
    FROM `metadata.rag_charts`
    WHERE domain = @p0
    ORDER BY chart_id
    """
    return run_bq(query, domain)


# ============================================
# RETRIEVER REGISTRY
# ============================================

RAG_RETRIEVERS = {
    "diagnostic": "get_diagnostics",
    "action": "get_diagnostics",
    "interpretation": "get_metric_interpretation",
    "definition": "get_metric_definition",
    "chart_explanation": "get_chart_explanation",
    "chart_discovery": "get_chart_discovery",
}


# ============================================
# RAG ORCHESTRATOR
# ============================================

def run_rag(domain: str, chart_id: str | None, question: str) -> str | None:
    """
    Orchestrates:
    intent → retriever → Gemini
    Includes graceful fallback when metadata is missing.
    """
    if not chart_id:
        return None

    rag_type = classify_rag_question(question)
    if not rag_type:
        return None

    retriever_name = RAG_RETRIEVERS.get(rag_type)
    if not retriever_name:
        return None

    retriever = globals()[retriever_name]

    data = retriever(domain, chart_id)

    # ✅ NEW: Graceful fallback when metadata is missing
    if not data:
        return (
            "No explanation metadata is available for this chart yet. "
            "This chart is intended for exploratory analysis, and additional "
            "documentation can be added during the next metadata enrichment phase."
        )

    return summarize_with_gemini(data, question)



# ============================================
# GEMINI SUMMARIZATION
# ============================================

def summarize_with_gemini(data, user_question):
    prompt = f"""
You are a senior analytics advisor.

User question:
{user_question}

Known facts (from metadata, not raw data):
{data}

Respond concisely in executive language.
- Do NOT speculate
- Focus on likely causes, interpretation, or next checks
- Be neutral and factual
"""

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return getattr(response, "text", None)
