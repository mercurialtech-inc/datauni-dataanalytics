import os
import json
import urllib.parse
import re

from flask import (
    Flask,
    request,
    render_template_string,
    session,
    redirect,
    url_for,
)

from google.cloud import bigquery
import google.generativeai as genai
from rapidfuzz import fuzz, distance

from rag_engine import (
    classify_rag_question,
    run_rag,
    should_skip_chart_navigation,
    fetch_rag_diagnostics,
)


# =======================================
# FLASK SETUP
# =======================================

app = Flask(__name__)
app.secret_key = "secret_chat_key_123"   # demo only


# =======================================
# GEMINI CONFIG
# =======================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ Gemini API key loaded successfully.")
else:
    print("⚠ GEMINI_API_KEY not found — Gemini disabled")


# =======================================
# DOMAINS
# =======================================

DOMAINS = {"marketing", "revenue", "sports"}

# canonical master chart ids per domain
DOMAIN_MASTER_CHART = {
    "marketing": "mktg_master_dashboard",
    "revenue": "rev_master_dashboard",   # future
    "sports": "sprt_master_dashboard",   # future
}

# High-level "concept" → chart_id mapping per domain
CHART_CONCEPT_MAP = {
    "marketing": {
        "master": "mktg_master_dashboard",
        "spend": "mktg_total_spend",
        "quality": "mktg_lead_quality",
        "score": "mktg_avg_lead_score",
        "funnel": "mktg_lead_funnel",
        "efficiency": "mktg_efficiency",
        "performance": "mktg_campaign_perf_summary",
        "trend": "mktg_monthly_spend_leads",
    },
    "revenue": {},
    "sports": {},
}


# =======================================
# MARKETING DIMENSIONS (CAMPAIGN / CHANNEL)
# =======================================

CAMPAIGNS = [
    "Kickoff",
    "Boost",
    "Acquire",
    "Signups",
    "Grow",
    "Expand",
    "Wave",
    "Outreach",
    "Surge",
    "Engage",
]

CHANNELS = [
    "partnership",
    "organic",
    "referral",
    "paid_search",
    "facebook",
    "email",
]

CAMPAIGN_CANON = {c.lower(): c for c in CAMPAIGNS}
CHANNEL_CANON = {c.lower(): c for c in CHANNELS}

VALID_CAMPAIGNS = set(CAMPAIGN_CANON.keys())
VALID_CHANNELS = set(CHANNEL_CANON.keys())

# Looker Studio special separators
LOOKER_SPACE = "\uE000"
LOOKER_CLAUSE_SEP = "\uE001"


# =======================================
# REVENUE — DIMENSIONS (AUTHORITATIVE)
# =======================================

REVENUE_CLUBS = [
    "Aston Villa",
    "Bournemouth",
    "Brighton",
    "Leeds United",
    "Leicester City",
    "Everton",
    "Liverpool",
    "Arsenal",
    "Brentford",
    "Chelsea",
    "West Ham United",
    "Tottenham Hotspur",
    "Manchester United",
    "Newcastle United",
    "Norwich City",
    "Sheffield United",
    "Watford",
]

REVENUE_PRODUCT_CATEGORIES = [
    "Analytics Report",
    "Data Dashboard",
    "Financial Analysis",
]

REVENUE_SUBSCRIPTIONS = [
    "Elite Intelligence",
    "Scouting Suite",
    "Youth Dev Package",
    "Basic Analytics",
    "Performance Suite",
    "General Subscription",
]

REVENUE_PRODUCT_NAMES = [
    "Youth Academy Analytics",
    "Fan Engagement Analysis",
    "Match Performance Report",
    "Player Scouting Dashboard",
    "Sponsorship ROI Audit",
    "Club Financial Benchmarking",
]

REVENUE_DEAL_STAGE_LABELS = [
    "Prospecting",
    "Qualified",
    "Proposal",
    "Negotiation",
    "Closed Won",
    "Closed Lost",
]

REVENUE_LEAGUES = [
    "Premier League",
    "Championship",
]


REVENUE_CLUB_CANON = {c.lower(): c for c in REVENUE_CLUBS}
REVENUE_CATEGORY_CANON = {c.lower(): c for c in REVENUE_PRODUCT_CATEGORIES}
REVENUE_SUBSCRIPTION_CANON = {s.lower(): s for s in REVENUE_SUBSCRIPTIONS}
REVENUE_PRODUCT_CANON = {p.lower(): p for p in REVENUE_PRODUCT_NAMES}
REVENUE_LEAGUE_CANON = {l.lower(): l for l in REVENUE_LEAGUES}
REVENUE_DEAL_STAGE_CANON = {d.lower(): d for d in REVENUE_DEAL_STAGE_LABELS}

RAG_RETRIEVERS = {
    "diagnostic": "get_diagnostics",
    "action": "get_diagnostics",
    "interpretation": "get_metric_interpretation",
    "definition": "get_metric_definition",
    "chart_explanation": "get_chart_explanation",
    "chart_discovery": "get_chart_discovery",
}


REVENUE_DOMAIN_FILTER_CONFIG = {
    "clubs": {
        "values": REVENUE_CLUBS,
        "canon": REVENUE_CLUB_CANON,
        "df": "df4",
    },
    "product_categories": {
        "values": REVENUE_PRODUCT_CATEGORIES,
        "canon": REVENUE_CATEGORY_CANON,
        "df": "df5",
    },
    "subscriptions": {
        "values": REVENUE_SUBSCRIPTIONS,
        "canon": REVENUE_SUBSCRIPTION_CANON,
        "df": "df6",
    },
    "product_names": {
        "values": REVENUE_PRODUCT_NAMES,
        "canon": REVENUE_PRODUCT_CANON,
        "df": "df7",
    },
    "leagues": {
        "values": REVENUE_LEAGUES,
        "canon": REVENUE_LEAGUE_CANON,
        "df": "df8",
    },
    "deal_stage_labels": {
        "values": REVENUE_DEAL_STAGE_LABELS,
        "canon": REVENUE_DEAL_STAGE_CANON,
        "df": "df9",
    },
    "channels": {
        "values": CHANNELS,
        "canon": CHANNEL_CANON,
        "df": "df10",
    },
}

# =======================================
# SPORTS — DIMENSIONS (AUTHORITATIVE)
# =======================================

SPORTS_CLUBS = [
    "Arsenal",
    "Aston Villa",
    "Chelsea",
    "Liverpool",
    "Manchester United",
    "Tottenham Hotspur",
]

SPORTS_SEASONS = [
    "2019-20",
    "2020-21",
    "2021-22",
    "2022-23",
    "2023-24",
    "2024-25",
]

SPORTS_CUSTOMER_TYPES = [
    "paid",
    "freemium",
]

SPORTS_SUBSCRIPTION_TIERS = [
    "Elite+Performance",
    "Elite",
    "Trial",
]

SPORTS_CHART_CONCEPT_MAP = {
    "master": "sprt_master_dashboard",

    "shots_trend": "sprt_shots_on_target_trend",
    "goals_trend": "sprt_total_goals_trend",

    "goals_vs_xg": "sprt_goals_vs_xg",
    "goals_conversion": "sprt_goal_conversion_pct",

    "conceded_vs_xgc": "sprt_conceded_vs_xgc",
    "defensive_discipline": "sprt_defensive_discipline",
    "defensive_profile": "sprt_defensive_seasonal_profile",
}


SPORTS_CLUB_CANON = {c.lower(): c for c in SPORTS_CLUBS}
SPORTS_SEASON_CANON = {s.lower(): s for s in SPORTS_SEASONS}
SPORTS_CUSTOMER_TYPE_CANON = {c.lower(): c for c in SPORTS_CUSTOMER_TYPES}
SPORTS_TIER_CANON = {t.lower(): t for t in SPORTS_SUBSCRIPTION_TIERS}

# df mapping based on your Looker URLs:
# - df2 = club (single-select)
# - df3 = season
# - df4 = customer_type
# - df5 = subscription_tier
SPORTS_DOMAIN_FILTER_CONFIG = {
    "clubs": {
        "values": SPORTS_CLUBS,
        "canon": SPORTS_CLUB_CANON,
        "df": "df2",
        "single_select": True,   # for our own logic
    },
    "seasons": {
        "values": SPORTS_SEASONS,
        "canon": SPORTS_SEASON_CANON,
        "df": "df3",
    },
    "customer_types": {
        "values": SPORTS_CUSTOMER_TYPES,
        "canon": SPORTS_CUSTOMER_TYPE_CANON,
        "df": "df4",
    },
    "subscription_tiers": {
        "values": SPORTS_SUBSCRIPTION_TIERS,
        "canon": SPORTS_TIER_CANON,
        "df": "df5",
    },
}


def default_sports_filters_state():
    """
    Sports filter state mirrors revenue:
    { entity: { include: None, exclude: [] } }
    """
    return {
        entity: {
            "include": None,
            "exclude": [],
        }
        for entity in SPORTS_DOMAIN_FILTER_CONFIG.keys()
    }



# =======================================
# REVENUE — FILTER VERBS & TOKENS
# =======================================

REVENUE_FILTER_VERBS = {
    "add",
    "remove",
    "include",
    "exclude",
    "reset",
    "clear",
    "only",
    "except",
    "without",
    "apply",
}

# All possible value tokens for any revenue entity (lowercased)
REVENUE_ENTITY_TOKENS = set()
for meta in REVENUE_DOMAIN_FILTER_CONFIG.values():
    for v in meta["values"]:
        REVENUE_ENTITY_TOKENS.add(v.lower())

# "All X" phrases → reset that specific entity only
REVENUE_ALL_ENTITY_PHRASES = {
    "clubs": {
        "all clubs",
        "show all clubs",
        "reset clubs",
        "reset club",
        "clear clubs",
        "clear club",
    },
    "product_categories": {
        "all product categories",
        "all categories",
        "show all product categories",
        "show all categories",
        "reset product categories",
        "reset categories",
        "clear product categories",      # ✅ your phrase
        "clear product category",
        "clear categories",
    },
    "subscriptions": {
        "all subscriptions",
        "show all subscriptions",
        "reset subscriptions",
        "clear subscriptions",
    },
    "product_names": {
        "all products",
        "all product names",
        "show all products",
        "reset products",
        "clear products",
        "clear products names",
        "clear products name",
    },
    "leagues": {
        "all leagues",
        "show all leagues",
        "reset leagues",
        "reset league",
        "clear leagues",
        "clear league",
    },
    "deal_stage_labels": {
        "all deal stages",
        "all deal stage labels",
        "show all deal stages",
        "show all deal stage labels",
        "reset deal stages",
        "reset deal stage labels",
        "clear deal stages",
        "clear deal stage labels",       # ✅ your phrase (plural)
        "clear deal stage label",        # ✅ your phrase (singular)
        "clear deal stage", 
    },
    "channels": {
        "all channels",
        "show all channels",
        "reset channels",
        "clear channels",
    },
}




# =======================================
# REVENUE — CHART ROUTING
# =======================================

REVENUE_MASTER_CHART = "rev_master_dashboard"

# Concept → chart_id (not raw phrases)
REVENUE_CHART_CONCEPT_MAP = {
    # master / overview
    "master": "rev_master_dashboard",

    # trends
    "monthly_revenue_trend": "rev_monthly_revenue_trend",
    "mrr_trend": "rev_monthly_mrr_trend",

    # club views
    "revenue_by_club": "rev_revenue_by_club",
    "top_clubs": "rev_top_5_clubs_by_spend",

    # product views
    "revenue_by_product": "rev_revenue_by_product",
    "revenue_by_category": "rev_revenue_by_product_category",

    # mix
    "product_mix_by_category": "rev_product_revenue_mix_by_category",
    "subscription_mix": "rev_subscription_revenue_mix",

    # subscriptions
    "subscription_penetration": "rev_subscription_penetration_by_club",
    "subscription_composition": "rev_subscription_product_composition",
}

# Phrases like "all clubs", "all product categories", etc.
REVENUE_ENTITY_ALL_PHRASES = {
    "clubs": {
        "all clubs",
        "show all clubs",
        "reset clubs",
        "clear clubs",
    },
    "product_categories": {
        "all product categories",
        "show all product categories",
        "reset product categories",
        "clear product categories",
    },
    "product_names": {
        "all products",
        "show all products",
        "reset products",
        "clear products",
    },
    "subscriptions": {
        "all subscriptions",
        "show all subscriptions",
        "reset subscriptions",
        "clear subscriptions",
    },
    "leagues": {
        "all leagues",
        "show all leagues",
        "reset leagues",
        "clear leagues",
    },
    "deal_stage_labels": {
        "all deal stages",
        "show all deal stages",
        "reset deal stages",
        "clear deal stages",
    },
    "channels": {
        "all channels",
        "show all channels",
        "reset channels",
        "clear channels",
    },
}


def handle_revenue_all_entity_commands(text: str, filters: dict) -> bool:
    """
    If the message is an 'all X' command (all clubs, all product categories, etc.),
    reset JUST that entity to All and return True. Otherwise return False.
    """
    t = normalized_text(text)

    for entity, phrases in REVENUE_ENTITY_ALL_PHRASES.items():
        if t in phrases:
            filters[entity] = default_field_filter_state()
            return True

    return False


# =======================================
# SYNONYMS & COMMAND PHRASES
# =======================================

STOP_WORDS = {
    "and", "or", "the", "to", "in", "on", "at", "a", "an", "of",
    "for", "with", "by", "from"
}

SYNONYMS = {
    "fb": "facebook",
    "meta": "facebook",
    "ppc": "paid_search",
    "google": "paid_search",
    "google ads": "paid_search",
}

GLOBAL_ALL_PHRASES = {
    "all",
    "everything",
    "show all",
    "show everything",
    "all filters",
    "reset filters",
    "clear filters",
    "reset",
    "clear all",
    "remove filter",
    "remove filters",
}

ALL_CAMPAIGN_PHRASES = {
    "all campaigns",
    "show all campaigns",
    "reset campaigns",
    "clear campaigns",
}

ALL_CHANNEL_PHRASES = {
    "all channels",
    "show all channels",
    "reset channels",
    "clear channels",
}

REVENUE_STRONG_PHRASES = {
    "data dashboard",
    "financial dashboard",
    "revenue dashboard",
    "subscription dashboard",
    "billing dashboard",
    "financial analysis",
}

# =======================================
# REVENUE SYNONYMS (user-friendly → canonical key)
# =======================================

REVENUE_SYNONYMS = {
    # Clubs
    "villa": "aston villa",
    "aston": "aston villa",
    "avfc": "aston villa",
    "bmouth": "bournemouth",
    "brighton hove": "brighton",
    "leeds": "leeds united",
    "leicester": "leicester city",
    "everton fc": "everton",
    "liverpool fc": "liverpool",
    "arsenal fc": "arsenal",
    "brentford fc": "brentford",
    "chelsea fc": "chelsea",
    "west ham": "west ham united",
    "spurs": "tottenham hotspur",
    "tottenham": "tottenham hotspur",
    "man utd": "manchester united",
    "man u": "manchester united",
    "manchester u": "manchester united",
    "newcastle": "newcastle united",
    "norwich": "norwich city",
    "sheffield": "sheffield united",
    "watford fc": "watford",

    # Leagues
    "epl": "premier league",
    "pl": "premier league",
    "english premier league": "premier league",

    # Product categories (very minor typos / variants)
    "data dashbord": "data dashboard",
    "data dashboards": "data dashboard",
    "analytics reports": "analytics report",
    "financial analyses": "financial analysis",
}

# =======================================
# SPORTS — "ALL X" PHRASES & NLP FALLBACK
# =======================================

SPORTS_ENTITY_ALL_PHRASES = {
    "clubs": {
        "all clubs",
        "show all clubs",
        "reset clubs",
        "clear clubs",
    },
    "seasons": {
        "all seasons",
        "show all seasons",
        "reset seasons",
        "clear seasons",
    },
    "customer_types": {
        "all customer types",
        "show all customer types",
        "reset customer types",
        "clear customer types",
    },
    "subscription_tiers": {
        "all subscription tiers",
        "show all subscription tiers",
        "reset subscription tiers",
        "clear subscription tiers",
    },
}



SPORTS_CLUB_SYNONYMS = {
    # Arsenal
    "ars": "arsenal",
    "afc": "arsenal",

    # Aston Villa
    "avfc": "aston villa",
    "villa": "aston villa",

    # Chelsea
    "chel": "chelsea",
    "cfc": "chelsea",

    # Liverpool
    "lfc": "liverpool",
    "liv": "liverpool",

    # Manchester United
    "man u": "manchester united",
    "man utd": "manchester united",
    "utd": "manchester united",

    # Spurs
    "spurs": "tottenham hotspur",
}

SPORTS_SUB_TIER_SYNONYMS = {
    "elite performance": "Elite+Performance",
    "elite plus performance": "Elite+Performance",
    "elite+ performance": "Elite+Performance",
}


# =======================================
# BIGQUERY CLIENT & CHART CATALOG
# =======================================

BQ_PROJECT = os.getenv("BQ_PROJECT", "datauni-analytics")
BQ_DATASET = "metadata"
BQ_TABLE = "chart_catalog"

bq_client = bigquery.Client(project=BQ_PROJECT)


def load_chart_catalog():
    """
    Loads metadata.chart_catalog from BigQuery and returns a dict:
        { chart_id: {meta...}, ... }

    Safely handles ARRAY or CSV for tags / allowed_filters.
    project_name is normalized to lowercase to act as the "domain".
    """

    query = f"""
        SELECT
            chart_id,
            project_name,
            chart_title,
            description,
            tags,
            allowed_filters,
            render_engine,
            looker_report_id,
            looker_page_id,
            default_viz_type,
            sql_template
        FROM `{BQ_PROJECT}.{BQ_DATASET}.{BQ_TABLE}`
        WHERE is_active = TRUE
    """

    rows = bq_client.query(query).result()
    catalog = {}

    for r in rows:
        # tags → list[str]
        tags = []
        if r.tags:
            if isinstance(r.tags, list):
                tags = [t.lower().strip() for t in r.tags]
            else:
                tags = [t.lower().strip() for t in str(r.tags).split(",")]

        # allowed_filters → list[str]
        allowed_filters = []
        if r.allowed_filters:
            if isinstance(r.allowed_filters, list):
                allowed_filters = [f.lower().strip() for f in r.allowed_filters]
            else:
                allowed_filters = [
                    f.lower().strip() for f in str(r.allowed_filters).split(",")
                ]

        catalog[r.chart_id] = {
            "chart_id": r.chart_id,
            "project_name": (r.project_name or "").lower(),   # used for domain
            "chart_title": r.chart_title,
            "description": r.description,
            "tags": tags,
            "allowed_filters": allowed_filters,
            "render_engine": r.render_engine,
            "looker_report_id": r.looker_report_id,
            "looker_page_id": r.looker_page_id,
            "default_viz_type": r.default_viz_type,
            "sql_template": r.sql_template,
        }

    return catalog


CHART_CATALOG = load_chart_catalog()
print(f"📊 Loaded {len(CHART_CATALOG)} charts from BigQuery")


# =======================================
# BASIC TEXT HELPERS
# =======================================

def normalized_text(text: str) -> str:
    return (text or "").strip().lower()


def is_global_all_command(text: str) -> bool:
    return normalized_text(text) in GLOBAL_ALL_PHRASES


def is_all_campaigns_command(text: str) -> bool:
    return normalized_text(text) in ALL_CAMPAIGN_PHRASES


def is_all_channels_command(text: str) -> bool:
    return normalized_text(text) in ALL_CHANNEL_PHRASES


# =======================================
# EXPLICIT CHART OVERRIDE
# =======================================

def extract_explicit_chart_id(user_text: str):
    """
    Supports explicit override:
      "chart=mktg_xxx"
      "chart: mktg_xxx"
      "chart mktg_xxx"
    """
    txt = normalized_text(user_text)

    if "chart=" in txt:
        return txt.split("chart=")[-1].strip()

    if "chart:" in txt:
        return txt.split("chart:")[-1].strip()

    if txt.startswith("chart "):
        return txt.replace("chart", "").strip()

    return None


# =======================================
# DOMAIN DETECTION / SWITCH
# =======================================

DOMAIN_KEYWORDS = {
    "marketing": {
        "marketing", "campaign", "campaigns", "ad", "ads",
        "lead", "leads", "cac", "cpc", "cpm"
    },
    "revenue": {
        "revenue", "mrr", "arr", "billing", "invoice", "invoices",
        "subscription", "subscriptions"
    },
    "sports": {
        "sport", "sports", "match", "matches", "game", "games",
        "fixture", "fixtures", "player", "players",
        "club", "clubs", "goal", "goals", "xg", "shots", "passes"
    },
}

# =======================================
# DOMAIN FILTER CONFIG (MARKETING ONLY FOR NOW)
# =======================================

DOMAIN_FILTER_CONFIG = {
    "marketing": {
        "entities": {
            "campaigns": {
                "values": CAMPAIGNS,
                "canon": CAMPAIGN_CANON,
                "df": "df3",
            },
            "channels": {
                "values": CHANNELS,
                "canon": CHANNEL_CANON,
                "df": "df4",
            },
        },
        "use_dependencies": True,
    },
}


def handle_sports_all_commands(user_text: str, filters: dict):
    """
    Handles phrases like:
      - 'all clubs'
      - 'all seasons'
      - 'all customer types'
      - 'all subscription tiers'
    Resets ONLY that one entity to All.
    Returns (filters, handled_bool).
    """
    t = normalized_text(user_text)
    handled = False

    for entity, phrases in SPORTS_ENTITY_ALL_PHRASES.items():
        if t in phrases:
            filters[entity] = default_field_filter_state()
            handled = True

    return filters, handled



def summarize_sports_filters(filters: dict) -> str:
    """
    Compact summary for sports, similar to revenue summary.
    """
    if not filters:
        return "Sports: All"

    parts = []
    for entity, meta in SPORTS_DOMAIN_FILTER_CONFIG.items():
        state = filters.get(entity) or {}
        include = state.get("include")
        exclude = state.get("exclude") or []

        if include is None and not exclude:
            continue  # All

        label = entity.replace("_", " ")

        if include:
            parts.append(f"{label}={','.join(include)}")
        if exclude:
            parts.append(f"{label}≠{','.join(exclude)}")

    return "Sports: All" if not parts else " | ".join(parts)

def pick_revenue_chart(user_text: str) -> str:
    """
    Map revenue-domain user text → specific revenue chart id.

    Priority:
    1) Highly specific phrases (monthly revenue, MRR, top spend, by club/product/category)
    2) Phrase-based fallback via REVENUE_CHART_CONCEPT_MAP
    3) Default: rev_master_dashboard
    """

    t = (user_text or "").lower().strip()

    # ----- Explicit trend combos -----
    if "monthly revenue" in t or "revenue trend" in t or "revenue over time" in t:
        return "rev_monthly_revenue_trend"

    if "mrr" in t:
        return "rev_monthly_mrr_trend"

    # ----- Top spend / top revenue -----
    if "top" in t and ("spend" in t or "revenue" in t):
        # e.g. "top 5 spend", "top revenue clubs", "top 5 clubs by revenue"
        return "rev_top_5_clubs_by_spend"

    # ----- Club revenue views -----
    if "revenue by club" in t or "by club" in t or "club revenue" in t:
        return "rev_revenue_by_club"

    # ----- Product views -----
    if "by product" in t:
        return "rev_revenue_by_product"

    if "by category" in t or "product category" in t:
        return "rev_revenue_by_product_category"

    # ----- Mix views -----
    if "product mix" in t:
        return "rev_product_revenue_mix_by_category"

    if "subscription mix" in t or "subscription revenue mix" in t:
        return "rev_subscription_revenue_mix"

    # ----- Subscription penetration / composition -----
    if "subscription penetration" in t:
        return "rev_subscription_penetration_by_club"

    if "subscription composition" in t or "subs composition" in t:
        return "rev_subscription_product_composition"

    # ----- Fallback via concept map -----
    for phrase in sorted(REVENUE_CHART_CONCEPT_MAP.keys(), key=len, reverse=True):
        if phrase in t:
            return REVENUE_CHART_CONCEPT_MAP[phrase]

    # ----- Final fallback -----
    return "rev_master_dashboard"


def pick_sports_chart(user_text: str) -> str | None:
    """
    Deterministic mapping from sports phrases → sports chart_id.
    Fallback is the sports master dashboard.
    """
    t = (user_text or "").lower().strip()

    # 1️⃣ Master dashboard
    MASTER_PHRASES = {
        "elite intelligence dashboard",
        "sports dashboard",
        "main sports dashboard",
        "sports overview",
        "sports main chart",
        "sports master chart",
    }
    if any(p in t for p in MASTER_PHRASES):
        return "sprt_master_dashboard"

    # 2️⃣ Shots on Target
    if "shots on target" in t or "shots trend" in t:
        return "sprt_shots_on_target_trend"

    # 3️⃣ Total Goals trend
    if (
        "total goals" in t
        or "goals trend" in t
        or "goals over seasons" in t
        or ("goals" in t and "trend" in t)
    ):
        return "sprt_total_goals_trend"

    # 4️⃣ Goals vs xG
    if (
        "goals vs xg" in t
        or "goals vs expected goals" in t
        or "goals vs expected" in t
        or ("goals" in t and "expected goals" in t)
        or ("xg" in t and "goals" in t)
    ):
        return "sprt_goals_vs_xg"

    # 5️⃣ Conceded vs xGC
    if (
        "conceded vs xgc" in t
        or "conceded vs expected" in t
        or ("conceded" in t and "xgc" in t)
    ):
        return "sprt_conceded_vs_xgc"

    # 6️⃣ Goal conversion %
    if (
        "goal conversion" in t
        or "goals conversion" in t
        or "conversion %" in t
        or "conversion percent" in t
    ):
        return "sprt_goal_conversion_pct"

    # 7️⃣ Defensive views
    if "defensive discipline" in t:
        return "sprt_defensive_discipline"

    if (
        "defensive seasonal profile" in t
        or "defensive profile" in t
        or ("defensive" in t and "profile" in t)
    ):
        return "sprt_defensive_seasonal_profile"

    # 8️⃣ Fallback: master sports dashboard
    return "sprt_master_dashboard"


def is_revenue_chart_request(q: str) -> bool:
    """
    True when the message clearly refers to a *chart / view* in the
    revenue domain (trend, by club, top 5, etc).

    IMPORTANT:
    - Does NOT try to detect "filter-only" – that's handled in resolve().
    - 'add data dashboard' (no nav verb, no trend/by-club/top-5 wording)
      should NOT trigger a chart change.
    """

    t = (q or "").lower().strip()
    if not t:
        return False

    # 1) Strong patterns that clearly mean a specific chart
    STRONG_PATTERNS = [
        "mrr trend",
        "monthly revenue",
        "revenue trend",
        "revenue over time",
        "revenue by club",
        "revenue by product",
        "revenue by category",
        "product mix",
        "subscription mix",
        "subscription penetration",
        "subscription composition",
        "top 5",
        "top five",
        "top clubs",
        "top spend",
        "top revenue",
        "by club",
        "by product",
        "by category",
    ]
    if any(p in t for p in STRONG_PATTERNS):
        return True

    # 2) Nav verbs + generic chart words
    NAV_VERBS = {"show", "see", "open", "view", "display"}
    CHART_WORDS = {"dashboard", "chart", "overview", "report", "trend"}
    if any(v in t for v in NAV_VERBS) and any(w in t for w in CHART_WORDS):
        return True

    return False

def is_sports_chart_request(user_text: str) -> bool:
    """
    True when the message clearly refers to a *sports chart / view*.
    We keep this generous, so phrases like
    'shots on target trend', 'goals vs xg', 'defensive profile',
    'conceded vs expected' all count as chart requests.
    """
    if not user_text:
        return False

    t = user_text.lower().strip()

    # If it looks like a pure filter command, do a quick check
    FILTER_VERBS = {
        "add", "remove", "include", "exclude",
        "reset", "clear", "filter", "filters",
        "only", "except", "without",
    }
    if any(v in t for v in FILTER_VERBS):
        CHART_WORDS = {"trend", "xg", "xgc", "conversion", "dashboard", "chart", "profile"}
        if not any(w in t for w in CHART_WORDS):
            return False

    # Strong sports-chart phrases
    STRONG_PATTERNS = [
        "shots on target",
        "shots trend",
        "goals trend",
        "total goals",
        "goals over seasons",
        "goals vs xg",
        "goals versus xg",
        "goals vs expected goals",
        "goals vs expected",
        "expected goals",
        "conceded vs xgc",
        "conceded vs expected",
        "expected conceded",
        "defensive discipline",
        "defensive seasonal profile",
        "defensive profile",
        "goal conversion",
        "goals conversion",
        "conversion %",
        "elite intelligence dashboard",
        "sports dashboard",
    ]
    if any(p in t for p in STRONG_PATTERNS):
        return True

    # Generic chart words + sportsy terms
    NAV_VERBS = {"show", "see", "open", "view", "display"}
    CHART_WORDS = {"dashboard", "chart", "trend", "overview", "report"}
    SPORT_METRICS = {
        "shots", "goals", "xg", "xgc",
        "defensive", "conversion", "seasonal", "expected",
    }

    if any(v in t for v in NAV_VERBS) and any(w in t for w in CHART_WORDS):
        if any(m in t for m in SPORT_METRICS):
            return True

    return False



def is_sports_chart_only_request(user_text: str) -> bool:
    """
    True only for *pure navigation* messages in the sports domain
    that do NOT try to modify filters (no add/remove/etc.).

    Examples that should be True:
      - "elite intelligence dashboard"
      - "sports dashboard"
      - "shots on target trend"
      - "defensive profile"
      - "goals vs xg"

    Examples that should be False:
      - "add arsenal"
      - "remove liverpool"
      - "defensive profile and add arsenal"
    """
    if not user_text:
        return False

    t = user_text.lower().strip()

    # If it has filter verbs, it's not chart-only
    FILTER_VERBS = {
        "add", "remove", "include", "exclude",
        "reset", "clear", "filter", "filters",
        "only", "except", "without",
    }
    if any(v in t for v in FILTER_VERBS):
        return False

    # Strong “just navigation” phrases
    CHART_ONLY_PHRASES = {
        "elite intelligence",
        "elite intelligence dashboard",
        "sports dashboard",
        "main sports dashboard",
        "sports main chart",
        "sports master chart",
        "sports overview",
        "sports summary",
    }
    if any(p in t for p in CHART_ONLY_PHRASES):
        return True

    # Fallback: if it looks like a sports chart request at all
    # (and we already filtered out filter verbs above), treat as chart-only.
    return is_sports_chart_request(t)



def revenue_fuzzy_match_value(value: str, canon_map: dict, threshold: int = 80):
    """
    Return the canonical *key* (lowercase) from canon_map if fuzzy match found.
    canon_map is of the form: {lowercase_name: "Proper Label"}.

    Used by revenue_nlp_fallback so typos like 'arsenl' → 'arsenal',
    'chelsa' → 'chelsea', etc.
    """
    value = (value or "").lower().strip()
    if not value:
        return None

    # Exact key match
    if value in canon_map:
        return value

    # Fuzzy on keys
    best_score = 0
    best_key = None

    for k in canon_map.keys():
        score = fuzz.ratio(value, k)
        if score > best_score:
            best_score = score
            best_key = k

    if best_key and best_score >= threshold:
        return best_key

    return None





def default_filters_state_for_domain(domain: str):
    """
    Build an empty filter state using DOMAIN_FILTER_CONFIG.
    This is the ONLY place where filter structure is defined.
    """
    domain = domain or "marketing"
    entities = DOMAIN_FILTER_CONFIG[domain]["entities"]

    return {
        entity: default_field_filter_state()
        for entity in entities.keys()
    }


def detect_domain_switch(user_text: str, current_domain: str) -> str:
    """
    Domain routing with a strong lock:

    - Explicit phrases ('switch to revenue', 'go to sports', 'sports dashboard') always win.
    - Once you're in REVENUE or SPORTS, you STAY there unless the user explicitly
      asks to switch.
    - From MARKETING we allow implicit detection using high-level keywords only
      (NOT club names), and we bias revenue vs sports using 'revenue'/'goal' type words.
    """

    t = normalized_text(user_text)
    if not t:
        return current_domain or "marketing"

    # 0️⃣ Explicit switches ALWAYS win
    for d in DOMAINS:
        if f"switch to {d}" in t or f"go to {d}" in t or f"{d} dashboard" in t:
            return d

    # 🔒 1️⃣ Hard lock once you're in revenue/sports
    if current_domain in {"revenue", "sports"}:
        # Only explicit phrases above can move you out
        return current_domain

    # 2️⃣ From marketing (or None) → allow implicit detection
    hits = {d: 0 for d in DOMAINS}

    for d, words in DOMAIN_KEYWORDS.items():
        for w in words:
            if w in t:
                hits[d] += 1

    # No signals → stay where you are
    if all(v == 0 for v in hits.values()):
        return current_domain or "marketing"

    # Choose best domain by keyword hits
    best_domain = max(hits, key=hits.get)

    # If tie between revenue and sports, slightly bias REVENUE for "club"-type messages
    if hits.get("revenue", 0) == hits.get("sports", 0) and hits.get("revenue", 0) > 0:
        if "revenue" in t or "mrr" in t or "subscription" in t or "deal" in t:
            best_domain = "revenue"
        elif "goal" in t or "goals" in t or "xg" in t or "match" in t or "shots" in t:
            best_domain = "sports"

    chartish = any(
        kw in t for kw in ["chart", "dashboard", "trend", "summary", "overview", "report"]
    )

    # Only auto-switch from marketing if the message sounds chart-ish
    if current_domain in {None, "marketing"} and best_domain != current_domain and chartish:
        return best_domain

    return current_domain or "marketing"




def default_revenue_filters_state():
    return {
        entity: {
            "include": None,
            "exclude": []
        }
        for entity in REVENUE_DOMAIN_FILTER_CONFIG.keys()
    }


# =======================================
# FILTER-ONLY MESSAGE DETECTION (H1)
# =======================================

def is_revenue_chart_only_request(text: str) -> bool:
    """
    True only for *pure navigation* messages like:
      - 'revenue dashboard'
      - 'show revenue dashboard'
      - 'mrr trend'
      - 'monthly revenue chart'
    i.e. messages that do NOT try to change filters.
    """

    t = (text or "").lower().strip()

    # Any filter verbs or entity tokens → NOT chart-only
    if any(v in t for v in REVENUE_FILTER_VERBS):
        return False

    for token in REVENUE_ENTITY_TOKENS:
        if token in t:
            return False

    CHART_ONLY_PHRASES = {
        "revenue dashboard",
        "revenue chart",
        "monthly revenue",
        "mrr trend",
        "show revenue",
        "open revenue dashboard",
        "revenue overview",
    }

    CHART_VERBS = {"show", "open", "view", "see"}
    CHART_WORDS = {"dashboard", "chart", "trend", "overview", "report"}

    if any(p in t for p in CHART_ONLY_PHRASES):
        return True

    if any(v in t for v in CHART_VERBS) and any(w in t for w in CHART_WORDS):
        return True

    return False




def is_filter_only_message(user_text: str) -> bool:
    """
    H1 behavior:
    Returns True ONLY when the message is *strictly* about modifying filters
    and contains NO intent to view a chart, summary, overview, or dashboard.
    """

    if not user_text:
        return False

    t = user_text.lower().strip()

    # 1. If any chart keyword appears → NOT filter-only
    CHART_KEYWORDS = {
        "chart", "graph", "visual", "visualization",
        "dashboard", "overview", "summary", "report",
        "show me", "display", "open", "view",
        "trend", "trends", "time series",
    }

    for kw in CHART_KEYWORDS:
        if kw in t:
            return False

    # 2. Words that strongly indicate filter modification
    FILTER_VERBS = {
        "add", "remove", "exclude", "include",
        "reset", "clear", "filter", "filters",
        "only", "except"
    }

    FILTER_NOUNS = {
        "campaign", "campaigns",
        "channel", "channels"
    }

    if any(w in t for w in FILTER_VERBS):
        return True

    if any(w in t for w in FILTER_NOUNS):
        return True

    # 3. Mentions of valid campaign/channel values alone = filters
    for name in list(VALID_CAMPAIGNS) + list(VALID_CHANNELS):
        if name in t:
            return True

    return False



# =======================================
# CHART REQUEST DETECTION (H1)
# =======================================

def is_chart_request(user_text: str) -> bool:
    """
    H1 Hybrid behavior:
    True when the user clearly intends to view a chart / dashboard / summary.

    - If filter-only → False.
    - Requires clear chart intent: 'chart', 'dashboard', 'graph', 'trend', etc.
    - Or verbs like 'show', 'see', 'view' + metric words.
    - Plain 'lead score' / 'quality' / 'performance' alone will NOT switch charts.
    """

    if not user_text:
        return False

    t = normalized_text(user_text)

    # 1. Filter-only override
    if is_filter_only_message(t):
        return False

    # 2. Explicit override
    if extract_explicit_chart_id(t):
        return True

    # 3. Strong chart-ish words
    STRONG_CHART_WORDS = {
        "chart", "graph", "dashboard", "overview",
        "report", "visual", "visualization",
        "trend", "trends", "time series",
        "bubble", "scatter", "table",
        "kpi", "scorecard",
        "master chart", "master dashboard",
        "main chart", "main dashboard",
    }

    for w in STRONG_CHART_WORDS:
        if w in t:
            return True

    # 4. Verbs + metric words
    VERBS = {"show", "see", "display", "open", "view"}
    METRIC_WORDS = {
        "spend", "budget", "ad spend",
        "leads", "lead score",
        "campaign performance",
        "performance summary",
        "monthly", "funnel",
        "revenue", "mrr",
        "goals", "players"
    }

    if any(v in t for v in VERBS) and any(m in t for m in METRIC_WORDS):
        return True

    # 5. High-signal phrases that are almost certainly chart requests
    HIGH_SIGNAL_PHRASES = {
        "campaign performance chart",
        "campaign performance summary",
        "lead funnel chart",
        "lead funnel breakdown",
        "monthly spend trend",
        "monthly trend chart",
        "lead quality chart",
        "lead score chart",
        "efficiency chart",
    }

    for phrase in HIGH_SIGNAL_PHRASES:
        if phrase in t:
            return True

    return False


# =======================================
# GEMINI PROMPT (FILTER INTENT) — FIXED .format
# =======================================

GEMINI_INTENT_PROMPT = """
You are an intent parser for a marketing analytics assistant.
Convert the user message into structured JSON following *exactly* this schema:

{{
  "campaigns": {{
    "set": [],
    "add": [],
    "remove": []
  }},
  "channels": {{
    "set": [],
    "add": [],
    "remove": []
  }},
  "clear_all": false
}}

STRICT RULES:
- Do NOT add values not present in these lists:

  CAMPAIGNS_LIST = {campaigns_list}
  CHANNELS_LIST  = {channels_list}

- ALWAYS lowercase all returned values.

NEGATION RULES:
If user says phrases like:
- "no X"
- "no campaign X"
- "no channel X"
- "remove X"
- "remove campaign X"
- "remove channel X"
- "except X"
then use the "remove" list.

SET RULES:
If user says:
- "only X"
- "just X"
- "nothing but X"
then use the "set" list (NOT add).

ALL RULES (VERY IMPORTANT):
- If the user says phrases like:
    - "all"
    - "everything"
    - "show all"
    - "show everything"
    - "all filters"
    - "reset filters"
    - "clear filters"
    - "reset"
    - "clear all"
  then set "clear_all": true.

- If the user says "all campaigns" (or similar),
  set campaigns.set = CAMPAIGNS_LIST (do NOT touch channels).

- If the user says "all channels" (or similar),
  set channels.set = CHANNELS_LIST (do NOT touch campaigns).

- "all campaigns" must NOT set clear_all to true.
- "all channels" must NOT set clear_all to true.

SYNONYM RULES:
The user may use these synonyms. Map them to the canonical list values:

  - "fb" → "facebook"
  - "meta" → "facebook"
  - "ppc" → "paid_search"
  - "google" → "paid_search"
  - "google ads" → "paid_search"

CHANNEL ADD RULE:
If the user says things like:
- "add <channel>"
- "add <channel> back"
- "include <channel>"
- "show <channel>"
then ALWAYS put that channel into channels.add.

Never put channels into campaigns.set or campaigns.add.
Never ignore channel add requests.

CAMPAIGN ADD RULE:
If the user says things like:
- "add <campaign>"
- "add <campaign> back"
- "include <campaign>"
- "show <campaign>"
then ALWAYS put that campaign into campaigns.add.

Never put campaign names into channels.add or channels.set.
Never ignore an explicit add request for a campaign.

If the user uses any of these synonyms, return the mapped canonical value.

FINAL RULES:
- ALWAYS output valid JSON ONLY.
- NEVER include any explanation text outside the JSON.
- ALWAYS lowercase your values.
- NEVER hallucinate values not in the allowed lists.

User message:
\"\"\"{user_text}\"\"\"
"""

REVENUE_GEMINI_INTENT_PROMPT = """
You are an intent parser for a revenue analytics assistant.

Return ONLY valid JSON in this exact schema:

{{
  "clubs": {{ "set": [], "add": [], "remove": [] }},
  "product_categories": {{ "set": [], "add": [], "remove": [] }},
  "product_names": {{ "set": [], "add": [], "remove": [] }},
  "subscriptions": {{ "set": [], "add": [], "remove": [] }},
  "leagues": {{ "set": [], "add": [], "remove": [] }},
  "deal_stage_labels": {{ "set": [], "add": [], "remove": [] }},
  "channels": {{ "set": [], "add": [], "remove": [] }},
  "clear_all": false
}}

Rules:
- ONLY use values from the allowed lists provided below
- ALWAYS lowercase values
- NEVER hallucinate values

SET:
- "only X", "just X", "nothing but X" → set

ADD:
- "add X", "include X", "show X" → add

REMOVE:
- "remove X", "except X", "without X" → remove

CLEAR:
- "clear all", "reset filters" → clear_all=true

Allowed values (lowercase):

clubs = {clubs_list}
product_categories = {product_categories_list}
product_names = {product_names_list}
subscriptions = {subscriptions_list}
leagues = {leagues_list}
deal_stage_labels = {deal_stage_labels_list}
channels = {channels_list}

User message:
\"\"\"{user_text}\"\"\"
"""

def parse_sports_intent(user_message: str):
    """
    Gemini-based sports intent parser.

    We allow chart words + filters in the same sentence
    (e.g. "goals vs expected and only arsenal").
    """
    if not GEMINI_API_KEY:
        return None

    t = (user_message or "").lower().strip()
    if not t:
        return None

    prompt = SPORTS_GEMINI_INTENT_PROMPT.format(
        clubs_list=[c.lower() for c in SPORTS_CLUBS],
        seasons_list=[s.lower() for s in SPORTS_SEASONS],
        customer_types_list=[c.lower() for c in SPORTS_CUSTOMER_TYPES],
        subscription_tiers_list=[t.lower() for t in SPORTS_SUBSCRIPTION_TIERS],
        user_text=user_message,
    )

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
    except Exception as e:
        print("Gemini Sports ERROR →", e)
        return None

    raw_text = getattr(response, "text", "")
    if not raw_text:
        return None

    text_out = raw_text.strip()
    if text_out.startswith("```"):
        text_out = text_out.strip("`")
        if "\n" in text_out:
            text_out = text_out.split("\n", 1)[1]

    try:
        intent = json.loads(text_out)
    except Exception as e:
        print("Sports Gemini JSON parse error:", e)
        print("RAW TEXT:", text_out)
        return None

    return intent


SPORTS_GEMINI_INTENT_PROMPT = """
You are an intent parser for a sports performance analytics assistant.

Return ONLY valid JSON in this exact schema:

{{
  "clubs": {{ "set": [], "add": [], "remove": [] }},
  "seasons": {{ "set": [], "add": [], "remove": [] }},
  "customer_types": {{ "set": [], "add": [], "remove": [] }},
  "subscription_tiers": {{ "set": [], "add": [], "remove": [] }},
  "clear_all": false
}}

Rules:
- ONLY use values from the allowed lists provided below.
- ALWAYS lowercase values.
- NEVER hallucinate values not in the allowed lists.

SET:
- "only X", "just X", "nothing but X" → put X into the "set" list (replacing previous).

ADD:
- "add X", "include X", "show X" → put X into the "add" list (append).

REMOVE:
- "remove X", "except X", "without X", "no X" → put X into the "remove" list.

CLEAR:
- Phrases like "clear all", "reset filters", "remove all filters" → set "clear_all": true.

Allowed values (lowercase):

clubs = {clubs_list}
seasons = {seasons_list}
customer_types = {customer_types_list}
subscription_tiers = {subscription_tiers_list}

User message:
\"\"\"{user_text}\"\"\"
"""



# =======================================
# FILTER STATE HELPERS
# =======================================

def default_field_filter_state():
    return {
        "include": None,   # None = All
        "exclude": [],     # explicit exclusions
    }


def default_filters_state():
    return {
        "campaigns": default_field_filter_state(),
        "channels": default_field_filter_state(),
    }


def ensure_filters_in_session():
    domain = session.get("active_domain", "marketing")
    if "filters" not in session:
        session["filters"] = default_filters_state_for_domain(domain)



# =======================================
# LOOKER FIELD FILTER ENGINE
# =======================================

class LookerFieldFilter:
    """
    Represents filters for a single Looker field.
    Supports include/exclude & multi-clause AND/OR logic.
    """

    def __init__(self):
        self.clauses = []  # (logic_op, mode, values)

    def add_include(self, values, logic_op=""):
        values = [v for v in values if v]
        if not values:
            return
        self.clauses.append((logic_op, "include", values))

    def add_exclude(self, values, logic_op="AND"):
        values = [v for v in values if v]
        if not values:
            return
        self.clauses.append((logic_op, "exclude", values))

    def to_looker_string(self, looker_space):
        if not self.clauses:
            return None

        parts = []
        for logic_op, mode, values in self.clauses:
            prefix = f"{logic_op}{mode}" if logic_op else mode
            joined = looker_space.join(values)
            clause = f"{prefix}{looker_space}0{looker_space}IN{looker_space}{joined}"
            parts.append(clause)

        return LOOKER_CLAUSE_SEP.join(parts)


# =======================================
# GEMINI INTENT CLEANUP
# =======================================

def normalize_intent_structure(intent):
    if not isinstance(intent, dict):
        return None

    for section in ["campaigns", "channels"]:
        block = intent.get(section) or {}
        intent[section] = {
            "set": block.get("set") or [],
            "add": block.get("add") or [],
            "remove": block.get("remove") or [],
        }

    intent["clear_all"] = bool(intent.get("clear_all", False))
    return intent



def sanitize_intent(intent):
    intent = normalize_intent_structure(intent)
    if intent is None:
        return None

    for section in ["campaigns", "channels"]:
        cleaned = {"set": [], "add": [], "remove": []}

        for op in ["set", "add", "remove"]:
            for v in intent[section][op]:
                if not isinstance(v, str):
                    continue
                v_low = v.lower().strip()

                # synonyms
                if v_low in SYNONYMS:
                    v_low = SYNONYMS[v_low]

                if section == "campaigns":
                    if v_low in VALID_CAMPAIGNS:
                        cleaned[op].append(v_low)
                else:
                    if v_low in VALID_CHANNELS:
                        cleaned[op].append(v_low)

        intent[section] = cleaned

    return intent



def route_entities(intent):
    campaigns = intent["campaigns"]
    channels = intent["channels"]

    # move channels out of campaigns
    for op in ["set", "add", "remove"]:
        wrong = []
        for v in campaigns[op]:
            if v in VALID_CHANNELS:
                channels[op].append(v)
                wrong.append(v)
        for v in wrong:
            campaigns[op].remove(v)

    # move campaigns out of channels
    for op in ["set", "add", "remove"]:
        wrong = []
        for v in channels[op]:
            if v in VALID_CAMPAIGNS:
                campaigns[op].append(v)
                wrong.append(v)
        for v in wrong:
            channels[op].remove(v)

    return intent


def parse_marketing_intent(user_message: str):
    if not GEMINI_API_KEY:
        return None

    prompt = GEMINI_INTENT_PROMPT.format(
        campaigns_list=list(VALID_CAMPAIGNS),
        channels_list=list(VALID_CHANNELS),
        user_text=user_message,
    )

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
    except Exception as e:
        print("Gemini ERROR →", e)
        return None

    raw_text = getattr(response, "text", "")
    if not raw_text:
        return None

    text = raw_text.strip()

    if text.startswith("```"):
        text = text.strip("`")
        if "\n" in text:
            text = text.split("\n", 1)[1]

    try:
        intent = json.loads(text)
    except Exception as e:
        print("Gemini JSON parse error:", e)
        print("RAW TEXT:", text)
        return None

    intent = sanitize_intent(intent)
    if intent is None:
        return None

    intent = route_entities(intent)
    return intent



def parse_revenue_intent(user_message: str):
    """
    Revenue intent parser.

    IMPORTANT RULES:
    - Allow filters EVEN IF chart words exist (e.g. 'mrr trend and add aston villa').
    - Only skip parsing for *pure navigation* messages with NO filter signal:
        'revenue dashboard', 'show revenue dashboard', etc.
    - Prevent 'revenue dashboard' from being mis-read as product_categories='data dashboard'.
    """

    t = (user_message or "").lower().strip()

    # Does this message look like it wants to change filters?
    has_filter_verb = any(v in t for v in REVENUE_FILTER_VERBS)
    has_entity_token = any(token in t for token in REVENUE_ENTITY_TOKENS)
    has_filter_signal = has_filter_verb or has_entity_token

    # 1️⃣ Pure navigation → skip filters
    if not has_filter_signal and is_revenue_chart_only_request(t):
        return None

    # 2️⃣ Very generic 'dashboard' phrases → also skip filters
    BLOCKED_PHRASES = {
        "dashboard",
        "revenue dashboard",
        "financial dashboard",
        "subscription dashboard",
        "billing dashboard",
    }
    if not has_filter_signal and t in BLOCKED_PHRASES:
        return None

    if not GEMINI_API_KEY:
        return None

    prompt = REVENUE_GEMINI_INTENT_PROMPT.format(
        clubs_list=[v.lower() for v in REVENUE_DOMAIN_FILTER_CONFIG["clubs"]["values"]],
        product_categories_list=[
            v.lower() for v in REVENUE_DOMAIN_FILTER_CONFIG["product_categories"]["values"]
        ],
        product_names_list=[
            v.lower() for v in REVENUE_DOMAIN_FILTER_CONFIG["product_names"]["values"]
        ],
        subscriptions_list=[
            v.lower() for v in REVENUE_DOMAIN_FILTER_CONFIG["subscriptions"]["values"]
        ],
        leagues_list=[
            v.lower() for v in REVENUE_DOMAIN_FILTER_CONFIG["leagues"]["values"]
        ],
        deal_stage_labels_list=[
            v.lower() for v in REVENUE_DOMAIN_FILTER_CONFIG["deal_stage_labels"]["values"]
        ],
        channels_list=[
            v.lower() for v in REVENUE_DOMAIN_FILTER_CONFIG["channels"]["values"]
        ],
        user_text=user_message,
    )

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
    except Exception as e:
        print("Gemini Revenue ERROR →", e)
        return None

    raw_text = getattr(response, "text", "")
    if not raw_text:
        return None

    text = raw_text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if "\n" in text:
            text = text.split("\n", 1)[1]

    try:
        intent = json.loads(text)
    except Exception as e:
        print("Revenue Gemini JSON parse error:", e)
        print("RAW TEXT:", text)
        return None

    return intent

def normalize_revenue_intent(intent):
    """
    Ensures each entity block has: set, add, remove.
    Gemini sometimes returns boolean or None. We must correct it.
    """
    clean = {}

    for ent, blk in intent.items():

        # ❗ Fix: If Gemini returned bool/None/string → replace with empty dict
        if not isinstance(blk, dict):
            blk = {}

        clean[ent] = {
            "set": blk.get("set", []) or [],
            "add": blk.get("add", []) or [],
            "remove": blk.get("remove", []) or [],
        }

    # Ensure clear_all exists and is boolean
    clean["clear_all"] = bool(intent.get("clear_all", False))

    return clean


def sanitize_revenue_intent_values(intent: dict) -> dict:
    """
    Take a *normalized* revenue intent (every entity has set/add/remove lists)
    and:
      - apply revenue-specific synonyms
      - apply marketing-style channel synonyms
      - fuzzy match to the correct canonical keys
    Returns a new cleaned intent that is safe for apply_revenue_intent.
    """
    if not isinstance(intent, dict):
        return normalize_revenue_intent({})

    cleaned = {}

    for entity, meta in REVENUE_DOMAIN_FILTER_CONFIG.items():
        canon_map = meta["canon"]      # {lowercase_key: "Proper Label"}
        block = intent.get(entity) or {}
        new_block = {"set": [], "add": [], "remove": []}

        for op in ["set", "add", "remove"]:
            raw_vals = block.get(op) or []
            for v in raw_vals:
                v_low = (v or "").lower().strip()
                if not v_low:
                    continue

                # 1) Channel synonyms (reuse marketing SYNONYMS)
                if entity == "channels" and v_low in SYNONYMS:
                    v_low = SYNONYMS[v_low]

                # 2) Revenue synonyms
                if v_low in REVENUE_SYNONYMS:
                    v_low = REVENUE_SYNONYMS[v_low]

                # 3) Fuzzy match against this entity's canonical map
                matched_key = revenue_fuzzy_match_value(
                    v_low,
                    canon_map,
                    threshold=80,  # slightly looser like marketing
                )

                if matched_key and matched_key in canon_map:
                    if matched_key not in new_block[op]:
                        new_block[op].append(matched_key)

        cleaned[entity] = new_block

    # keep clear_all flag exactly as-is
    cleaned["clear_all"] = bool(intent.get("clear_all", False))
    return cleaned



def parse_intent_by_domain(user_message: str, domain: str):
    if domain == "marketing":
        return parse_marketing_intent(user_message)
    if domain == "revenue":
        return parse_revenue_intent(user_message)
    if domain == "sports":
        return parse_sports_intent(user_message)
    return None



def normalize_sports_intent(intent: dict) -> dict:
    """
    Ensure sports intent always has:
      { "set": [], "add": [], "remove": [] }
    for each entity + a boolean clear_all flag.
    """
    if not isinstance(intent, dict):
        return {
            "clubs": {"set": [], "add": [], "remove": []},
            "seasons": {"set": [], "add": [], "remove": []},
            "customer_types": {"set": [], "add": [], "remove": []},
            "subscription_tiers": {"set": [], "add": [], "remove": []},
            "clear_all": False,
        }

    def _normalize_block(block):
        if not isinstance(block, dict):
            return {"set": [], "add": [], "remove": []}
        return {
            "set": block.get("set") or [],
            "add": block.get("add") or [],
            "remove": block.get("remove") or [],
        }

    normalized = {
        "clubs": _normalize_block(intent.get("clubs")),
        "seasons": _normalize_block(intent.get("seasons")),
        "customer_types": _normalize_block(intent.get("customer_types")),
        "subscription_tiers": _normalize_block(intent.get("subscription_tiers")),
        "clear_all": bool(intent.get("clear_all", False)),
    }
    return normalized


def normalize_sports_filters_case(filters: dict) -> dict:
    """
    Ensure all sports filter values use proper-case labels
    from SPORTS_DOMAIN_FILTER_CONFIG[entity]["canon"].

    Example:
      include = ["liverpool"]  →  ["Liverpool"]
    """
    if not filters:
        return filters

    normalized = {}

    for entity, meta in SPORTS_DOMAIN_FILTER_CONFIG.items():
        canon = meta.get("canon", {})  # {lower: ProperLabel}
        state = filters.get(entity) or default_field_filter_state()

        include = state.get("include")
        exclude = state.get("exclude") or []

        # Normalize include
        if include:
            norm_include = []
            for v in include:
                key = (v or "").lower().strip()
                norm_include.append(canon.get(key, v))
        else:
            norm_include = None  # keep None = All

        # Normalize exclude
        norm_exclude = []
        for v in exclude:
            key = (v or "").lower().strip()
            norm_exclude.append(canon.get(key, v))

        normalized[entity] = {
            "include": norm_include,
            "exclude": norm_exclude,
        }

    return normalized


def apply_sports_intent(current_filters: dict, intent: dict) -> dict:
    """
    Apply sports Gemini intent to filters.

    NOTE: club is effectively single-select → include will be trimmed to 1.
    """
    # Global clear_all
    if intent.get("clear_all"):
        return default_sports_filters_state()

    filters = current_filters

    ENTITY_CONFIG = {
        "clubs": {
            "canon": SPORTS_CLUB_CANON,
            "single_select": True,
        },
        "seasons": {
            "canon": SPORTS_SEASON_CANON,
            "single_select": False,
        },
        "customer_types": {
            "canon": SPORTS_CUSTOMER_TYPE_CANON,
            "single_select": False,
        },
        "subscription_tiers": {
            "canon": SPORTS_TIER_CANON,
            "single_select": False,
        },
    }

    for entity, cfg in ENTITY_CONFIG.items():
        canon_map = cfg["canon"]
        single_select = cfg["single_select"]

        state = filters.get(entity) or default_field_filter_state()
        include = state.get("include")
        exclude = state.get("exclude") or []

        was_all = include is None and not exclude
        was_all_except = include is None and bool(exclude)

        block = intent.get(entity, {"set": [], "add": [], "remove": []})

        # SET
        if block["set"]:
            include_vals = [canon_map[v] for v in block["set"] if v in canon_map]
            if single_select and include_vals:
                include_vals = [include_vals[-1]]
            include = include_vals or None
            exclude = []

        # ADD
        if block["add"]:
            add_vals = [canon_map[v] for v in block["add"] if v in canon_map]
            if add_vals:
                for v in add_vals:
                    if v in exclude:
                        exclude.remove(v)

                if include is None:
                    include = []

                for v in add_vals:
                    if v not in include:
                        include.append(v)

                if single_select and include:
                    include = [include[-1]]  # last wins

        # REMOVE
        if block["remove"]:
            remove_vals = [canon_map[v] for v in block["remove"] if v in canon_map]

            if was_all:
                # All → All-except-X
                for v in remove_vals:
                    if v not in exclude:
                        exclude.append(v)

            elif include is not None:
                include = [v for v in include if v not in remove_vals]
                if not include:
                    include = None
                    exclude = []

            else:
                for v in remove_vals:
                    if v not in exclude:
                        exclude.append(v)

        state["include"] = include
        state["exclude"] = exclude
        filters[entity] = state

    return filters


# =======================================
# FALLBACK NLP (IF GEMINI FAILS)
# =======================================

def extract_filters_from_text(text: str):
    words = text.lower().split()
    found_campaigns = []
    found_channels = []

    for w in words:
        w_clean = w.strip(",.!?- ")

        if w_clean in STOP_WORDS:
            continue

        if w_clean in CAMPAIGN_CANON and CAMPAIGN_CANON[w_clean] not in found_campaigns:
            found_campaigns.append(CAMPAIGN_CANON[w_clean])

        if w_clean in CHANNEL_CANON and CHANNEL_CANON[w_clean] not in found_channels:
            found_channels.append(CHANNEL_CANON[w_clean])

        if w_clean in SYNONYMS:
            syn = SYNONYMS[w_clean]
            canonical = CHANNEL_CANON.get(syn.lower(), syn)
            if canonical not in found_channels:
                found_channels.append(canonical)

    # fuzzy
    for w in words:
        w_clean = w.strip(",.!?- ")

        if w_clean in STOP_WORDS:
            continue

        for ch in CHANNELS:
            score = fuzz.ratio(w_clean, ch.lower())
            dist = distance.Levenshtein.distance(w_clean, ch.lower())
            if score >= 80 and dist <= 2 and ch not in found_channels:
                found_channels.append(ch)

        for c in CAMPAIGNS:
            score = fuzz.ratio(w_clean, c.lower())
            dist = distance.Levenshtein.distance(w_clean, c.lower())
            if score >= 80 and dist <= 2 and c not in found_campaigns:
                found_campaigns.append(c)

    return found_campaigns, found_channels


def extract_revenue_filters_from_text(text: str) -> dict:
    """
    Lightweight fallback when Gemini is unavailable or returns unusable intent.

    Returns:
      {
        "clubs": {"liverpool", "aston villa"},
        "leagues": {"premier league"},
        ...
      }
    where each value is the canonical *key* (lowercase) from the entity's canon map.
    """
    words = (text or "").lower().split()
    results = {entity: set() for entity in REVENUE_DOMAIN_FILTER_CONFIG.keys()}

    for w in words:
        w_clean = w.strip(",.!?- ")
        if not w_clean or w_clean in STOP_WORDS:
            continue

        # apply synonyms first
        w_clean = REVENUE_SYNONYMS.get(w_clean, w_clean)

        for entity, meta in REVENUE_DOMAIN_FILTER_CONFIG.items():
            canon_map = meta["canon"]
            key = revenue_fuzzy_match_value(w_clean, canon_map, threshold=88)
            if key:
                results[entity].add(key)

    return results

def apply_revenue_fallback_nlp(filters: dict, user_text: str) -> dict:
    """
    Very simple fallback behavior:
    - Any recognized entities become INCLUDE-only (SET),
      clearing excludes for that entity.
    """
    extracted = extract_revenue_filters_from_text(user_text)
    new_filters = filters

    for entity, keys in extracted.items():
        if not keys:
            continue

        state = new_filters.get(entity) or default_field_filter_state()

        # Map canonical keys → proper labels for Looker
        canon_map = REVENUE_DOMAIN_FILTER_CONFIG[entity]["canon"]
        include_labels = [canon_map[k] for k in keys]

        state["include"] = include_labels
        state["exclude"] = []
        new_filters[entity] = state

    return new_filters

def revenue_nlp_fallback(user_text: str, current_filters: dict) -> dict:
    """
    Lightweight NLP fallback for revenue when Gemini:
      - returns None, OR
      - returns an 'empty' intent (no set/add/remove ops).

    GOALS:
    - Behave like Gemini-based intent:
        * 'add X' → add to existing include
        * 'only X' / 'just X' → SET
        * 'remove X' / 'without X' / 'except X' → REMOVE
    - Use fuzzy matching so misspellings like 'arsenl', 'chelsa' still work.
    - Never wipe out existing 'include' lists unless the user clearly asks
      for "only ..." / "just ...".
    """

    t = normalized_text(user_text)
    if not t:
        return current_filters

    # 1️⃣ Decide global "mode" for this message
    mode = "add"  # default: additive, like your marketing behavior

    REMOVE_TOKENS = ["remove", "without", "except", "no "]
    SET_TOKENS = ["only ", "just ", "nothing but "]

    if any(tok in t for tok in REMOVE_TOKENS):
        mode = "remove"
    if any(tok in t for tok in SET_TOKENS):
        mode = "set"

    # 2️⃣ Build candidate phrases (unigrams + bigrams + trigrams)
    raw_tokens = [w.strip(",.!?:;") for w in t.split() if w.strip(",.!?:;")]
    phrases = set()

    n_tokens = len(raw_tokens)
    for i in range(n_tokens):
        # unigrams
        phrases.add(raw_tokens[i])
        # bigrams
        if i + 1 < n_tokens:
            phrases.add(raw_tokens[i] + " " + raw_tokens[i + 1])
        # trigrams
        if i + 2 < n_tokens:
            phrases.add(raw_tokens[i] + " " + raw_tokens[i + 1] + " " + raw_tokens[i + 2])

    # 3️⃣ Try to map each phrase to a revenue entity via synonyms + fuzzy
    found = {entity: set() for entity in REVENUE_DOMAIN_FILTER_CONFIG.keys()}

    for phrase in phrases:
        if not phrase:
            continue

        # First apply explicit synonyms (man u → manchester united, etc.)
        norm_phrase = REVENUE_SYNONYMS.get(phrase, phrase).lower().strip()

        for entity, meta in REVENUE_DOMAIN_FILTER_CONFIG.items():
            canon_map = meta["canon"]  # {lowercase_name: "Proper Label"}

            # 3a) exact key match
            key = None
            if norm_phrase in canon_map:
                key = norm_phrase
            else:
                # 3b) fuzzy key match (handles 'arsenl', 'chelsa', etc.)
                key = revenue_fuzzy_match_value(norm_phrase, canon_map)

            if key:
                found[entity].add(key)

    # If we found nothing at all, just return filters unchanged
    if all(len(vals) == 0 for vals in found.values()):
        print(">> REVENUE NLP fallback: no entities detected")
        return current_filters

    # 4️⃣ Convert fuzzy hits → intent-like structure
    intent = {
        entity: {"set": [], "add": [], "remove": []}
        for entity in REVENUE_DOMAIN_FILTER_CONFIG.keys()
    }
    intent["clear_all"] = False  # fallback never does global clear

    for entity, keys in found.items():
        if not keys:
            continue

        key_list = list(keys)  # still lowercase canonical keys

        if mode == "set":
            intent[entity]["set"] = key_list
        elif mode == "remove":
            intent[entity]["remove"] = key_list
        else:
            # default: add
            intent[entity]["add"] = key_list

    print(">> REVENUE NLP INTENT (fallback):", intent)

    # 5️⃣ Reuse the main apply_revenue_intent so behavior is consistent
    return apply_revenue_intent(current_filters, intent)

def _apply_sports_value(filters, entity: str, value: str, op: str) -> None:
    """
    Apply a single (entity, value, op) to sports filters.
    op ∈ {"set", "add", "remove"}.
    """
    state = filters.get(entity) or default_field_filter_state()

    include = state.get("include")
    exclude = state.get("exclude") or []
    was_all = include is None and not exclude

    # SET
    if op == "set":
        include = [value]
        exclude = []

    # ADD
    elif op == "add":
        if value in exclude:
            exclude.remove(value)
        if include is None:
            include = []
        if value not in include:
            include.append(value)

    # REMOVE
    elif op == "remove":
        if was_all:
            if value not in exclude:
                exclude.append(value)
        elif include is not None:
            include = [v for v in include if v != value]
            if not include:
                include = None
                exclude = []
        else:
            if value not in exclude:
                exclude.append(value)

    # Single-select club: only 1 in include
    if entity == "clubs" and include:
        include = [include[-1]]

    state["include"] = include
    state["exclude"] = exclude
    filters[entity] = state


def sports_nlp_fallback(user_text: str, current_filters: dict) -> dict:
    """
    Very lightweight NLP for sports filters.
    Handles clubs (with typos and short forms), seasons, customer_types,
    and subscription_tiers.

    Examples:
      - 'arsenl' → Arsenal
      - 'only man u' → clubs = [Manchester United]
      - 'add lfc' → add Liverpool
      - '2023-24 and 2024-25' → seasons
      - 'paid freemium' → customer types
      - 'elite performance only' → subscription_tiers = [Elite+Performance]
      - 'all seasons' / 'clear seasons' → reset seasons to All
    """

    t = (user_text or "").lower().strip()
    if not t:
        return current_filters

    filters = current_filters or default_sports_filters_state()

    # ---- 0) Handle "all seasons"/"clear seasons" explicitly ----
    SEASON_CLEAR_PHRASES = {
        "all seasons",
        "show all seasons",
        "reset seasons",
        "clear seasons",
    }
    if any(p in t for p in SEASON_CLEAR_PHRASES):
        # Reset JUST seasons to All
        filters["seasons"] = default_field_filter_state()
        return filters

    # (You can add similar blocks later if you want "all clubs", etc.)
    # -------------------------------------------------------------

    # Decide operation
    if "only " in t or "just " in t:
        op = "set"
    elif any(v in t for v in ["remove", "exclude", "without", "except"]):
        op = "remove"
    elif any(v in t for v in ["add ", "include ", "plus "]):
        op = "add"
    else:
        # default to set (like 'arsenal', '2023-24')
        op = "set"

    found = {
        "clubs": set(),
        "seasons": set(),
        "customer_types": set(),
        "subscription_tiers": set(),
    }

    # ---- CLUBS: synonyms (man u, lfc, etc.) ----
    for phrase, label in SPORTS_CLUB_SYNONYMS.items():
        if phrase in t:
            found["clubs"].add(label)

    # ---- CLUBS: canonical substrings ----
    for label in SPORTS_CLUBS:
        key = label.lower()
        if key in t:
            found["clubs"].add(label)

    # ---- SEASONS: exact strings like '2023-24' ----
    for s in SPORTS_SEASONS:
        if s.lower() in t:
            found["seasons"].add(s)

    # ---- CUSTOMER TYPES ----
    if "paid" in t:
        found["customer_types"].add("paid")
    if "freemium" in t or "free tier" in t:
        found["customer_types"].add("freemium")

    # ---- SUBSCRIPTION TIERS: synonyms ----
    for phrase, label in SPORTS_SUB_TIER_SYNONYMS.items():
        if phrase in t:
            found["subscription_tiers"].add(label)
    for label in SPORTS_SUBSCRIPTION_TIERS:
        key = label.lower()
        if key in t:
            found["subscription_tiers"].add(label)

    # ---- Fuzzy tokens for clubs (arsenl, chelsa, etc.) ----
    tokens = re.split(r"[^a-z0-9\+\-]+", t)
    for token in tokens:
        if len(token) < 3:
            continue
        key = revenue_fuzzy_match_value(token, SPORTS_CLUB_CANON, threshold=80)
        if key:
            found["clubs"].add(SPORTS_CLUB_CANON[key])

    # Apply all found values
    any_found = False
    for entity, values in found.items():
        for v in values:
            any_found = True
            _apply_sports_value(filters, entity, v, op)

    if not any_found:
        # nothing recognized → leave filters untouched
        return filters

    return filters




# =======================================
# APPLY GEMINI INTENT → STRUCTURED FILTERS
# =======================================

def apply_gemini_intent(current_filters: dict, intent: dict) -> dict:
    """
    Applies Gemini intent to filter state (include/exclude),
    plus campaign↔channel dependency logic.
    """

    RAW_MAP = {
        "surge": ["email"],
        "wave": ["facebook"],
        "outreach": ["facebook"],
        "acquire": ["organic"],
        "grow": ["paid_search"],
        "kickoff": ["partnership"],
        "boost": ["partnership"],
        "expand": ["partnership"],
        "engage": ["partnership"],
        "signups": ["referral"],
    }

    CHANNEL_TO_CAMPS = {}
    for camp, chans in RAW_MAP.items():
        for ch in chans:
            CHANNEL_TO_CAMPS.setdefault(ch, []).append(camp)

    filters = current_filters

    # Global clear all
    if intent.get("clear_all"):
        return {
            "campaigns": default_field_filter_state(),
            "channels": default_field_filter_state(),
        }

    # 1) Process campaigns & channels independently
    for section, canon_map, all_values in [
        ("campaigns", CAMPAIGN_CANON, CAMPAIGNS),
        ("channels", CHANNEL_CANON, CHANNELS),
    ]:
        block = intent[section]
        state = filters.get(section) or default_field_filter_state()

        include = state.get("include")
        exclude = state.get("exclude") or []

        was_all = include is None and not exclude
        was_all_except = include is None and bool(exclude)

        # SET
        if block["set"]:
            include = [canon_map[v] for v in block["set"] if v in canon_map]
            exclude = []

        # ADD
        if block["add"]:
            add_vals = [canon_map[v] for v in block["add"] if v in canon_map]

            if add_vals:
                original_exclude = set(exclude)

                for v in add_vals:
                    if v in exclude:
                        exclude.remove(v)

                previously_excluded = [v for v in add_vals if v in original_exclude]
                new_vals = [v for v in add_vals if v not in original_exclude]

                if was_all_except and previously_excluded and not new_vals:
                    pass
                else:
                    if include is None:
                        include = []
                    for v in add_vals:
                        if v not in include:
                            include.append(v)

        # REMOVE
        if block["remove"]:
            remove_vals = [canon_map[v] for v in block["remove"] if v in canon_map]

            if was_all:
                # All → All-except-X
                for val in remove_vals:
                    if val not in exclude:
                        exclude.append(val)

            elif include is not None:
                include = [v for v in include if v not in remove_vals]
                if len(include) == 0:
                    include = None
                    exclude = []

            else:
                for val in remove_vals:
                    if val not in exclude:
                        exclude.append(val)

        state["include"] = include
        state["exclude"] = exclude
        filters[section] = state

    # 2) Dependency handling
    campaign_state = filters["campaigns"]
    channel_state = filters["channels"]

    added_campaigns = intent["campaigns"]["add"]
    set_campaigns = intent["campaigns"]["set"]
    affected_campaigns = set(added_campaigns + set_campaigns)

    # Campaign ADD → un-exclude required channels
    for camp in affected_campaigns:
        if camp in RAW_MAP:
            for ch in RAW_MAP[camp]:
                canon_ch = CHANNEL_CANON[ch]
                if canon_ch in channel_state["exclude"]:
                    channel_state["exclude"].remove(canon_ch)

    # Channel ADD → restore dependent campaigns when all required channels are OK
    explicit_added_channels = intent["channels"]["add"] + intent["channels"]["set"]

    for ch in explicit_added_channels:
        if ch in CHANNEL_TO_CAMPS:
            for camp in CHANNEL_TO_CAMPS[ch]:
                required = RAW_MAP[camp]
                other_ok = True
                for rc in required:
                    canon_rc = CHANNEL_CANON[rc]
                    if canon_rc != CHANNEL_CANON[ch] and canon_rc in channel_state["exclude"]:
                        other_ok = False
                        break

                if other_ok:
                    canon_camp = CAMPAIGN_CANON[camp]
                    if canon_camp in campaign_state["exclude"]:
                        campaign_state["exclude"].remove(canon_camp)
                    if campaign_state["include"] is not None:
                        if canon_camp not in campaign_state["include"]:
                            campaign_state["include"].append(canon_camp)

    # Channel REMOVE → drop related campaigns if all required channels excluded
    for ch in list(channel_state["exclude"]):
        if ch.lower() not in CHANNEL_TO_CAMPS:
            continue
        for camp in CHANNEL_TO_CAMPS[ch.lower()]:
            required = RAW_MAP[camp]
            if all(CHANNEL_CANON[rc] in channel_state["exclude"] for rc in required):
                canon_camp = CAMPAIGN_CANON[camp]
                if campaign_state["include"] and canon_camp in campaign_state["include"]:
                    campaign_state["include"].remove(canon_camp)
                if campaign_state["include"] is None and canon_camp not in campaign_state["exclude"]:
                    campaign_state["exclude"].append(canon_camp)

    # Campaign REMOVE → auto-exclude orphan channels (unless explicitly added)
    explicit_channel_changes = {
        CHANNEL_CANON[v]
        for v in intent["channels"]["add"] + intent["channels"]["set"]
        if v in CHANNEL_CANON
    }

    if campaign_state["include"] is not None:
        remaining = {c.lower() for c in campaign_state["include"]}
    else:
        excluded = {c.lower() for c in campaign_state["exclude"]}
        remaining = {c.lower() for c in RAW_MAP.keys() if c not in excluded}

    for ch in CHANNELS:
        if ch in explicit_channel_changes:
            continue
        camps_using_ch = CHANNEL_TO_CAMPS.get(ch, [])
        if not any(c in remaining for c in camps_using_ch):
            if channel_state["include"] and ch in channel_state["include"]:
                channel_state["include"].remove(ch)
            if ch not in channel_state["exclude"]:
                channel_state["exclude"].append(ch)

    return filters


def apply_revenue_intent(current_filters: dict, intent: dict) -> dict:
    """
    Applies revenue Gemini intent to filter state.
    Mirrors marketing include/exclude semantics.
    """

    # ✅ FIX: correct clear_all handling
    if intent.get("clear_all"):
        return default_revenue_filters_state()

    filters = current_filters

    for entity, meta in REVENUE_DOMAIN_FILTER_CONFIG.items():
        canon_map = meta["canon"]
        state = filters.get(entity) or default_field_filter_state()

        include = state.get("include")
        exclude = state.get("exclude") or []

        was_all = include is None and not exclude
        was_all_except = include is None and bool(exclude)

        block = intent.get(entity, {"set": [], "add": [], "remove": []})

        # SET
        if block["set"]:
            include = [canon_map[v] for v in block["set"] if v in canon_map]
            exclude = []

        # ADD
        if block["add"]:
            add_vals = [canon_map[v] for v in block["add"] if v in canon_map]

            if add_vals:
                for v in add_vals:
                    if v in exclude:
                        exclude.remove(v)

                if include is None:
                    include = []
                for v in add_vals:
                    if v not in include:
                        include.append(v)

        # REMOVE
        if block["remove"]:
            remove_vals = [canon_map[v] for v in block["remove"] if v in canon_map]

            if was_all:
                for v in remove_vals:
                    if v not in exclude:
                        exclude.append(v)

            elif include is not None:
                include = [v for v in include if v not in remove_vals]
                if not include:
                    include = None
                    exclude = []

            else:
                for v in remove_vals:
                    if v not in exclude:
                        exclude.append(v)

        state["include"] = include
        state["exclude"] = exclude
        filters[entity] = state

    return filters


# =======================================
# MASTER RESOLVER (FILTERS ONLY, MARKETING)
# =======================================

def resolve_user_message(user_message: str, filters: dict) -> dict:
    txt = normalized_text(user_message)

    # Global all → clear both
    if is_global_all_command(txt):
        filters["campaigns"] = default_field_filter_state()
        filters["channels"] = default_field_filter_state()
        return filters

    # All campaigns only
    if is_all_campaigns_command(txt):
        filters["campaigns"] = default_field_filter_state()
        return filters

    # All channels only
    if is_all_channels_command(txt):
        filters["channels"] = default_field_filter_state()
        return filters

    # Gemini
    intent = parse_intent_by_domain(user_message, "marketing")
    if intent:
        print(">> GEMINI INTENT:", intent)
        return apply_gemini_intent(filters, intent)

    # Fallback NLP
    print(">> Gemini failed → using fallback NLP")
    new_campaigns, new_channels = extract_filters_from_text(user_message)

    if new_campaigns:
        filters["campaigns"]["include"] = new_campaigns
        filters["campaigns"]["exclude"] = []

    if new_channels:
        filters["channels"]["include"] = new_channels
        filters["channels"]["exclude"] = []

    return filters


# =======================================
# LOOKER PARAM HELPERS
# =======================================

def build_looker_filter(field_state: dict):
    if not field_state:
        return None

    include = field_state.get("include")
    exclude = field_state.get("exclude") or []

    lf = LookerFieldFilter()

    if include:
        lf.add_include(include, logic_op="")

    if exclude:
        logic_op = "AND" if lf.clauses else ""
        lf.add_exclude(exclude, logic_op=logic_op)

    if not lf.clauses:
        return None

    return lf.to_looker_string(LOOKER_SPACE)


def build_looker_params(filters: dict) -> dict:
    params = {}

    campaigns_state = filters.get("campaigns")
    channels_state = filters.get("channels")

    if campaigns_state:
        s = build_looker_filter(campaigns_state)
        if s:
            params["df3"] = s

    if channels_state:
        s = build_looker_filter(channels_state)
        if s:
            params["df4"] = s

    return params

def build_marketing_looker_params(filters):
    params = {}

    campaigns_state = filters.get("campaigns")
    channels_state = filters.get("channels")

    if campaigns_state:
        s = build_looker_filter(campaigns_state)
        if s:
            params["df3"] = s

    if channels_state:
        s = build_looker_filter(channels_state)
        if s:
            params["df4"] = s

    return params

def build_revenue_looker_params(filters):
    params = {}

    for entity, meta in REVENUE_DOMAIN_FILTER_CONFIG.items():
        state = filters.get(entity)
        if not state:
            continue

        s = build_looker_filter(state)
        if s:
            params[meta["df"]] = s

    return params


def build_sports_looker_params(filters):
    """
    Build Looker params for sports using SPORTS_DOMAIN_FILTER_CONFIG.
    Note: clubs dimension is single-select in the report, so we enforce
    at most one value in include for 'clubs'.
    """
    params = {}

    for entity, meta in SPORTS_DOMAIN_FILTER_CONFIG.items():
        state = filters.get(entity)
        if not state:
            continue

        effective_state = state

        # Enforce single-select for clubs
        if entity == "clubs" and state.get("include"):
            effective_state = {
                "include": state["include"][:1],   # first club only
                "exclude": state.get("exclude") or [],
            }

        s = build_looker_filter(effective_state)
        if s:
            params[meta["df"]] = s

    return params



def build_looker_params_for_domain(filters, domain):
    if domain == "marketing":
        return build_marketing_looker_params(filters)

    if domain == "revenue":
        return build_revenue_looker_params(filters)

    if domain == "sports":
        return build_sports_looker_params(filters)

    return {}   # future domains


def ensure_domain_filters():
    session.setdefault("filters", {})

    if "marketing" not in session["filters"]:
        session["filters"]["marketing"] = default_filters_state()

    if "revenue" not in session["filters"]:
        session["filters"]["revenue"] = default_revenue_filters_state()

    if "sports" not in session["filters"]:
        session["filters"]["sports"] = default_sports_filters_state()





# =======================================
# DEFAULT CHART PER DOMAIN
# =======================================

def get_default_chart_for_domain(active_domain: str) -> str:
    """
    Return a reasonable default chart for the given domain.
    - If a master chart id is configured and present, use that.
    - Else: first chart belonging to that domain.
    - Fallback: first chart in catalog.
    """

    domain = (active_domain or "marketing").lower()

    # 1) Configured master id
    master_id = DOMAIN_MASTER_CHART.get(domain)
    if master_id and master_id in CHART_CATALOG:
        return master_id

    # 2) Any chart for that domain
    for cid, meta in CHART_CATALOG.items():
        if (meta.get("project_name") or "").lower() == domain:
            return cid

    # 3) Any chart at all
    for cid in CHART_CATALOG.keys():
        return cid

    return None


# =======================================
# CONCEPT RESOLUTION (Option A core)
# =======================================

def resolve_chart_concept(user_text: str, domain: str) -> str | None:
    """
    Map user text → high-level chart 'concept', then CHART_CONCEPT_MAP[domain]
    decides the exact chart id.

    This is deterministic and domain-aware.
    """

    t = (user_text or "").lower().strip()
    d = (domain or "marketing").lower()

    if d != "marketing":
        # For now we only define concept rules for marketing.
        return None

    # ---------- MASTER / MAIN DASHBOARD ----------
    MASTER_PHRASES = {
        "main chart",
        "main dashboard",
        "master chart",
        "master dashboard",
        "home dashboard",
        "home chart",
        "overview",
        "full dashboard",
        "all charts",
        "everything view",
    }
    if any(p in t for p in MASTER_PHRASES):
        return "master"

    # ---------- MONTHLY / TREND ----------
    # More specific ones first
    MONTHLY_TREND_PATTERNS = [
        "monthly trend",
        "month trend",
        "trend by month",
        "month over month",
        "mom trend",
        "monthly chart",
        "trend monthly",
        "monthly spend trend",
        "trend over months",
        "trend over time",
        "time series",
        "trend chart",
    ]
    if any(p in t for p in MONTHLY_TREND_PATTERNS):
        return "trend"
    # Generic "trend" alone (without monthly) still maps to trend
    if "trend" in t or "trends" in t:
        return "trend"

    # ---------- PERFORMANCE ----------
    if (
        "campaign performance" in t
        or "campaign summary" in t
        or ("performance" in t and "campaign" in t)
        or ("performance" in t and "summary" in t)
        or "perf summary" in t
    ):
        return "performance"
    if "performance" in t and "chart" in t:
        return "performance"

    # ---------- FUNNEL ----------
    if "funnel" in t or "pipeline" in t:
        return "funnel"

    # ---------- SCORE ----------
    if "lead score" in t or "score chart" in t or "lead score chart" in t:
        return "score"
    # If user explicitly says "lead score" with some chart-ish word
    if "lead score" in t and ("chart" in t or "graph" in t or "dashboard" in t):
        return "score"

    # ---------- QUALITY ----------
    if "lead quality" in t or "quality chart" in t:
        return "quality"
    if "quality" in t and ("chart" in t or "graph" in t or "dashboard" in t):
        return "quality"

    # ---------- EFFICIENCY ----------
    if (
        "efficiency" in t
        or "efficient" in t
        or "roi" in t
        or "return" in t
        or "cac" in t
        or "cost per acquisition" in t
    ):
        return "efficiency"

    # ---------- SPEND ----------
    if (
        "spend" in t
        or "spends" in t
        or "ad spend" in t
        or "budget" in t
        or "money spent" in t
        or "cost" in t
    ):
        return "spend"

    return None

def resolve_revenue_chart_concept(user_text: str) -> str | None:
    """
    Map user text → high-level revenue concept key used in REVENUE_CHART_CONCEPT_MAP.

    Returns one of:
      'master',
      'monthly_revenue_trend', 'mrr_trend',
      'revenue_by_club', 'top_clubs',
      'revenue_by_product', 'revenue_by_category',
      'product_mix_by_category', 'subscription_mix',
      'subscription_penetration', 'subscription_composition'
    """

    t = (user_text or "").lower().strip()
    if not t:
        return None

    # ----- MASTER / OVERVIEW -----
    MASTER_PHRASES = {
        "revenue dashboard",
        "financial dashboard",
        "subscription dashboard",
        "billing dashboard",
        "main dashboard",
        "master dashboard",
        "master chart",
        "overview",
        "summary view",
    }
    if any(p in t for p in MASTER_PHRASES):
        return "master"

    # ----- MRR vs Monthly Revenue -----
    if "mrr" in t or "recurring revenue" in t:
        return "mrr_trend"

    if (
        "monthly revenue" in t
        or ("monthly" in t and "revenue" in t)
        or "revenue trend" in t
        or "revenue over time" in t
        or "revenue time series" in t
    ):
        return "monthly_revenue_trend"

    if "trend" in t or "trends" in t:
        # generic 'trend' for revenue → monthly revenue trend
        return "monthly_revenue_trend"

    # ----- CLUB VIEWS -----
    # e.g. "top 5 spend", "top revenue clubs", "top 5 clubs by revenue"
    if "top" in t and ("spend" in t or "revenue" in t) and "club" in t:
        return "top_clubs"
    if "top 5 spend" in t or "top five spend" in t:
        return "top_clubs"

    if (
        "revenue by club" in t
        or "by club" in t
        or "club revenue" in t
    ):
        return "revenue_by_club"

    # ----- PRODUCT VIEWS -----
    if "revenue by product" in t or "by product" in t:
        return "revenue_by_product"

    if "by category" in t or "product category" in t:
        return "revenue_by_category"

    # ----- MIX VIEWS -----
    if "product mix" in t or "revenue mix" in t:
        return "product_mix_by_category"

    if "subscription mix" in t or "subscription revenue mix" in t:
        return "subscription_mix"

    # ----- SUBSCRIPTION KPIs -----
    if "subscription penetration" in t:
        return "subscription_penetration"

    if (
        "subscription composition" in t
        or "subs composition" in t
        or "subscription breakdown" in t
    ):
        return "subscription_composition"

    return None

def resolve_sports_chart_concept(user_text: str) -> str | None:
    """
    Map sports user text → high-level sports concept key used in SPORTS_CHART_CONCEPT_MAP.
    """

    t = (user_text or "").lower().strip()
    if not t:
        return None

    # MASTER dashboard
    MASTER_PHRASES = {
        "elite intelligence",
        "elite intelligence dashboard",
        "sports dashboard",
        "main dashboard",
        "master dashboard",
        "master chart",
        "overview",
        "summary view",
    }
    if any(p in t for p in MASTER_PHRASES):
        return "master"

    # SHOTS ON TARGET TREND
    if "shots on target" in t or "shot on target" in t or "shots trend" in t:
        return "shots_trend"

    # GOALS TREND
    if "goals trend" in t or "goals over seasons" in t or "total goals" in t:
        return "goals_trend"

    # GOALS vs xG (expected goals)
    if (
        "goals vs xg" in t
        or "goals versus xg" in t
        or "goals vs expected" in t
        or "goals versus expected" in t
        or "goals vs expected goals" in t
        or "expected goals" in t and "goals" in t
    ):
        return "goals_vs_xg"

    # GOALS CONVERSION %
    if (
        "conversion" in t
        or "conversion %" in t
        or "goal conversion" in t
        or "goals conversion" in t
    ):
        return "goals_conversion"

    # CONCEDED vs xGC
    if (
        "conceded" in t and "xgc" in t
    ) or (
        "conceded" in t and "expected goals against" in t
    ):
        return "conceded_vs_xgc"

    # DEFENSIVE DISCIPLINE
    if "defensive discipline" in t or "cards" in t or "fouls" in t:
        return "defensive_discipline"

    # DEFENSIVE SEASONAL PROFILE
    if "defensive seasonal profile" in t or "defensive profile" in t:
        return "defensive_profile"

    return None


def pick_best_revenue_chart(user_text: str, catalog: dict) -> str | None:
    """
    Revenue Option-A chart selector.

    Layers:
      0) Explicit chart override: "chart=rev_xxx"
      1) Deterministic concept mapping (resolve_revenue_chart_concept + REVENUE_CHART_CONCEPT_MAP)
      2) Metadata fuzzy scoring restricted to project_name='revenue'
      3) Fallback: REVENUE_MASTER_CHART / default revenue chart
    """

    t = (user_text or "").lower().strip()

    # 0️⃣ Explicit chart override
    explicit = extract_explicit_chart_id(t)
    if explicit and explicit in catalog:
        print(f"🔧 Revenue explicit chart override → {explicit}")
        return explicit

    # 1️⃣ Concept mapping
    concept = resolve_revenue_chart_concept(user_text)
    if concept:
        chart_id = REVENUE_CHART_CONCEPT_MAP.get(concept)
        if chart_id and chart_id in catalog:
            print(f"🎯 Revenue concept '{concept}' → chart_id={chart_id}")
            return chart_id
        else:
            print(f"⚠ Revenue concept '{concept}' has no valid chart in catalog")

    # 2️⃣ Generic dashboard words → master
    DASH_WORDS = {
        "dashboard",
        "master dashboard",
        "master chart",
        "overview",
        "summary",
        "main page",
    }
    if any(w in t for w in DASH_WORDS):
        if REVENUE_MASTER_CHART in catalog:
            print(f"📌 Revenue dashboard phrase → {REVENUE_MASTER_CHART}")
            return REVENUE_MASTER_CHART
        default_id = get_default_chart_for_domain("revenue")
        if default_id:
            print(f"📌 Revenue dashboard phrase → default chart {default_id}")
            return default_id

    # 3️⃣ Fuzzy fallback using chart_catalog metadata (project_name='revenue')
    candidates = {}
    for cid, meta in catalog.items():
        proj = (meta.get("project_name") or "").lower()
        if proj == "revenue" or not proj:
            candidates[cid] = meta

    if not candidates:
        candidates = catalog

    BEST_THRESHOLD = 50
    STRONG_THRESHOLD = 75

    WEIGHT_TITLE = 1.5
    WEIGHT_DESC = 1.0
    WEIGHT_TAGS = 2.0

    # Simple revenue vocabulary – boosts tag matches
    DOMAIN_KEYWORDS = {
        "trend": ["trend", "trends", "time series", "monthly", "over time"],
        "club": ["club", "clubs"],
        "product": ["product", "category"],
        "subscription": ["subscription", "subscriptions", "subscribers"],
        "mix": ["mix", "composition", "breakdown"],
        "mrr": ["mrr", "recurring"],
        "revenue": ["revenue", "sales"],
    }

    matched_categories = set()
    for cat, variants in DOMAIN_KEYWORDS.items():
        if any(v in t for v in variants):
            matched_categories.add(cat)

    best_id = None
    best_score = 0

    for cid, meta in candidates.items():
        title = (meta.get("chart_title") or "").lower()
        desc = (meta.get("description") or "").lower()
        tags = [x.lower() for x in (meta.get("tags") or [])]

        title_score = fuzz.partial_ratio(t, title)
        desc_score = fuzz.partial_ratio(t, desc)
        tag_score = fuzz.partial_ratio(t, " ".join(tags))

        score = (
            title_score * WEIGHT_TITLE +
            desc_score * WEIGHT_DESC +
            tag_score * WEIGHT_TAGS
        )

        # Boost charts whose tags line up with what user said
        for cat in matched_categories:
            if cat in tags:
                score += 20

        if score >= STRONG_THRESHOLD:
            print(f"🏆 Revenue strong fuzzy match → {cid} (score={score})")
            return cid

        if score > best_score:
            best_score = score
            best_id = cid

    # 4️⃣ Final safety fallback
    if not best_id or best_score < BEST_THRESHOLD:
        if REVENUE_MASTER_CHART in catalog:
            print(
                f"⚠ Revenue fuzzy low (best={best_score}) → "
                f"fallback to master {REVENUE_MASTER_CHART}"
            )
            return REVENUE_MASTER_CHART

        default_id = get_default_chart_for_domain("revenue")
        if default_id:
            print(
                f"⚠ Revenue fuzzy low (best={best_score}) → "
                f"fallback to default revenue chart {default_id}"
            )
            return default_id

        if catalog:
            any_chart = list(catalog.keys())[0]
            print(
                f"⚠ Revenue fuzzy low and no defaults → "
                f"fallback to first chart {any_chart}"
            )
            return any_chart

        return None

    print(f"✅ Revenue fuzzy-selected chart → {best_id} (score={best_score})")
    return best_id


# =======================================
# CHART SELECTION ENGINE (DOMAIN-AWARE, HYBRID)
# =======================================

def pick_best_chart(user_text: str, catalog: dict, domain: str = "marketing") -> str | None:
    """
    Stable, 3-layer chart selector (Hybrid / Option A):

      Layer 1: Deterministic concept mapping (resolve_chart_concept + CHART_CONCEPT_MAP)
      Layer 2: Metadata-driven fuzzy scoring, restricted to domain
      Layer 3: Safe fallback to <domain> master chart

    NOTE: This function assumes is_chart_request(user_text) is already True.
    """

    t = (user_text or "").lower().strip()
    domain = (domain or "marketing").lower()

    # ---------------------------------------
    # 0. Explicit chart override
    # ---------------------------------------
    explicit = extract_explicit_chart_id(t)
    if explicit and explicit in catalog:
        print(f"🔧 Explicit chart override → {explicit}")
        return explicit

    # ---------------------------------------
    # 1. Concept → chart id mapping (Option A core)
    # ---------------------------------------
    concept = resolve_chart_concept(user_text, domain)
    if concept:
        domain_map = CHART_CONCEPT_MAP.get(domain, {})
        chart_id = domain_map.get(concept)
        if chart_id and chart_id in catalog:
            print(f"🎯 Concept '{concept}' in domain '{domain}' → chart_id={chart_id}")
            return chart_id
        else:
            print(f"⚠ Concept '{concept}' mapped but chart missing for domain '{domain}'")

    # ---------------------------------------
    # 2. Master dashboard intent (generic)
    # ---------------------------------------
    DASH_KEYWORDS = {
        "dashboard",
        "main dashboard",
        "master dashboard",
        "master chart",
        "main chart",
        "home dashboard",
        "home chart",
        "main page",
    }
    if any(k in t for k in DASH_KEYWORDS):
        default_id = get_default_chart_for_domain(domain)
        if default_id:
            print(f"📌 Master/dashboard phrase → default chart {default_id}")
            return default_id

    # ---------------------------------------
    # 3. Fuzzy fallback by metadata
    # ---------------------------------------

    # Candidate charts restricted to current domain
    candidates = {}
    for cid, meta in catalog.items():
        proj = (meta.get("project_name") or "").lower()
        if proj == domain or not proj:
            candidates[cid] = meta

    # If no charts matched the domain, fall back to all
    if not candidates:
        candidates = catalog

    # Scoring parameters
    BEST_THRESHOLD = 50          # require decent confidence
    STRONG_MATCH_THRESHOLD = 75  # instant lock

    WEIGHT_TITLE = 1.5
    WEIGHT_DESC = 1.0
    WEIGHT_TAGS = 2.0

    # Domain vocabulary used to boost tag matches a bit
    DOMAIN_KEYWORDS = {
        "funnel": ["funnel", "conversion", "lead funnel"],
        "summary": ["summary", "performance summary", "top", "best"],
        "trend": ["trend", "trends", "time series", "monthly", "over time"],
        "leads": ["lead", "leads", "signups"],
        "spend": ["spend", "ad spend", "budget", "cost"],
        "cac": ["cac", "cost per acquisition"],
        "quality": ["quality", "lead quality"],
        "score": ["score", "lead score"],
        "efficiency": ["efficiency", "roi", "return"],
    }

    matched_categories = set()
    for cat, variants in DOMAIN_KEYWORDS.items():
        if any(v in t for v in variants):
            matched_categories.add(cat)

    best_chart_id = None
    best_score = 0

    for cid, meta in candidates.items():
        title = (meta.get("chart_title") or "").lower()
        desc = (meta.get("description") or "").lower()
        tags = [x.lower() for x in (meta.get("tags") or [])]

        title_score = fuzz.partial_ratio(t, title)
        desc_score = fuzz.partial_ratio(t, desc)
        tag_score = fuzz.partial_ratio(t, " ".join(tags))

        score = (
            title_score * WEIGHT_TITLE +
            desc_score * WEIGHT_DESC +
            tag_score * WEIGHT_TAGS
        )

        # Boost when domain keyword matches chart tags
        for cat in matched_categories:
            if cat in tags:
                score += 20

        # Strong immediate match
        if score >= STRONG_MATCH_THRESHOLD:
            print(f"🏆 Strong fuzzy match → {cid} (score={score})")
            return cid

        if score > best_score:
            best_score = score
            best_chart_id = cid

    # ---------------------------------------
    # 4. Final safety fallback
    # ---------------------------------------
    if not best_chart_id or best_score < BEST_THRESHOLD:
        default_id = get_default_chart_for_domain(domain)
        if default_id:
            print(
                f"⚠ Low fuzzy score (best={best_score}) → "
                f"fallback to default chart {default_id}"
            )
            return default_id

        # last resort
        if catalog:
            any_chart = list(catalog.keys())[0]
            print(
                f"⚠ No good candidate and no domain default → "
                f"fallback to first chart {any_chart}"
            )
            return any_chart
        return None

    print(f"✅ Fuzzy-selected chart → {best_chart_id} (score={best_score})")
    return best_chart_id


def handle_revenue_all_commands(user_text: str, filters: dict):
    """
    Handles phrases like:
      - 'all clubs'
      - 'all product categories'
      - 'all subscriptions'
    and resets ONLY that one entity to All (include=None, exclude=[]).
    Returns (new_filters, handled_bool).
    """
    t = normalized_text(user_text)
    handled = False

    for entity, phrases in REVENUE_ALL_ENTITY_PHRASES.items():
        if t in phrases:
            filters[entity] = default_field_filter_state()
            handled = True

    return filters, handled
  


# =======================================
# HTML PAGE TEMPLATE
# =======================================

PAGE_HTML = """
<html>
<head>
<style>
body {
    font-family: Arial;
    background:#f0f2f5;
    margin:0;
    padding:0;
}

/* MAIN CHAT AREA (scrollable) */
#chat-container {
    max-width: 900px;
    margin: auto;
    padding: 20px;
    padding-bottom: 10px;
    height: calc(100vh - 260px);
    overflow-y: auto;
    box-sizing: border-box;
}

.bubble-user {
    background:#007bff;
    color:white;
    padding:12px;
    border-radius:12px;
    margin:10px 0;
    width:fit-content;
    max-width:80%;
    margin-left:auto;
}

.bubble-bot {
    background:#e5e5ea;
    padding:12px;
    border-radius:12px;
    margin:10px 0;
    width:fit-content;
    max-width:80%;
}

/* CHART BELOW CHAT */
#chart-wrapper {
    max-width: 900px;
    margin: 0 auto;
    padding: 5px 20px 120px 20px;
}

iframe {
    width:100%;
    height:900px;
    border:none;
    margin-top:15px;
    border-radius:6px;
    background:white;
}

/* INPUT BOX FIXED TO BOTTOM */
#askbox {
    position:fixed;
    bottom:0;
    left:0;
    right:0;
    background:white;
    padding:15px;
    border-top:1px solid #ccc;
}

input[type=text] {
    width:80%;
    padding:12px;
    border:1px solid #ccc;
    border-radius:8px;
    font-size:16px;
}

button {
    width:15%;
    padding:12px;
    margin-left:10px;
    background:#007bff;
    color:white;
    border:none;
    border-radius:8px;
    cursor:pointer;
}
</style>
</head>

<body>

<div id="chat-container">
    <h2>Analytics Chat Assistant</h2>

    {% for msg in messages %}
      <div class="bubble-{{ msg.type }}">{{ msg.text }}</div>
    {% endfor %}
</div>

<div id="chart-wrapper">
    {% if chart_url %}
      <iframe src="{{ chart_url }}"></iframe>
    {% endif %}
</div>

<div id="askbox">
  <form action="/resolve" method="get">
    <input type="text" name="q" placeholder="Ask something…" autofocus>
    <button>Ask</button>
  </form>
</div>

<script>
function scrollChatToBottom() {
    const chat = document.querySelector("#chat-container");
    if (!chat) return;

    chat.scrollTo({
        top: chat.scrollHeight,
        behavior: "smooth"
    });
}

document.addEventListener("DOMContentLoaded", () => {
    requestAnimationFrame(() => {
        setTimeout(scrollChatToBottom, 50);
    });
});
</script>

</body>
</html>
"""


# =======================================
# SUMMARY HELPERS FOR UI
# =======================================

def summarize_field_filters(field_state: dict, all_values) -> str:
    if not field_state:
        return "All"

    include = field_state.get("include")
    exclude = field_state.get("exclude") or []

    if include is None and not exclude:
        return "All"

    parts = []

    if include:
        if set(include) == set(all_values) and not exclude:
            return "All"
        parts.append(", ".join(include))

    if exclude:
        parts.append("except " + ", ".join(exclude))

    if not parts:
        return "All"
    return " ; ".join(parts)


def summarize_revenue_filters(filters: dict) -> str:
    """
    Compact, readable revenue summary for the chat bubble.
    Shows only entities that are not 'All'.
    """
    if not filters:
        return "Revenue: All"

    parts = []

    for entity, meta in REVENUE_DOMAIN_FILTER_CONFIG.items():
        state = filters.get(entity) or {}
        include = state.get("include")
        exclude = state.get("exclude") or []

        if include is None and not exclude:
            continue  # All → skip

        label = entity.replace("_", " ")

        if include:
            parts.append(f"{label}={','.join(include)}")
        if exclude:
            parts.append(f"{label}≠{','.join(exclude)}")

    return "Revenue: All" if not parts else " | ".join(parts)

# =======================================
# ROUTES
# =======================================

@app.route("/")
def index():
    session.setdefault("history", [])
    ensure_filters_in_session()
    # default domain
    session.setdefault("active_domain", "marketing")

    return render_template_string(
        PAGE_HTML,
        messages=session["history"],
        chart_url=session.get("last_chart"),
    )


@app.route("/resolve")
def resolve():
    q = request.args.get("q", "").strip()
    text = q.lower().strip()

    session.setdefault("history", [])
    session.setdefault("active_domain", "marketing")

    # ------------------------------------------
    # Ensure per-domain filter stores exist
    # ------------------------------------------
    ensure_domain_filters()

    # Log user message
    session["history"].append({"type": "user", "text": q})

    # ------------------------------------------
    # 1️⃣ DOMAIN SWITCHING
    # ------------------------------------------
    current_domain = session["active_domain"]
    new_domain = detect_domain_switch(q, current_domain)
    session["active_domain"] = new_domain

    print(f"\n🌐 Active domain: {new_domain}")
    print(f"🗣️ User said: {q}")

    # ------------------------------------------
    # 2️⃣ APPLY FILTERS (DOMAIN-SPECIFIC)
    # ------------------------------------------
    filters = session["filters"][new_domain]

    if new_domain == "marketing":
        filters = resolve_user_message(q, filters)

    elif new_domain == "revenue":
        if is_global_all_command(text):
            filters = default_revenue_filters_state()
        else:
            filters, handled_all = handle_revenue_all_commands(q, filters)
            if not handled_all:
                intent = parse_revenue_intent(q)
                if intent:
                    intent = normalize_revenue_intent(intent)
                    has_ops = intent.get("clear_all", False)
                    if not has_ops:
                        for e in REVENUE_DOMAIN_FILTER_CONFIG:
                            blk = intent.get(e, {})
                            if blk.get("set") or blk.get("add") or blk.get("remove"):
                                has_ops = True
                                break
                    filters = (
                        apply_revenue_intent(filters, intent)
                        if has_ops
                        else revenue_nlp_fallback(q, filters)
                    )
                else:
                    filters = revenue_nlp_fallback(q, filters)

    elif new_domain == "sports":
        if is_global_all_command(text):
            filters = default_sports_filters_state()
        else:
            intent = parse_sports_intent(q)
            if intent:
                intent = normalize_sports_intent(intent)
                has_ops = intent.get("clear_all", False)
                if not has_ops:
                    for e in SPORTS_DOMAIN_FILTER_CONFIG:
                        blk = intent.get(e, {})
                        if blk.get("set") or blk.get("add") or blk.get("remove"):
                            has_ops = True
                            break
                filters = (
                    apply_sports_intent(filters, intent)
                    if has_ops
                    else sports_nlp_fallback(q, filters)
                )
            else:
                filters = sports_nlp_fallback(q, filters)

    session["filters"][new_domain] = filters

    # ------------------------------------------
    # 3️⃣ CHART SELECTION (STABLE)
    # ------------------------------------------
    skip_chart_navigation = should_skip_chart_navigation(q)

    previous_chart_url = session.get("last_chart")

    # Always ensure a chart exists
    chart_url = previous_chart_url or url_for(
        "chart",
        chart_id=get_default_chart_for_domain(new_domain),
    )

    if not skip_chart_navigation:

        if new_domain != current_domain:
            chart_url = url_for(
                "chart",
                chart_id=get_default_chart_for_domain(new_domain),
            )

        else:
            if new_domain == "revenue":
                if is_revenue_chart_only_request(text) or is_revenue_chart_request(text):
                    if "top" in text and "spend" in text:
                        chart_id = "rev_top_5_clubs_by_spend"
                    else:
                        chart_id = pick_revenue_chart(q)
                    chart_url = url_for(
                        "chart",
                        chart_id=chart_id or get_default_chart_for_domain("revenue"),
                    )

            elif new_domain == "sports":
                if is_sports_chart_request(q):
                    chart_id = pick_sports_chart(q)
                    chart_url = url_for(
                        "chart",
                        chart_id=chart_id or get_default_chart_for_domain("sports"),
                    )

            else:  # marketing
                if is_chart_request(q):
                    chart_id = pick_best_chart(q, CHART_CATALOG, domain="marketing")
                    chart_url = url_for(
                        "chart",
                        chart_id=chart_id or get_default_chart_for_domain("marketing"),
                    )

    session["last_chart"] = chart_url

    # ------------------------------------------
    # 4️⃣ RAG RESPONSE (SINGLE ENTRY POINT)
    # ------------------------------------------
    rag_text = None

    if skip_chart_navigation:
        chart_id = None
        if chart_url and "chart_id=" in chart_url:
            chart_id = chart_url.split("chart_id=")[-1]

        rag_text = run_rag(
            domain=new_domain,
            chart_id=chart_id,
            question=q,
        )

    # ------------------------------------------
    # 5️⃣ SUMMARY BUBBLE
    # ------------------------------------------
    if new_domain == "marketing":
        summary = (
            f"Campaigns: {summarize_field_filters(filters['campaigns'], CAMPAIGNS)} | "
            f"Channels: {summarize_field_filters(filters['channels'], CHANNELS)}"
        )

    elif new_domain == "revenue":
        summary = summarize_revenue_filters(filters)

    elif new_domain == "sports":
        parts = []
        for entity in SPORTS_DOMAIN_FILTER_CONFIG:
            state = filters.get(entity) or {}
            inc = state.get("include")
            exc = state.get("exclude") or []
            if inc:
                parts.append(f"{entity}={','.join(inc)}")
            if exc:
                parts.append(f"{entity}≠{','.join(exc)}")
        summary = "Sports: All" if not parts else " | ".join(parts)

    else:
        summary = "Unknown domain"

    session["history"].append({
        "type": "bot",
        "text": f"[Domain: {new_domain}] {summary}"
    })

    # ------------------------------------------
    # 6️⃣ RAG RESPONSE (ADDITIVE)
    # ------------------------------------------
    if rag_text:
        session["history"].append({
            "type": "bot",
            "text": f"📊 Diagnostic insight:\n{rag_text}"
        })

    return redirect(url_for("index"))


@app.route("/chart")
def chart():
    chart_id = request.args.get("chart_id", "")

    if chart_id not in CHART_CATALOG:
        return f"Unknown chart_id: {chart_id}", 400

    chart_meta = CHART_CATALOG[chart_id]
    report_id = chart_meta["looker_report_id"]
    page_id = chart_meta["looker_page_id"]

    domain = session.get("active_domain", "marketing")
    filters = session["filters"].get(domain, {})

    # 🔹 Domain-specific Looker params
    if domain == "marketing":
        params_dict = build_marketing_looker_params(filters)
    elif domain == "revenue":
        params_dict = build_revenue_looker_params(filters)
    elif domain == "sports":
        params_dict = build_sports_looker_params(filters)
    else:
        params_dict = {}

    # 🔎 DEBUG
    try:
        print("\n================ LOOKER DEBUG ================")
        print("Domain:", domain)
        print("Chart ID:", chart_id)
        print("Filters dict:")
        print(json.dumps(filters, indent=2))
        print("\nParams dict (pre-encoding):")
        print(json.dumps(params_dict, indent=2))
    except Exception:
        print("LOOKER DEBUG (raw):", domain, chart_id, filters, params_dict)

    if params_dict:
        params_str = urllib.parse.quote(json.dumps(params_dict))
        embed_url = (
            f"https://lookerstudio.google.com/embed/reporting/"
            f"{report_id}/page/{page_id}?params={params_str}"
        )
    else:
        embed_url = (
            f"https://lookerstudio.google.com/embed/reporting/"
            f"{report_id}/page/{page_id}"
        )

    print("Embed URL:", embed_url)
    print("=============================================\n")

    return render_template_string(
        f"""
        <html><body style="margin:0;">
          <iframe width="100%" height="900" src="{embed_url}" frameborder="0"></iframe>
        </body></html>
        """
    )




@app.route("/reset_session")
def reset_session():
    session.clear()
    return "Session cleared."


# =======================================
# MAIN
# =======================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)