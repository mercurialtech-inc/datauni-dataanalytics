INSERT INTO revenue.mart_revenue (
  order_id,
  deal_id,
  lead_id,
  club_id,

  order_product_key,
  order_product_name,
  order_product_category,
  order_product_type,
  order_unit_price_usd,
  order_revenue_usd,

  subscription_id,
  subscription_product_key,
  subscription_product_name,
  subscription_product_category,
  subscription_product_type,
  subscription_price_usd,
  subscription_start_date,
  subscription_end_date,
  subscription_status,

  order_date,
  quantity,

  deal_stage,
  deal_created_at,
  deal_close_date,
  deal_amount_usd,
  deal_is_closed,
  deal_is_won,

  club_name_clean,
  club_name_raw,
  city,
  league,
  tier,
  is_premier_league,

  campaign_id,
  channel,
  country,
  lead_score,
  signup_date
)
SELECT
  o.order_id,
  o.deal_id,
  d.lead_id,
  d.club_id,

  -- Order product dims
  o.product_key AS order_product_key,
  p1.product_name AS order_product_name,
  p1.product_category AS order_product_category,
  p1.product_type AS order_product_type,
  o.unit_price_usd AS order_unit_price_usd,
  o.revenue_usd AS order_revenue_usd,

  -- Subscription + subscription-product dims
  s.subscription_id,
  s.product_key AS subscription_product_key,
  p2.product_name AS subscription_product_name,
  p2.product_category AS subscription_product_category,
  p2.product_type AS subscription_product_type,
  s.price_usd AS subscription_price_usd,
  s.start_date AS subscription_start_date,
  s.end_date AS subscription_end_date,
  s.status AS subscription_status,

  -- order attributes
  o.order_date,
  o.quantity,

  -- deal level
  d.deal_stage,
  d.created_at AS deal_created_at,
  d.close_date AS deal_close_date,
  d.amount_usd AS deal_amount_usd,
  d.is_closed AS deal_is_closed,
  d.is_won AS deal_is_won,

  -- club dim
  c.club_name_clean,
  c.club_name_raw,
  c.city,
  c.league,
  c.tier,
  c.is_premier_league,

  -- marketing dim
  m.campaign_id,
  m.channel,
  m.country,
  SAFE_CAST(m.lead_score AS INT64) AS lead_score,
  m.signup_date
FROM revenue.stg_revenue_orders o
LEFT JOIN revenue.stg_revenue_deals d
  ON o.deal_id = d.deal_id
LEFT JOIN revenue.stg_revenue_subscriptions s
  ON o.deal_id = s.deal_id
LEFT JOIN revenue.stg_revenue_product p1
  ON o.product_key = p1.product_key
LEFT JOIN revenue.stg_revenue_product p2
  ON s.product_key = p2.product_key
LEFT JOIN sports.stg_dim_club c
  ON d.club_id = c.club_id
LEFT JOIN marketing.stg_marketing_leads m
  ON d.lead_id = m.lead_id;
