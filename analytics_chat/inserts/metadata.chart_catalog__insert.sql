INSERT INTO metadata.chart_catalog (
  chart_id, project_name, chart_title, description, tags, allowed_filters,
  render_engine, looker_report_id, looker_page_id, default_viz_type,
  sql_template, is_active, created_at, updated_at
)
VALUES
(
  'mktg_campaign_perf_summary',
  'marketing',
  'Campaign Performance Summary',
  'Overall campaign performance including leads, spend, CAC & conversions.',
  ['performance','summary','overview'],
  ['campaign','channel'],
  'looker',
  '0d005318-b909-4247-a511-928f3af4b97c',
  'jNsfF',
  'combo',
  NULL,
  TRUE,
  CURRENT_TIMESTAMP(),
  CURRENT_TIMESTAMP()
),
(
  'mktg_total_spend',
  'marketing',
  'Total Spend by Campaign',
  'Bar chart showing total ad spend per campaign.',
  ['spend','budget','cost'],
  ['campaign','channel'],
  'looker',
  'd97ef051-b046-493d-9900-fefd49d48d24',
  'jNsfF',
  'bar',
  NULL,
  TRUE,
  CURRENT_TIMESTAMP(),
  CURRENT_TIMESTAMP()
),
(
  'mktg_lead_quality',
  'marketing',
  'Lead Quality Breakdown',
  'Lead scoring + quality segmentation for each campaign.',
  ['lead_quality','scoring','segmentation'],
  ['campaign','channel'],
  'looker',
  '6d70a58f-4014-485b-9e9e-7ca05ca0c987',
  'jNsfF',
  'bar',
  NULL,
  TRUE,
  CURRENT_TIMESTAMP(),
  CURRENT_TIMESTAMP()
),
(
  'mktg_avg_lead_score',
  'marketing',
  'Average Lead Score by Campaign',
  'Average lead score visualization across campaigns.',
  ['lead_score','quality','trend'],
  ['campaign','channel'],
  'looker',
  '45fdea99-95ef-4749-843e-4af380d35078',
  'jNsfF',
  'line',
  NULL,
  TRUE,
  CURRENT_TIMESTAMP(),
  CURRENT_TIMESTAMP()
),
(
  'mktg_lead_funnel',
  'marketing',
  'Lead Funnel Breakdown',
  'Funnel counts by stage for each campaign.',
  ['funnel','conversion','stages'],
  ['campaign','channel'],
  'looker',
  '041b1f8c-f713-4752-a47e-01d4634c9917',
  'jNsfF',
  'funnel',
  NULL,
  TRUE,
  CURRENT_TIMESTAMP(),
  CURRENT_TIMESTAMP()
),
(
  'mktg_monthly_spend_leads',
  'marketing',
  'Monthly Spend & Leads',
  'Month-over-month trend for spend and leads.',
  ['trend','monthly','time_series'],
  ['campaign','channel'],
  'looker',
  'c2ec64e9-fd5b-448c-8ccf-efd70c19c121',
  'jNsfF',
  'line',
  NULL,
  TRUE,
  CURRENT_TIMESTAMP(),
  CURRENT_TIMESTAMP()
),
(
  'mktg_efficiency',
  'marketing',
  'Campaign Efficiency Analysis',
  'Bubble chart comparing spend, leads, and CAC across campaigns.',
  ['efficiency','cac','bubble','comparison'],
  ['campaign','channel'],
  'looker',
  'd4b8c0c1-55f0-4918-9b48-c4189cfaecf0',
  'jNsfF',
  'bubble',
  NULL,
  TRUE,
  CURRENT_TIMESTAMP(),
  CURRENT_TIMESTAMP()
),
(
  'mktg_master_dashboard',
  'marketing',
  'Marketing Master Dashboard',
  'Full dashboard containing all marketing charts.',
  ['dashboard','overview','all_charts'],
  ['campaign','channel'],
  'looker',
  'd32d1831-28ad-4826-abbd-16528cdcd557',
  'jNsfF',
  'dashboard',
  NULL,
  TRUE,
  CURRENT_TIMESTAMP(),
  CURRENT_TIMESTAMP()
);


INSERT INTO metadata.chart_catalog (
  chart_id, project_name, chart_title, description, tags, allowed_filters,
  render_engine, looker_report_id, looker_page_id,
  default_viz_type, sql_template, is_active,
  created_at, updated_at
)
VALUES
-- 1. Master
(
  'rev_master_dashboard',
  'revenue',
  'Revenue Master Dashboard',
  'End-to-end revenue dashboard across clubs, products, and subscriptions.',
  ['revenue','dashboard','overview'],
  ['club','product_category','product','subscription','league','deal_stage','channel'],
  'looker',
  '8363d8ae-bc1f-4060-8d2f-6bdbe6d5e0c8',
  '3hMgF',
  'dashboard',
  NULL, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- 2. Monthly Revenue Trend
(
  'rev_monthly_revenue_trend',
  'revenue',
  'Monthly Revenue Trend',
  'Month-over-month revenue trend.',
  ['revenue','trend','monthly'],
  ['club','product_category','product','subscription','league','deal_stage','channel'],
  'looker',
  'eb3e3648-ed76-4abd-b5a2-2613bc1f6acf',
  '3hMgF',
  'line',
  NULL, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- 3. Monthly MRR Trend
(
  'rev_monthly_mrr_trend',
  'revenue',
  'Monthly MRR Trend',
  'Monthly recurring revenue trend.',
  ['mrr','subscription','trend'],
  ['club','product_category','product','subscription','league','deal_stage','channel'],
  'looker',
  'f9fff02d-f01c-4628-81ee-97e1e7fec69f',
  '3hMgF',
  'line',
  NULL, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- 4. Revenue by Product Category
(
  'rev_revenue_by_product_category',
  'revenue',
  'Revenue by Product Category',
  'Revenue split by product category.',
  ['revenue','product_category','mix'],
  ['club','product_category','subscription','league','deal_stage','channel'],
  'looker',
  '71a65b9e-a61d-45bc-a0d8-49092b9aff07',
  '3hMgF',
  'bar',
  NULL, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- 5. Revenue by Product Name
(
  'rev_revenue_by_product',
  'revenue',
  'Revenue by Product',
  'Revenue distribution by product.',
  ['revenue','product','mix'],
  ['club','product_category','product','subscription','league','deal_stage','channel'],
  'looker',
  '5f9937c5-308b-4ada-87cc-8adb0ae997eb',
  '3hMgF',
  'bar',
  NULL, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- 6. Revenue by Club
(
  'rev_revenue_by_club',
  'revenue',
  'Revenue by Club',
  'Revenue contribution by club.',
  ['revenue','club','ranking'],
  ['club','product_category','product','subscription','league','deal_stage','channel'],
  'looker',
  'a08a9d91-fde1-433a-bb31-c1f3abce9795',
  '3hMgF',
  'bar',
  NULL, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- 7. Subscription Revenue Mix
(
  'rev_subscription_revenue_mix',
  'revenue',
  'Subscription Revenue Mix',
  'Revenue mix by subscription tier.',
  ['subscription','revenue','mix'],
  ['club','product_category','product','subscription','league','deal_stage','channel'],
  'looker',
  'e62b4ba0-392d-4f56-8fea-10902289fed8',
  '3hMgF',
  'donut',
  NULL, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- 8. Top 5 Clubs by Spending
(
  'rev_top_5_clubs_by_spend',
  'revenue',
  'Top 5 Clubs by Spending',
  'Top 5 clubs by total spend.',
  ['club','spend','ranking'],
  ['club','deal_stage','channel'],
  'looker',
  '9c5ce168-be86-4df5-9195-35b94d7b618a',
  '3hMgF',
  'bar',
  NULL, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- 9. Product Revenue Mix by Category
(
  'rev_product_revenue_mix_by_category',
  'revenue',
  'Product Revenue Mix by Category',
  'Product revenue mix grouped by category.',
  ['product','category','mix'],
  ['club','product','league','deal_stage','channel','subscription'],
  'looker',
  '4753cc0c-0d98-4c17-9cd8-2595f8d73698',
  '3hMgF',
  'donut',
  NULL, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- 10. Subscription Penetration by Club
(
  'rev_subscription_penetration_by_club',
  'revenue',
  'Subscription Penetration by Club',
  'Subscription penetration across clubs.',
  ['subscription','club','penetration'],
  ['product_category','subscription','product'],
  'looker',
  'a5195d07-98c5-43d3-acf7-a6f16244a11f',
  '3hMgF',
  'bar',
  NULL, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- 11. Subscription Product Composition
(
  'rev_subscription_product_composition',
  'revenue',
  'Subscription Product Composition',
  'Products included within subscriptions.',
  ['subscription','product','composition'],
  ['club','product','channel'],
  'looker',
  'a7689688-82dd-4bd3-a752-4d9d5fe73118',
  '3hMgF',
  'table',
  NULL, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
);

INSERT INTO metadata.chart_catalog (
  chart_id, project_name, chart_title, description, tags, allowed_filters,
  render_engine, looker_report_id, looker_page_id,
  default_viz_type, sql_template, is_active,
  created_at, updated_at
)
VALUES
-- 1. Master
(
  'sprt_master_dashboard',
  'sports',
  'Elite Intelligence Dashboard',
  'Elite club intelligence overview.',
  ['sports','dashboard','overview'],
  ['club','season','customer_type','subscription_tier'],
  'looker',
  '19797420-8743-415d-a926-8727b12e04ce',
  '0mrgF',
  'dashboard',
  NULL, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- 2. Shots on Target
(
  'sprt_shots_on_target_trend',
  'sports',
  'Shots on Target Over Seasons',
  'Shots on target trend by season.',
  ['shots','trend'],
  ['season','customer_type','subscription_tier'],
  'looker',
  '383baab1-e704-43ef-b247-f7a173b28462',
  '0mrgF',
  'line',
  NULL, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- 3. Total Goals Over Seasons
(
  'sprt_total_goals_trend',
  'sports',
  'Total Goals Over Seasons',
  'Total goals scored over seasons.',
  ['goals','trend'],
  ['club','season'],
  'looker',
  '9078f4c0-f5ed-4554-8042-f53dc401f260',
  '0mrgF',
  'line',
  NULL, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- 4. Goals vs xG
(
  'sprt_goals_vs_xg',
  'sports',
  'Goals vs xG',
  'Actual goals vs expected goals.',
  ['goals','xg','efficiency'],
  ['club','season'],
  'looker',
  'd09515be-f1ad-4387-960e-9f0afa336b47',
  '0mrgF',
  'scatter',
  NULL, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- 5. Goals Conversion %
(
  'sprt_goal_conversion_pct',
  'sports',
  'Goals Conversion Percentage',
  'Shot-to-goal conversion rate.',
  ['goals','conversion'],
  ['season','subscription_tier'],
  'looker',
  'fb49df8b-3be5-4e37-a266-a1bad2895133',
  '0mrgF',
  'bar',
  NULL, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- 6. Conceded vs xGC
(
  'sprt_conceded_vs_xgc',
  'sports',
  'Conceded Goals vs xGC',
  'Goals conceded vs expected goals conceded.',
  ['defense','xgc'],
  ['club','season','customer_type','subscription_tier'],
  'looker',
  '116f3969-d51b-45d8-8563-03d88a776b36',
  '0mrgF',
  'scatter',
  NULL, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- 7. Defensive Discipline
(
  'sprt_defensive_discipline',
  'sports',
  'Defensive Discipline',
  'Fouls, cards, and defensive discipline.',
  ['defense','discipline'],
  ['season','customer_type'],
  'looker',
  'afd85ba8-617a-44b6-b288-9576316083dc',
  '0mrgF',
  'bar',
  NULL, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
),

-- 8. Defensive Seasonal Profile
(
  'sprt_defensive_seasonal_profile',
  'sports',
  'Defensive Seasonal Profile',
  'Radar view of defensive metrics.',
  ['defense','profile'],
  ['season','customer_type'],
  'looker',
  '38e489b4-851f-423c-9501-a20eea44d55d',
  '0mrgF',
  'radar',
  NULL, TRUE, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
);
