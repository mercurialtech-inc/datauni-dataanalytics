INSERT INTO `metadata.rag_charts`
(chart_id, domain, primary_metrics, questions_answered, when_to_use, common_followups, caveats, created_at, updated_at)
VALUES
(
  "mktg_total_spend",
  "marketing",
  ["total_spend"],
  [
    "Where are we spending the most by campaign?",
    "Which campaigns are driving overall spend?"
  ],
  "Use to understand budget allocation and identify major spend drivers before evaluating performance outcomes.",
  ["mktg_campaign_perf_summary", "mktg_efficiency", "mktg_monthly_spend_leads"],
  "High spend is not bad by itself. Always pair with leads and CAC; also confirm time period/pacing when comparing campaigns.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "mktg_lead_quality",
  "marketing",
  ["lead_quality", "leads", "avg_lead_score"],
  [
    "Which campaigns generate higher-quality leads?",
    "Is lead quality improving or degrading by campaign/channel?"
  ],
  "Use when volume looks good but downstream outcomes or CAC are worsening; quality often explains the gap.",
  ["mktg_avg_lead_score", "mktg_campaign_perf_summary", "mktg_lead_funnel"],
  "Quality buckets depend on scoring rules/model. If definitions change, comparisons across time may not be apples-to-apples.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "mktg_efficiency",
  "marketing",
  ["efficiency", "total_spend", "leads", "cac"],
  [
    "Which campaigns are most efficient at converting spend into outcomes?",
    "How do campaigns compare on spend vs leads vs CAC?"
  ],
  "Use to compare campaigns and guide budget reallocation. Best for relative decisions (shift budget) rather than absolute reporting.",
  ["mktg_campaign_perf_summary", "mktg_monthly_spend_leads", "mktg_lead_quality"],
  "Bubble charts can mislead if one campaign has tiny volume. Validate with trends and minimum volume thresholds.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "mktg_campaign_perf_summary",
  "marketing",
  ["total_spend", "leads", "cac", "funnel_conversion"],
  [
    "What is overall campaign performance across spend, leads, and CAC?",
    "Which campaigns are doing well on both volume and efficiency?"
  ],
  "Use as your default performance overview for executives. It’s the quickest way to spot winners/losers.",
  ["mktg_efficiency", "mktg_lead_funnel", "mktg_lead_quality"],
  "If CAC is approximate (uses qualified leads or conversions), explain the denominator clearly when presenting.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "mktg_master_dashboard",
  "marketing",
  ["total_spend", "leads", "cac", "lead_quality", "avg_lead_score", "funnel_conversion", "monthly_trend"],
  [
    "Give me the full marketing overview dashboard.",
    "How is marketing doing end-to-end?"
  ],
  "Use for broad stakeholder reviews and when you don’t yet know which question you’re answering.",
  ["mktg_campaign_perf_summary", "mktg_monthly_spend_leads", "mktg_efficiency"],
  "Master dashboards are summary-heavy; for deep dives, switch to the specific chart that matches the question.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "mktg_lead_funnel",
  "marketing",
  ["funnel_conversion", "leads", "lead_quality"],
  [
    "Where are leads dropping off in the funnel?",
    "Is the bottleneck at early-stage or late-stage conversion?"
  ],
  "Use when leads are stable but downstream metrics (customers/revenue) are not improving. Helps locate the funnel bottleneck.",
  ["mktg_lead_quality", "mktg_campaign_perf_summary"],
  "Funnel stage definitions can change. Confirm stage mapping and attribution windows before comparing across months.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "mktg_monthly_spend_leads",
  "marketing",
  ["monthly_trend", "total_spend", "leads"],
  [
    "How are spend and leads trending month over month?",
    "Did something change recently that impacted performance?"
  ],
  "Use to detect seasonality, pacing, and step-changes from campaign launches/pauses or tracking changes.",
  ["mktg_efficiency", "mktg_campaign_perf_summary"],
  "Trend shifts can come from measurement changes (tracking/attribution). Always sanity check tracking releases or pipeline changes.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "mktg_avg_lead_score",
  "marketing",
  ["avg_lead_score", "lead_quality"],
  [
    "Are we attracting higher-intent leads over time?",
    "Which campaigns have the best lead scores?"
  ],
  "Use when you want a single numeric proxy for lead intent/quality and to compare campaigns quickly.",
  ["mktg_lead_quality", "mktg_lead_funnel"],
  "Average can hide distribution shifts (e.g., more low and more high). Pair with quality breakdown for clarity.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
);

INSERT INTO `metadata.rag_charts`
(chart_id, domain, primary_metrics, questions_answered, when_to_use, common_followups, caveats, created_at, updated_at)
VALUES
(
  "mktg_kpi_total_leads",
  "marketing",
  ["leads"],
  [
    "How many total leads did marketing generate?",
    "Is lead volume increasing or decreasing overall?"
  ],
  "Use as a headline indicator of marketing volume across all campaigns and channels within the current filter context.",
  [
    "mktg_monthly_spend_leads",
    "mktg_campaign_perf_summary",
    "mktg_lead_quality"
  ],
  "This is an aggregate metric. Changes may be driven by seasonality, pacing, or tracking updates. Always validate trends and lead quality before drawing conclusions.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
);


INSERT INTO `metadata.rag_charts`
(chart_id, domain, primary_metrics, questions_answered, when_to_use, common_followups, caveats, created_at, updated_at)
VALUES
(
  "mktg_kpi_total_spend",
  "marketing",
  ["total_spend"],
  [
    "What is our total marketing spend?",
    "Is spend increasing or decreasing overall?"
  ],
  "Use as a high-level indicator of marketing investment across campaigns and channels in the selected period.",
  [
    "mktg_total_spend",
    "mktg_monthly_spend_leads",
    "mktg_campaign_perf_summary"
  ],
  "Spend alone does not indicate performance. Always interpret alongside leads, CAC, and efficiency metrics.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
);

INSERT INTO `metadata.rag_charts`
(chart_id, domain, primary_metrics, questions_answered, when_to_use, common_followups, caveats, created_at, updated_at)
VALUES
(
  "mktg_kpi_overall_cac",
  "marketing",
  ["cac"],
  [
    "What is our overall customer acquisition cost?",
    "Is customer acquisition becoming more or less expensive?"
  ],
  "Use as a headline efficiency indicator summarizing the cost to acquire outcomes across all marketing activity.",
  [
    "mktg_efficiency",
    "mktg_lead_quality",
    "mktg_campaign_perf_summary",
    "mktg_lead_funnel"
  ],
  "Overall CAC can hide campaign-level variation and denominator effects. Validate changes with efficiency, quality, and funnel charts before taking action.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
);

INSERT INTO `metadata.rag_charts`
(chart_id, domain, primary_metrics, questions_answered, when_to_use, common_followups, caveats, created_at, updated_at)
VALUES
(
  "mktg_kpi_avg_lead_score",
  "marketing",
  ["avg_lead_score"],
  [
    "What is the average lead quality across marketing?",
    "Are we attracting higher- or lower-intent leads overall?"
  ],
  "Use as a quick proxy for overall lead intent and quality across campaigns and channels.",
  [
    "mktg_lead_quality",
    "mktg_avg_lead_score",
    "mktg_lead_funnel"
  ],
  "Averages can mask distribution changes. Pair with lead quality breakdowns to understand whether gains are broad-based or concentrated.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
);

INSERT INTO `metadata.rag_charts`
(chart_id, domain, primary_metrics, questions_answered, when_to_use, common_followups, caveats, created_at, updated_at)
VALUES

-- =========================
-- TOTAL REVENUE KPI
-- =========================
(
  "rev_kpi_total_revenue",
  "revenue",
  ["revenue"],
  [
    "What is our total revenue?",
    "Is revenue increasing or decreasing overall?"
  ],
  "Use as a headline indicator of realized revenue across all orders and subscriptions in the current filter context.",
  [
    "rev_monthly_revenue_trend",
    "rev_revenue_by_product",
    "rev_revenue_by_club"
  ],
  "This is an aggregate KPI. Revenue concentration, timing, or mix shifts may be hidden. Always validate with trends and mix breakdowns.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- TOTAL MRR KPI
-- =========================
(
  "rev_kpi_total_mrr",
  "revenue",
  ["mrr"],
  [
    "What is our total monthly recurring revenue?",
    "Is recurring revenue growing or declining?"
  ],
  "Use as a snapshot of recurring revenue stability across active subscriptions.",
  [
    "rev_monthly_mrr_trend",
    "rev_subscription_revenue_mix",
    "rev_subscription_penetration_by_club"
  ],
  "Short-term changes can be driven by timing or one-off adjustments. Confirm with trend and churn context.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- TOTAL ARR KPI
-- =========================
(
  "rev_kpi_total_arr",
  "revenue",
  ["arr"],
  [
    "What is our total annual recurring revenue?",
    "How durable is our recurring revenue base?"
  ],
  "Use as a long-term view of recurring revenue health, smoothing short-term MRR volatility.",
  [
    "rev_monthly_mrr_trend",
    "rev_subscription_revenue_mix"
  ],
  "ARR assumes current MRR is sustainable. Always validate against churn and renewal risk.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- TOTAL DEALS KPI
-- =========================
(
  "rev_kpi_total_deals",
  "revenue",
  ["total_deals"],
  [
    "How many deals are we closing?",
    "Is sales activity increasing or slowing?"
  ],
  "Use as a proxy for sales motion intensity and pipeline throughput.",
  [
    "rev_revenue_by_club",
    "rev_deal_stage_distribution"
  ],
  "Deal volume does not imply deal quality or revenue impact. Pair with win rate and deal value.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- TOTAL ORDERS KPI
-- =========================
(
  "rev_kpi_total_orders",
  "revenue",
  ["total_orders"],
  [
    "How many customer orders were completed?",
    "Is transaction volume changing?"
  ],
  "Use as an indicator of customer demand and transaction frequency.",
  [
    "rev_revenue_by_product",
    "rev_monthly_revenue_trend"
  ],
  "High order counts do not necessarily mean high revenue. Always validate revenue per order.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- DEAL WIN RATE KPI
-- =========================
(
  "rev_kpi_deal_win_rate",
  "revenue",
  ["deal_win_rate"],
  [
    "What percentage of deals are we winning?",
    "Is sales effectiveness improving or declining?"
  ],
  "Use as a quality indicator for the sales funnel and pricing effectiveness.",
  [
    "rev_subscription_penetration_by_club",
    "rev_revenue_by_club"
  ],
  "Win rate should be interpreted alongside deal size and pipeline mix.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
);


INSERT INTO `metadata.rag_charts`
(chart_id, domain, primary_metrics, questions_answered, when_to_use, common_followups, caveats, created_at, updated_at)
VALUES

-- =========================
-- REVENUE BY CLUB
-- =========================
(
  "rev_revenue_by_club",
  "revenue",
  ["revenue"],
  [
    "Which clubs contribute the most revenue?",
    "How concentrated is revenue across clubs?"
  ],
  "Use to understand revenue concentration and dependency on top clubs.",
  [
    "rev_monthly_revenue_trend",
    "rev_revenue_by_product"
  ],
  "High concentration increases risk. Validate stability over time.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- TOP 5 CLUBS BY SPEND
-- =========================
(
  "rev_top_5_clubs_by_spend",
  "revenue",
  ["revenue"],
  [
    "Which clubs are spending the most?",
    "Are a few clubs driving the majority of spend?"
  ],
  "Use to identify top revenue-driving clubs and assess concentration risk.",
  [
    "rev_revenue_by_club"
  ],
  "Top spenders may skew averages. Always assess long-tail contribution.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- REVENUE BY PRODUCT
-- =========================
(
  "rev_revenue_by_product",
  "revenue",
  ["revenue", "product_mix"],
  [
    "Which products generate the most revenue?",
    "How diversified is revenue across products?"
  ],
  "Use to understand product contribution and identify growth or dependency risks.",
  [
    "rev_product_revenue_mix_by_category",
    "rev_monthly_revenue_trend"
  ],
  "Product mix shifts can hide volume changes.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- REVENUE BY PRODUCT CATEGORY
-- =========================
(
  "rev_revenue_by_product_category",
  "revenue",
  ["product_mix"],
  [
    "How is revenue split across product categories?",
    "Are certain categories becoming more dominant?"
  ],
  "Use to assess portfolio balance at a category level.",
  [
    "rev_revenue_by_product"
  ],
  "Category-level views can mask individual product performance.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- SUBSCRIPTION PENETRATION BY CLUB
-- =========================
(
  "rev_subscription_penetration_by_club",
  "revenue",
  ["subscription_penetration"],
  [
    "Which clubs have adopted subscriptions?",
    "Where are expansion opportunities?"
  ],
  "Use to understand adoption breadth and identify upsell opportunities.",
  [
    "rev_subscription_revenue_mix",
    "rev_revenue_by_club"
  ],
  "Penetration does not indicate revenue depth.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- REVENUE MASTER DASHBOARD
-- =========================
(
  "rev_master_dashboard",
  "revenue",
  ["revenue", "mrr", "arr", "product_mix", "subscription_mix"],
  [
    "Give me a full revenue overview.",
    "How is the business performing end-to-end?"
  ],
  "Use as the executive entry point before drilling into specific revenue questions.",
  [
    "rev_monthly_revenue_trend",
    "rev_monthly_mrr_trend"
  ],
  "Summary dashboards hide underlying drivers. Always drill down.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- PRODUCT REVENUE MIX BY CATEGORY
-- =========================
(
  "rev_product_revenue_mix_by_category",
  "revenue",
  ["product_mix"],
  [
    "How is revenue distributed across product categories?",
    "Are we shifting toward higher- or lower-value categories?"
  ],
  "Use to explain revenue changes driven by portfolio mix.",
  [
    "rev_revenue_by_product"
  ],
  "Mix views do not show volume changes.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- SUBSCRIPTION REVENUE MIX
-- =========================
(
  "rev_subscription_revenue_mix",
  "revenue",
  ["subscription_mix", "mrr"],
  [
    "How is subscription revenue distributed across tiers?",
    "Are customers upgrading or downgrading?"
  ],
  "Use to explain MRR movement and pricing effectiveness.",
  [
    "rev_monthly_mrr_trend",
    "rev_subscription_penetration_by_club"
  ],
  "Tier definition changes will break comparability.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- MONTHLY REVENUE TREND
-- =========================
(
  "rev_monthly_revenue_trend",
  "revenue",
  ["monthly_revenue_trend", "revenue"],
  [
    "How is revenue trending month over month?",
    "Did something recently change?"
  ],
  "Use to detect growth, seasonality, and step-changes.",
  [
    "rev_revenue_by_product",
    "rev_revenue_by_club"
  ],
  "Trends may reflect timing effects rather than structural change.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- MONTHLY MRR TREND
-- =========================
(
  "rev_monthly_mrr_trend",
  "revenue",
  ["mrr"],
  [
    "How is recurring revenue trending?",
    "Is subscription revenue stable?"
  ],
  "Use to evaluate recurring revenue durability.",
  [
    "rev_subscription_revenue_mix",
    "rev_subscription_penetration_by_club"
  ],
  "One-off adjustments can distort short-term trends.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- SUBSCRIPTION PRODUCT COMPOSITION
-- =========================
(
  "rev_subscription_product_composition",
  "revenue",
  ["subscription_mix", "product_mix"],
  [
    "Which products are included in subscriptions?",
    "How bundled are subscription offerings?"
  ],
  "Use to understand subscription structure and bundling strategy.",
  [
    "rev_subscription_revenue_mix"
  ],
  "Composition does not indicate usage or value realization.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
);

INSERT INTO `metadata.rag_charts`
(chart_id, domain, primary_metrics, questions_answered, when_to_use, common_followups, caveats, created_at, updated_at)
VALUES

(
  "sprt_kpi_matches_played",
  "sports",
  ["matches_played"],
  [
    "How many matches were played?",
    "What is the sample size for performance metrics?"
  ],
  "Use as contextual information to interpret per-match rates.",
  ["sprt_total_goals_trend"],
  "Not a performance metric by itself.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

(
  "sprt_kpi_total_goals",
  "sports",
  ["total_goals"],
  [
    "How many goals did the team score?",
    "Is scoring improving or declining?"
  ],
  "Use as the headline attacking outcome metric.",
  ["sprt_goals_vs_xg", "sprt_goal_conversion_pct"],
  "Goals can be noisy short-term; validate with xG.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

(
  "sprt_kpi_total_xg",
  "sports",
  ["xg"],
  [
    "How many expected goals were created?",
    "Is chance creation strong?"
  ],
  "Use to evaluate chance quality independently of finishing.",
  ["sprt_goals_vs_xg"],
  "xG is model-dependent.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

(
  "sprt_kpi_avg_possession",
  "sports",
  ["avg_possession"],
  [
    "How much possession does the team have?",
    "Is the team controlling matches?"
  ],
  "Use to understand tactical style and control.",
  ["sprt_shots_on_target_trend"],
  "High possession does not guarantee goals.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

(
  "sprt_kpi_total_shots",
  "sports",
  ["total_shots"],
  [
    "How many shots were taken?",
    "Is attacking pressure increasing?"
  ],
  "Use to measure attacking volume.",
  ["sprt_goal_conversion_pct", "sprt_goals_vs_xg"],
  "Shot volume without quality can mislead.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
);

INSERT INTO `metadata.rag_charts`
(chart_id, domain, primary_metrics, questions_answered, when_to_use, common_followups, caveats, created_at, updated_at)
VALUES

(
  "sprt_goal_conversion_pct",
  "sports",
  ["goal_conversion_pct"],
  [
    "How efficient is finishing?",
    "Are goals aligned with shot volume?"
  ],
  "Use to evaluate finishing efficiency.",
  ["sprt_goals_vs_xg"],
  "High conversion may regress without xG support.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

(
  "sprt_goals_vs_xg",
  "sports",
  ["total_goals", "xg"],
  [
    "Are goals sustainable?",
    "Is the team over- or under-performing xG?"
  ],
  "Use to separate finishing variance from chance quality.",
  ["sprt_goal_conversion_pct"],
  "Short samples can exaggerate gaps.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

(
  "sprt_shots_on_target_trend",
  "sports",
  ["shots_on_target", "seasonal_trend"],
  [
    "Is attacking pressure increasing over seasons?"
  ],
  "Use to track attacking consistency.",
  ["sprt_total_goals_trend"],
  "Does not reflect chance quality.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

(
  "sprt_total_goals_trend",
  "sports",
  ["total_goals", "seasonal_trend"],
  [
    "How has goal scoring evolved?"
  ],
  "Use to assess attacking improvement over time.",
  ["sprt_goals_vs_xg"],
  "Contextualize with xG.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

(
  "sprt_defensive_discipline",
  "sports",
  ["defensive_discipline"],
  [
    "Is discipline impacting defense?"
  ],
  "Use to understand defensive risk factors.",
  ["sprt_conceded_vs_xgc"],
  "Cards/fouls vary by referee.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

(
  "sprt_conceded_vs_xgc",
  "sports",
  ["goals_conceded", "xgc"],
  [
    "Is defense over- or under-performing?"
  ],
  "Use to assess defensive sustainability.",
  ["sprt_defensive_seasonal_profile"],
  "Goalkeeper variance matters.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

(
  "sprt_defensive_seasonal_profile",
  "sports",
  ["defensive_discipline", "xgc"],
  [
    "How has defensive profile changed by season?"
  ],
  "Use for long-term defensive assessment.",
  ["sprt_conceded_vs_xgc"],
  "Radar charts are comparative, not absolute.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

(
  "sprt_master_dashboard",
  "sports",
  ["total_goals", "xg", "goal_conversion_pct", "defensive_discipline", "seasonal_trend"],
  [
    "Give me a full sports performance overview."
  ],
  "Use as the executive entry point.",
  ["sprt_goals_vs_xg", "sprt_defensive_seasonal_profile"],
  "Always drill down for context.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
);


