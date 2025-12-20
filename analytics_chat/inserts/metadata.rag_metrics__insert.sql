INSERT INTO `metadata.rag_metrics`
(domain, metric_key, metric_name, definition, calculation_summary, common_drivers, interpretation_notes, related_metrics, created_at, updated_at)
VALUES
(
  "marketing",
  "total_spend",
  "Total Spend",
  "Total advertising spend for the selected campaigns/channels/time period.",
  "Sum of ad spend across all records in scope (campaign/channel/time filters).",
  ["budget changes", "campaign activation/pauses", "channel mix shifts", "bid/auction dynamics", "seasonality"],
  "Use Total Spend to understand investment level. Pair with leads and CAC to judge efficiency; spend alone is not performance.",
  ["leads", "cac", "cpl", "spend_share", "channel_mix"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "marketing",
  "leads",
  "Leads",
  "Count of leads generated from marketing activity for the selected scope.",
  "Count of lead events attributed to campaigns/channels in scope.",
  ["traffic volume changes", "conversion rate changes", "tracking/attribution changes", "landing page performance", "seasonality"],
  "Leads measure volume, not quality. Always interpret alongside lead quality/lead score and CAC/CPL.",
  ["lead_quality", "avg_lead_score", "cac", "cpl", "conversion_rate"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "marketing",
  "cac",
  "Customer Acquisition Cost (CAC)",
  "Average cost to acquire a customer (or acquisition proxy) from marketing spend.",
  "Typically spend divided by acquired customers; in many marketing dashboards it is approximated using qualified leads or conversions as the denominator.",
  ["spend changes", "conversion/qualification rate shifts", "mix of high-cost channels", "pricing/offer changes", "sales follow-up effectiveness"],
  "CAC is only meaningful if the denominator is consistent. If conversions/qualified leads definitions change, CAC will move even when spend is flat.",
  ["total_spend", "leads", "conversion_rate", "lead_quality"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "marketing",
  "lead_quality",
  "Lead Quality",
  "Quality segmentation of leads (e.g., high/medium/low) indicating likelihood to convert or value.",
  "Leads are bucketed into quality tiers using business rules or a scoring model.",
  ["audience targeting changes", "channel mix", "lead scoring model updates", "form friction/intent", "offer quality"],
  "If lead volume goes up but lead quality goes down, you may be buying cheaper traffic. Use quality to explain CAC movements.",
  ["avg_lead_score", "leads", "cac", "conversion_rate"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "marketing",
  "avg_lead_score",
  "Average Lead Score",
  "Average lead score across leads in scope, representing propensity/intent/value.",
  "Average of lead_score field for leads attributed to campaigns/channels in scope.",
  ["scoring model recalibration", "audience mix shifts", "channel mix", "campaign messaging changes", "seasonality"],
  "A rising average lead score suggests improved targeting/intent, but confirm the scoring model didn’t change (definition drift).",
  ["lead_quality", "leads", "cac"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "marketing",
  "funnel_conversion",
  "Funnel Conversion",
  "Movement of leads through funnel stages (e.g., Lead → MQL → SQL → Customer).",
  "Counts by stage and/or stage-to-stage conversion rates within the selected scope.",
  ["lead quality shifts", "sales capacity/follow-up", "stage definition changes", "attribution changes", "product/offer changes"],
  "Funnel is where volume becomes outcomes. If spend is up but later stages are flat, investigate quality or sales follow-up.",
  ["leads", "lead_quality", "avg_lead_score", "cac"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "marketing",
  "efficiency",
  "Marketing Efficiency",
  "How effectively spend converts into outcomes (leads, conversions) at acceptable cost (CAC).",
  "Compared using ratios like spend per lead (CPL), CAC, and relative performance across campaigns.",
  ["channel saturation", "creative fatigue", "audience overlap", "bidding changes", "seasonality"],
  "Efficiency is comparative: use it to choose where to shift budget. Validate with trend charts to avoid one-time anomalies.",
  ["total_spend", "leads", "cac", "cpl", "conversion_rate"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "marketing",
  "monthly_trend",
  "Monthly Trend",
  "Month-over-month movement of spend and leads to identify growth, seasonality, and anomalies.",
  "Aggregates spend and leads by month for the selected scope.",
  ["seasonality", "budget pacing", "campaign start/stop timing", "tracking changes", "market shocks"],
  "Use monthly trends to explain changes in averages. If a single month spikes, investigate pacing or campaign launches.",
  ["total_spend", "leads", "cac"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
);


INSERT INTO `metadata.rag_metrics`
(domain, metric_key, metric_name, definition, calculation_summary, common_drivers, interpretation_notes, related_metrics, created_at, updated_at)
VALUES

-- =========================
-- CORE REVENUE
-- =========================
(
  "revenue",
  "revenue",
  "Total Revenue",
  "Total recognized revenue generated from orders and subscriptions within the selected scope.",
  "Sum of revenue amounts across all completed orders and active subscriptions in scope.",
  ["order volume", "pricing changes", "product mix", "subscription adoption", "renewals and churn"],
  "Revenue reflects realized value. Interpret alongside MRR and mix metrics to assess sustainability and quality of growth.",
  ["mrr", "arr", "product_mix", "subscription_mix"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- RECURRING REVENUE
-- =========================
(
  "revenue",
  "mrr",
  "Monthly Recurring Revenue (MRR)",
  "Recurring monthly revenue generated from active subscriptions.",
  "Sum of recurring subscription revenue normalized to a monthly basis.",
  ["new subscriptions", "churn", "upgrades/downgrades", "pricing changes"],
  "MRR is a stability indicator. Validate spikes or drops against churn and subscription mix.",
  ["revenue", "arr", "subscription_mix"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "revenue",
  "arr",
  "Annual Recurring Revenue (ARR)",
  "Annualized value of recurring subscription revenue.",
  "ARR = MRR × 12.",
  ["subscription growth", "pricing strategy", "churn", "plan upgrades/downgrades"],
  "ARR smooths short-term volatility and reflects long-term revenue durability.",
  ["mrr", "subscription_mix"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- SALES VOLUME
-- =========================
(
  "revenue",
  "total_orders",
  "Total Orders",
  "Total number of completed customer orders in the selected period.",
  "Count of completed order records within the selected scope.",
  ["customer demand", "deal conversion", "renewals", "seasonality"],
  "Order volume measures activity, not value. Always pair with revenue per order.",
  ["revenue", "deal_win_rate"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "revenue",
  "total_deals",
  "Total Deals",
  "Total number of sales deals created or closed in the selected period.",
  "Count of deal records within the selected scope.",
  ["sales activity level", "pipeline health", "market demand"],
  "Deal volume reflects sales motion intensity, not deal quality or value.",
  ["deal_win_rate", "revenue"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- SALES QUALITY
-- =========================
(
  "revenue",
  "deal_win_rate",
  "Deal Win Rate",
  "Percentage of sales deals successfully closed as won.",
  "Won deals divided by total deals in scope.",
  ["sales effectiveness", "pricing competitiveness", "lead quality", "sales cycle length"],
  "Win rate is a quality metric. It explains why deal volume does or does not translate into revenue.",
  ["total_deals", "revenue"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- MIX & ADOPTION
-- =========================
(
  "revenue",
  "subscription_mix",
  "Subscription Revenue Mix",
  "Distribution of recurring revenue across subscription tiers or plans.",
  "Recurring revenue grouped by subscription tier or plan.",
  ["tier upgrades/downgrades", "pricing strategy", "customer segmentation"],
  "Mix shifts can move MRR even if total subscriber count is flat.",
  ["mrr", "arr", "subscription_penetration"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "revenue",
  "product_mix",
  "Product Revenue Mix",
  "Distribution of revenue across products or product categories.",
  "Revenue grouped by product or product category.",
  ["product adoption", "cross-sell/upsell", "pricing differences"],
  "Product mix often explains revenue change without volume change.",
  ["revenue", "subscription_mix"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "revenue",
  "subscription_penetration",
  "Subscription Penetration",
  "Share of clubs or customers with an active subscription.",
  "Subscribed entities divided by total eligible entities.",
  ["sales adoption", "product-market fit", "pricing", "renewal success"],
  "Penetration measures breadth of adoption, not depth of spend.",
  ["mrr", "subscription_mix"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- TRENDS
-- =========================
(
  "revenue",
  "monthly_revenue_trend",
  "Monthly Revenue Trend",
  "Month-over-month movement of total revenue.",
  "Revenue aggregated by calendar month within the selected scope.",
  ["seasonality", "deal timing", "renewals", "pricing changes"],
  "Use trends to distinguish structural growth from timing effects.",
  ["revenue", "mrr"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
);

INSERT INTO `metadata.rag_metrics`
(domain, metric_key, metric_name, definition, calculation_summary, common_drivers, interpretation_notes, related_metrics, created_at, updated_at)
VALUES
(
  "sports",
  "matches_played",
  "Matches Played",
  "Total number of matches played in the selected scope.",
  "Count of matches played.",
  ["season length", "competition format", "schedule density"],
  "Used as context for rate-based metrics. Always normalize goals and shots per match when comparing teams.",
  ["total_goals", "total_shots"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "sports",
  "avg_possession",
  "Average Possession",
  "Average percentage of ball possession across matches.",
  "Average possession percentage across all matches in scope.",
  ["tactical style", "opposition strength", "game state"],
  "Possession alone does not imply effectiveness. Pair with shots, xG, and conversion.",
  ["xg", "shots_on_target"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "sports",
  "total_shots",
  "Total Shots",
  "Total number of shots attempted.",
  "Count of all shots taken.",
  ["attacking intent", "tactical approach", "match tempo"],
  "Shot volume indicates pressure, but quality (xG) determines effectiveness.",
  ["shots_on_target", "xg"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
);


INSERT INTO `metadata.rag_metrics`
(domain, metric_key, metric_name, definition, calculation_summary, common_drivers, interpretation_notes, related_metrics, created_at, updated_at)
VALUES

-- =========================
-- SCORING & ATTACK
-- =========================
(
  "sports",
  "total_goals",
  "Total Goals",
  "Total number of goals scored by a club within the selected scope.",
  "Count of goal events for the selected club and season(s).",
  ["shot volume", "shot quality", "finishing ability", "opposition strength"],
  "Goals are the outcome metric. Always interpret alongside xG and shots to understand sustainability.",
  ["xg", "shots_on_target", "goal_conversion_pct"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "sports",
  "xg",
  "Expected Goals (xG)",
  "Model-based estimate of goal probability based on shot quality.",
  "Sum of expected goal values across all shots.",
  ["chance quality", "shot location", "chance creation patterns"],
  "xG reflects chance quality, not finishing. Persistent gaps between goals and xG may regress.",
  ["total_goals", "goal_conversion_pct"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "sports",
  "goal_conversion_pct",
  "Goal Conversion Percentage",
  "Percentage of shots converted into goals.",
  "Goals divided by total shots or shots on target.",
  ["finishing skill", "shot selection", "opposition defense"],
  "High conversion rates may be unsustainable without strong xG support.",
  ["total_goals", "shots_on_target", "xg"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- SHOOTING
-- =========================
(
  "sports",
  "shots_on_target",
  "Shots on Target",
  "Number of shots that required a save or resulted in a goal.",
  "Count of shots classified as on target.",
  ["attacking intent", "chance creation", "tactical approach"],
  "Shots on target reflect pressure but not necessarily chance quality.",
  ["xg", "total_goals"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- DEFENSIVE METRICS
-- =========================
(
  "sports",
  "goals_conceded",
  "Goals Conceded",
  "Total number of goals conceded by a club.",
  "Count of goals allowed within the selected scope.",
  ["defensive organization", "opposition strength", "goalkeeper performance"],
  "Goals conceded should be evaluated with xGC to assess defensive sustainability.",
  ["xgc", "defensive_discipline"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),
(
  "sports",
  "xgc",
  "Expected Goals Conceded (xGC)",
  "Model-based estimate of goal probability allowed based on shots faced.",
  "Sum of expected goal values conceded across all opponent shots.",
  ["defensive shape", "shot suppression", "opponent chance quality"],
  "xGC reflects defensive chance quality allowed, not finishing variance.",
  ["goals_conceded", "defensive_discipline"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- DISCIPLINE & DEFENSE
-- =========================
(
  "sports",
  "defensive_discipline",
  "Defensive Discipline",
  "Fouls, cards, and disciplinary actions committed by the team.",
  "Count of fouls, yellow cards, and red cards.",
  ["pressing intensity", "defensive timing", "referee tendencies"],
  "Poor discipline can lead to dangerous situations and fatigue over time.",
  ["goals_conceded", "xgc"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- =========================
-- TRENDS
-- =========================
(
  "sports",
  "seasonal_trend",
  "Seasonal Performance Trend",
  "Performance trends observed across seasons.",
  "Metric values aggregated by season.",
  ["squad changes", "managerial changes", "tactical evolution"],
  "Seasonal trends help separate one-off performance from structural change.",
  ["total_goals", "goals_conceded", "xg", "xgc"],
  CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
);

