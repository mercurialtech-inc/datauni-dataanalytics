# Analytics Chat Assistant  
**Metadata-Driven AI for Explainable Business Analytics**

This project demonstrates a **production-grade Analytics Chat Assistant** that enables users to explore **Marketing, Revenue, and Sports analytics** through natural language — without writing SQL, navigating dashboards, or relying on ad-hoc analyst support.

The system combines **deterministic analytics logic**, **metadata-driven chart intelligence**, and **Retrieval-Augmented Generation (RAG)** using Google Gemini to deliver **explainable, non-hallucinating insights**.

This is not a chatbot demo.  
It is an **analytics operating layer** designed to sit on top of real BI infrastructure.

---

## 🔗 Live Demo

- **Analytics Chat (Live):**  
  https://analytics-chat-17391180742.us-central1.run.app

- **Reset Chat Session:**  
  https://analytics-chat-17391180742.us-central1.run.app/reset_session

- **How to try chat:**  
  https://github.com/mercurialtech-inc/datauni-dataanalytics/blob/master/analytics_chat/docs/How%20to%20Try%20the%20Analytics%20Chat%20Assistant.pdf

### Try typing:
- `Why did CAC increase?`
- `What does this chart show?`
- `Switch to sports` → `What is xG?`

---

## 🚀 Key Capabilities

### Natural Language → Analytics Resolution
- Converts user questions into **validated filters, charts, and explanations**
- Maintains **session-aware analytical context**
- Supports conversational follow-ups (add, remove, explain, switch domain)

### Deterministic & Governed Analytics
- Canonical filters and dimensions only
- Explicit include / exclude / clear semantics
- No guessing, no free-text SQL generation
- Fully auditable analytical logic

### Metadata-Driven Intelligence
All analytical behavior is driven by metadata stored in **BigQuery**, including:
- Chart catalog
- Metric definitions
- Diagnostic patterns
- Executive explanations
- Known caveats

### Explainable RAG (No Hallucination)
- Gemini is used **only** to summarize retrieved metadata
- If no explanation exists, the system responds safely
- No speculative answers or fabricated insights

### Multi-Domain Architecture
The same system supports:
- **Marketing Analytics** (CAC, channels, efficiency)
- **Revenue Analytics** (products, subscriptions, deals)
- **Sports Analytics** (xG, goals, defensive metrics)

Each domain has its own:
- Filter grammar
- Chart vocabulary
- Metric definitions

All domains share a common resolver and RAG pipeline.

---

## 🧠 Architecture Overview

**High-level flow:**

1. User asks a question in natural language  
2. Intent is classified (diagnostic, definition, interpretation, chart discovery)  
3. Filters and chart selection are resolved deterministically  
4. Metadata is retrieved from BigQuery  
5. Gemini generates an executive-friendly explanation  
6. Looker Studio dashboard is embedded with applied filters  

---

## 📁 Project Structure

Organized, modular, and production-oriented:

### `ddl/`
BigQuery schema definitions:
- `metadata.chart_catalog.sql`
- `metadata.rag_metrics.sql`
- `metadata.rag_charts.sql`
- `metadata.rag_diagnostics.sql`

---

### `inserts/`
Metadata population scripts:
- `metadata.chart_catalog__insert.sql`
- `metadata.rag_metrics__insert.sql`
- `metadata.rag_charts__insert.sql`
- `metadata.rag_diagnostics__insert.sql`

These define:
- Chart purpose and usage
- Metric definitions and interpretations
- Diagnostic patterns (e.g. “why CAC increased”)
- Executive-level explanation templates

---

### `flask/`
Application logic:
- `app.py` — request routing, domain handling, filter resolution, session management
- `rag_engine.py` — intent classification, metadata retrieval, Gemini summarization

---

### `docs/`
Project documentation:
- **Analytics Chat Assistant — Executive Summary.pdf**
- **How to Try the Analytics Chat Assistant.pdf**

---

## 🛠 Tools Used

**Google Gemini · BigQuery · Python (Flask) · Looker Studio · Docker · Cloud Run**

---

## 🎯 Design Principles

- **Trust over novelty** — analytics must be explainable
- **Metadata first** — AI responds only to governed information
- **Domain-aware** — no mixing of metrics across contexts
- **Safe defaults** — graceful fallbacks when metadata is missing
- **Production mindset** — containerized, deployable, scalable

---

## 📊 Intended Use Cases

- Executive self-service analytics  
- Analytics enablement for non-technical stakeholders  
- AI-assisted BI layer on top of Looker / Tableau / Power BI  
- Portfolio demonstration of AI + analytics system design  

---

## 📝 Final Notes

This project demonstrates:
- Senior-level analytics judgment
- Responsible AI application
- Product-oriented thinking
- End-to-end system ownership

It is designed to reflect how **modern analytics platforms should be built** — not just how dashboards or chatbots are created.
