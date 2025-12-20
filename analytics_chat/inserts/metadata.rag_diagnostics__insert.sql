INSERT INTO `metadata.rag_diagnostics`
(domain, metric_key, change_type, likely_causes, checks_to_perform, exec_friendly_summary, created_at, updated_at)
VALUES
(
  "marketing",
  "total_spend",
  "increase",
  [
    "Budget increase or new campaign launch",
    "Bid/auction dynamics raising CPM/CPC",
    "Shift toward higher-cost channels (e.g., paid_search)",
    "Pacing changes (spend front-loaded in the month)"
  ],
  ["mktg_total_spend", "mktg_monthly_spend_leads", "mktg_campaign_perf_summary"],
  "Higher spend typically reflects either a planned budget increase, a campaign/channel mix shift toward more expensive inventory, or auction pressure. Validate whether leads and CAC moved in the same direction to determine if the additional spend was efficient.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "marketing",
  "total_spend",
  "decrease",
  [
    "Budget cuts or campaign pause",
    "Pacing caps or delivery constraints",
    "Shift to lower-cost channels or organic/referral growth",
    "Tracking/reporting changes excluding some spend"
  ],
  ["mktg_total_spend", "mktg_monthly_spend_leads"],
  "Lower spend can be intentional (budget reduction) or operational (delivery constraints). Confirm if lead volume held steady; if so, efficiency may have improved or the channel mix shifted.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "marketing",
  "leads",
  "decrease",
  [
    "Traffic decline or reduced impressions",
    "Landing page conversion rate drop",
    "Audience saturation or creative fatigue",
    "Form friction increased / offer weakened",
    "Attribution or tracking changes (pixel/UTM issues)"
  ],
  ["mktg_monthly_spend_leads", "mktg_campaign_perf_summary", "mktg_lead_quality"],
  "A lead drop is commonly driven by reduced traffic, lower conversion, or measurement changes. If spend is flat or up while leads fall, investigate conversion and tracking first, then channel/campaign effectiveness.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "marketing",
  "lead_quality",
  "decrease",
  [
    "Channel mix shifted toward lower-intent sources (e.g., broad targeting)",
    "Creative/message mismatch attracting low-intent users",
    "Lead scoring model changed (thresholds or features)",
    "Sales follow-up delayed causing fewer leads to qualify"
  ],
  ["mktg_lead_quality", "mktg_avg_lead_score", "mktg_lead_funnel"],
  "A decline in lead quality often explains why CAC worsens even when lead volume looks healthy. First validate whether scoring/definitions changed; then review channel and campaign mix for intent alignment.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "marketing",
  "cac",
  "increase",
  [
    "Spend increased faster than conversions/qualified outcomes",
    "Lead quality declined (more low-intent leads)",
    "Shift to higher-cost channels or saturated audiences",
    "Downstream conversion (sales) weakened"
  ],
  ["mktg_campaign_perf_summary", "mktg_lead_quality", "mktg_efficiency", "mktg_lead_funnel"],
  "CAC increases when cost rises or outcomes fall. If spend is stable but CAC rises, focus on quality and funnel conversion; if spend rises, verify whether the additional spend drove proportional outcomes.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "marketing",
  "monthly_trend",
  "volatility",
  [
    "Monthly pacing differences (front/back-loaded spend)",
    "Campaign launches/pauses mid-month",
    "Seasonality or holiday effects",
    "Reporting latency or backfills",
    "Tracking/attribution updates causing discontinuities"
  ],
  ["mktg_monthly_spend_leads", "mktg_total_spend"],
  "Month-over-month volatility is often operational (pacing, launches) or measurement-driven (latency/backfills). Look for step-changes aligned with campaign changes or tracking releases before concluding performance truly shifted.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
);

INSERT INTO `metadata.rag_diagnostics`
(domain, metric_key, change_type, likely_causes, checks_to_perform, exec_friendly_summary)
VALUES

-- =========================
-- LEADS
-- =========================
(
  "marketing",
  "leads",
  "increase",
  [
    "Increased spend or expanded campaign reach",
    "Improved conversion rates on landing pages",
    "Channel mix shift toward higher-volume sources",
    "Seasonal demand uplift or promotional activity"
  ],
  [
    "mktg_monthly_spend_leads",
    "mktg_campaign_perf_summary",
    "mktg_lead_quality"
  ],
  "An increase in leads usually reflects higher reach or better conversion. Validate whether lead quality held steady to ensure the growth is sustainable and not driven by low-intent traffic."
),
(
  "marketing",
  "leads",
  "plateau",
  [
    "Audience saturation in key channels",
    "Spend increases offset by declining conversion",
    "Creative fatigue reducing marginal gains",
    "Operational limits on campaign scale"
  ],
  [
    "mktg_efficiency",
    "mktg_monthly_spend_leads",
    "mktg_lead_quality"
  ],
  "A lead plateau often indicates saturation or diminishing returns. If spend is rising while leads are flat, investigate efficiency, creative refresh needs, and channel diversification."
),

-- =========================
-- TOTAL SPEND
-- =========================
(
  "marketing",
  "total_spend",
  "plateau",
  [
    "Budget caps or pacing controls",
    "Stable campaign mix with no expansion",
    "Delivery limits in key channels",
    "Intentional spend stabilization"
  ],
  [
    "mktg_total_spend",
    "mktg_campaign_perf_summary"
  ],
  "Flat spend typically reflects intentional budget control or delivery constraints. Focus interpretation on whether outcomes improved or degraded under a steady investment level."
),

-- =========================
-- CAC
-- =========================
(
  "marketing",
  "cac",
  "decrease",
  [
    "Improved lead quality or intent",
    "Better conversion rates downstream",
    "Shift toward lower-cost, higher-performing channels",
    "Campaign optimization and learning effects"
  ],
  [
    "mktg_lead_quality",
    "mktg_avg_lead_score",
    "mktg_efficiency",
    "mktg_campaign_perf_summary"
  ],
  "A decrease in CAC typically reflects improved efficiency. Confirm that lead volume and quality remained healthy to ensure the improvement is sustainable rather than volume-driven."
),
(
  "marketing",
  "cac",
  "plateau",
  [
    "Offsetting changes in spend and conversions",
    "Stable channel and audience mix",
    "Efficiency gains matched by rising costs",
    "Mature optimization state"
  ],
  [
    "mktg_efficiency",
    "mktg_lead_quality",
    "mktg_monthly_spend_leads"
  ],
  "A flat CAC often indicates a balance between rising costs and improved performance. Focus on whether incremental investment is still delivering acceptable returns."
),

-- =========================
-- LEAD QUALITY
-- =========================
(
  "marketing",
  "lead_quality",
  "plateau",
  [
    "Stable targeting and audience mix",
    "Lead scoring model unchanged",
    "No significant creative or offer changes",
    "Consistent channel performance"
  ],
  [
    "mktg_lead_quality",
    "mktg_avg_lead_score"
  ],
  "Flat lead quality suggests consistency in targeting and intent. Improvements may require creative refresh, audience expansion, or offer changes."
),

-- =========================
-- AVG LEAD SCORE
-- =========================
(
  "marketing",
  "avg_lead_score",
  "decrease",
  [
    "Shift toward lower-intent channels",
    "Creative attracting less qualified audiences",
    "Scoring model recalibration",
    "Higher top-of-funnel volume diluting average"
  ],
  [
    "mktg_avg_lead_score",
    "mktg_lead_quality",
    "mktg_campaign_perf_summary"
  ],
  "A declining average lead score often explains downstream efficiency issues. Validate whether the scoring model changed before attributing the drop to campaign performance."
),
(
  "marketing",
  "avg_lead_score",
  "plateau",
  [
    "Stable targeting and scoring rules",
    "Limited experimentation in campaigns",
    "Optimization ceiling reached"
  ],
  [
    "mktg_lead_quality",
    "mktg_lead_funnel"
  ],
  "A flat average lead score suggests stable intent. To improve, experiment with new audiences, creatives, or qualification criteria."
),

-- =========================
-- EFFICIENCY
-- =========================
(
  "marketing",
  "efficiency",
  "decrease",
  [
    "Rising costs without proportional outcome gains",
    "Creative fatigue or audience saturation",
    "Channel mix shift toward lower-performing sources",
    "Deterioration in lead quality or conversion"
  ],
  [
    "mktg_efficiency",
    "mktg_lead_quality",
    "mktg_campaign_perf_summary"
  ],
  "A decline in efficiency indicates diminishing returns. Investigate channel mix, creative performance, and quality metrics before reallocating budget."
),
(
  "marketing",
  "efficiency",
  "plateau",
  [
    "Optimization maturity reached",
    "Incremental spend yielding proportional outcomes",
    "Stable channel and audience mix"
  ],
  [
    "mktg_efficiency",
    "mktg_monthly_spend_leads"
  ],
  "A flat efficiency curve often means optimization has matured. Further gains may require new channels, audiences, or product-led improvements."
);

INSERT INTO `metadata.rag_diagnostics`
(domain, metric_key, change_type, likely_causes, checks_to_perform, exec_friendly_summary, created_at, updated_at)
VALUES

-- =========================
-- TOTAL REVENUE
-- =========================
(
  "revenue","revenue","increase",
  ["Higher order volume","Price increases","Favorable product or subscription mix","Expansion within existing customers"],
  ["rev_monthly_revenue_trend","rev_revenue_by_product","rev_revenue_by_club"],
  "Revenue growth typically reflects increased demand, pricing power, or favorable mix. Validate whether growth is broad-based or concentrated in a few customers or products.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "revenue","revenue","decrease",
  ["Churn or customer contraction","Discounting or pricing pressure","Shift to lower-value products","Seasonal or cyclical slowdown"],
  ["rev_monthly_revenue_trend","rev_revenue_by_product","rev_revenue_by_club"],
  "A revenue decline can stem from churn, pricing pressure, or mix shifts. Identify whether the decline is structural or timing-related.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "revenue","revenue","plateau",
  ["Stable demand","Offsetting growth and churn","Mature market dynamics"],
  ["rev_monthly_revenue_trend"],
  "Flat revenue often indicates maturity or offsetting forces. Growth may require new products, pricing changes, or market expansion.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- MRR
-- =========================
(
  "revenue","mrr","increase",
  ["New subscriptions","Upgrades to higher tiers","Price increases","Improved renewals"],
  ["rev_monthly_mrr_trend","rev_subscription_revenue_mix","rev_subscription_penetration_by_club"],
  "Rising MRR signals improving recurring stability. Confirm churn remains controlled to ensure durability.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "revenue","mrr","decrease",
  ["Subscription churn","Downgrades","Discounting or incentives","Delayed renewals"],
  ["rev_monthly_mrr_trend","rev_subscription_revenue_mix"],
  "MRR decline is an early warning for revenue durability. Investigate churn and downgrade drivers promptly.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "revenue","mrr","plateau",
  ["Offsetting new subscriptions and churn","Stable pricing","Mature subscriber base"],
  ["rev_monthly_mrr_trend"],
  "Flat MRR suggests stability but limited growth momentum. Expansion may require new segments or packaging.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- ARR
-- =========================
(
  "revenue","arr","increase",
  ["Sustained MRR growth","Longer contract commitments","Higher subscription penetration"],
  ["rev_monthly_mrr_trend","rev_subscription_penetration_by_club"],
  "ARR growth indicates durable, long-term revenue expansion rather than short-term deal timing.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "revenue","arr","decrease",
  ["Churn","Subscription downgrades","Contract non-renewals"],
  ["rev_monthly_mrr_trend"],
  "ARR decline signals future revenue risk and should trigger retention and renewal analysis.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "revenue","arr","plateau",
  ["Stable renewals","Offsetting churn and growth"],
  ["rev_monthly_mrr_trend"],
  "Flat ARR suggests maturity in the subscription base with limited net expansion.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- TOTAL DEALS
-- =========================
(
  "revenue","total_deals","increase",
  ["Higher sales activity","Improved lead flow","Market expansion"],
  ["rev_revenue_by_club"],
  "An increase in deals reflects higher sales motion, but does not guarantee revenue growth. Validate deal size and win rate.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "revenue","total_deals","decrease",
  ["Reduced sales capacity","Market slowdown","Longer sales cycles"],
  ["rev_revenue_by_club"],
  "Fewer deals may indicate pipeline weakness or a strategic shift toward fewer, larger deals.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "revenue","total_deals","plateau",
  ["Stable pipeline volume","Capacity limits"],
  ["rev_revenue_by_club"],
  "Flat deal volume suggests stable sales capacity without expansion.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- TOTAL ORDERS
-- =========================
(
  "revenue","total_orders","increase",
  ["Higher customer demand","Renewals","Upsell success"],
  ["rev_revenue_by_product","rev_monthly_revenue_trend"],
  "Order growth indicates demand strength, but validate revenue per order to ensure value growth.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "revenue","total_orders","decrease",
  ["Demand softening","Churn","Lower conversion from deals to orders"],
  ["rev_revenue_by_product","rev_monthly_revenue_trend"],
  "Order decline may precede revenue decline if sustained.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "revenue","total_orders","plateau",
  ["Stable customer base","Market saturation"],
  ["rev_revenue_by_product"],
  "Flat order volume suggests maturity without new demand drivers.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- DEAL WIN RATE
-- =========================
(
  "revenue","deal_win_rate","increase",
  ["Improved sales execution","Better qualification","Competitive pricing"],
  ["rev_revenue_by_club"],
  "Rising win rate indicates stronger sales effectiveness and deal quality.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "revenue","deal_win_rate","decrease",
  ["Pricing pressure","Lower lead quality","Longer sales cycles"],
  ["rev_revenue_by_club"],
  "Declining win rate often explains why deal volume does not translate into revenue.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "revenue","deal_win_rate","plateau",
  ["Consistent sales performance","Stable market dynamics"],
  ["rev_revenue_by_club"],
  "Flat win rate suggests process stability but limited optimization gains.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- SUBSCRIPTION MIX
-- =========================
(
  "revenue","subscription_mix","increase",
  ["Upgrades to higher tiers","Pricing strategy effectiveness"],
  ["rev_subscription_revenue_mix"],
  "A favorable mix shift increases MRR without requiring more customers.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "revenue","subscription_mix","decrease",
  ["Downgrades","Discount-driven sales","Lower-tier adoption"],
  ["rev_subscription_revenue_mix"],
  "A declining mix can pressure MRR even when subscriber count is stable.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "revenue","subscription_mix","plateau",
  ["Stable customer behavior","Limited tier differentiation"],
  ["rev_subscription_revenue_mix"],
  "Flat mix suggests pricing and packaging changes may be needed.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- PRODUCT MIX
-- =========================
(
  "revenue","product_mix","increase",
  ["Successful product adoption","Cross-sell/upsell"],
  ["rev_revenue_by_product"],
  "A favorable product mix improves revenue quality and margin profile.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "revenue","product_mix","decrease",
  ["Demand shift to lower-value products","Competitive pressure"],
  ["rev_revenue_by_product"],
  "A declining product mix may pressure margins despite stable revenue.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "revenue","product_mix","plateau",
  ["Stable portfolio","Limited innovation"],
  ["rev_revenue_by_product"],
  "Flat mix indicates limited portfolio movement.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- SUBSCRIPTION PENETRATION
-- =========================
(
  "revenue","subscription_penetration","increase",
  ["Improved sales adoption","Better product-market fit"],
  ["rev_subscription_penetration_by_club"],
  "Rising penetration reflects broader adoption even if spend per customer is unchanged.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "revenue","subscription_penetration","decrease",
  ["Churn","Non-renewals","Market contraction"],
  ["rev_subscription_penetration_by_club"],
  "Declining penetration signals adoption or retention challenges.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "revenue","subscription_penetration","plateau",
  ["Market saturation","Stable renewals"],
  ["rev_subscription_penetration_by_club"],
  "Flat penetration suggests limited expansion without new markets or segments.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- MONTHLY TREND (VOLATILITY)
-- =========================
(
  "revenue","monthly_revenue_trend","volatility",
  ["Deal timing effects","Seasonality","Renewal clustering","One-off large deals"],
  ["rev_monthly_revenue_trend"],
  "Revenue volatility is often timing-driven. Look for structural shifts before concluding performance changed.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
);


INSERT INTO `metadata.rag_diagnostics`
(domain, metric_key, change_type, likely_causes, checks_to_perform, exec_friendly_summary, created_at, updated_at)
VALUES

-- =========================
-- TOTAL GOALS
-- =========================
(
  "sports",
  "total_goals",
  "increase",
  [
    "Improved chance creation",
    "Higher shot volume",
    "Better finishing efficiency",
    "Weaker opposition defense"
  ],
  ["sprt_goals_vs_xg", "sprt_goal_conversion_pct"],
  "An increase in goals can be driven by better chance creation or improved finishing. Validate sustainability by comparing goals against xG.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "sports",
  "total_goals",
  "decrease",
  [
    "Reduced shot volume",
    "Lower chance quality",
    "Poor finishing",
    "Stronger opposition defense"
  ],
  ["sprt_goals_vs_xg", "sprt_shots_on_target_trend"],
  "A decline in goals may reflect fewer chances or finishing variance. Compare goals with xG to isolate the driver.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "sports",
  "total_goals",
  "plateau",
  [
    "Stable attacking output",
    "Consistent tactical approach",
    "Offsetting improvements and declines"
  ],
  ["sprt_goals_vs_xg"],
  "Flat goal output suggests stable attacking performance. Focus on xG and conversion to identify marginal gains.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- EXPECTED GOALS (xG)
-- =========================
(
  "sports",
  "xg",
  "increase",
  [
    "Improved chance quality",
    "More high-danger shots",
    "Tactical changes creating better opportunities"
  ],
  ["sprt_goals_vs_xg"],
  "Rising xG indicates improved chance creation. Goals should eventually follow if finishing normalizes.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "sports",
  "xg",
  "decrease",
  [
    "Fewer quality chances",
    "More low-probability shots",
    "Stronger defensive opposition"
  ],
  ["sprt_goals_vs_xg"],
  "Declining xG suggests reduced chance quality. Tactical or personnel changes may be required.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "sports",
  "xg",
  "plateau",
  [
    "Stable attacking patterns",
    "Consistent chance creation level"
  ],
  ["sprt_goals_vs_xg"],
  "Flat xG indicates a stable attacking profile. Improvements may require structural changes.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- GOAL CONVERSION
-- =========================
(
  "sports",
  "goal_conversion_pct",
  "increase",
  [
    "Improved finishing",
    "Better shot selection",
    "Favorable variance"
  ],
  ["sprt_goals_vs_xg"],
  "Higher conversion may reflect better finishing, but short-term spikes can regress without xG support.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "sports",
  "goal_conversion_pct",
  "decrease",
  [
    "Poor finishing",
    "Lower-quality shots",
    "Goalkeeper overperformance by opponents"
  ],
  ["sprt_goals_vs_xg"],
  "Declining conversion often reflects finishing variance. Validate whether xG remains stable.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "sports",
  "goal_conversion_pct",
  "plateau",
  [
    "Stable finishing level",
    "Consistent shot profile"
  ],
  ["sprt_goals_vs_xg"],
  "Flat conversion suggests finishing is neither improving nor deteriorating. Focus on chance creation.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- SHOTS ON TARGET
-- =========================
(
  "sports",
  "shots_on_target",
  "increase",
  [
    "Higher attacking tempo",
    "More sustained pressure",
    "Tactical shift toward shooting"
  ],
  ["sprt_shots_on_target_trend"],
  "An increase in shots on target reflects greater attacking pressure, but not necessarily better chances.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "sports",
  "shots_on_target",
  "decrease",
  [
    "Reduced attacking intent",
    "Stronger opposition press",
    "Tactical conservatism"
  ],
  ["sprt_shots_on_target_trend"],
  "A decline in shots on target indicates reduced pressure. Assess whether this is strategic or problematic.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "sports",
  "shots_on_target",
  "plateau",
  [
    "Stable attacking style",
    "Consistent match control"
  ],
  ["sprt_shots_on_target_trend"],
  "Flat shot volume suggests consistent pressure levels.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- DEFENSIVE DISCIPLINE
-- =========================
(
  "sports",
  "defensive_discipline",
  "increase",
  [
    "Aggressive pressing",
    "Late challenges",
    "Defensive fatigue"
  ],
  ["sprt_defensive_discipline"],
  "Increased fouls or cards may signal aggressive tactics or loss of defensive control.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "sports",
  "defensive_discipline",
  "decrease",
  [
    "Improved defensive timing",
    "Better positioning",
    "Reduced pressing intensity"
  ],
  ["sprt_defensive_discipline"],
  "Improved discipline reduces defensive risk and fatigue.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "sports",
  "defensive_discipline",
  "plateau",
  [
    "Stable defensive behavior",
    "Consistent tactical approach"
  ],
  ["sprt_defensive_discipline"],
  "Flat discipline suggests a consistent defensive approach.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- DEFENSIVE PERFORMANCE (xGC vs Goals Conceded)
-- =========================
(
  "sports",
  "xgc",
  "increase",
  [
    "Allowing higher-quality chances",
    "Defensive shape breakdown",
    "Opposition tactical superiority"
  ],
  ["sprt_conceded_vs_xgc"],
  "Rising xGC indicates defensive vulnerability. Goals conceded may follow if not addressed.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "sports",
  "xgc",
  "decrease",
  [
    "Improved defensive organization",
    "Better shot suppression",
    "Tactical adjustments"
  ],
  ["sprt_conceded_vs_xgc"],
  "Lower xGC reflects improved defensive control and sustainability.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "sports",
  "xgc",
  "plateau",
  [
    "Stable defensive structure",
    "Consistent opposition quality"
  ],
  ["sprt_conceded_vs_xgc"],
  "Flat xGC indicates consistent defensive performance.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- SEASONAL TREND
-- =========================
(
  "sports",
  "seasonal_trend",
  "volatility",
  [
    "Squad changes",
    "Managerial or tactical shifts",
    "Injuries or fixture congestion",
    "Opposition strength variance"
  ],
  ["sprt_total_goals_trend", "sprt_defensive_seasonal_profile"],
  "Seasonal volatility often reflects structural changes. Compare multiple metrics to understand true progression.",
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
);


