CREATE TABLE IF NOT EXISTS revenue.mart_revenue (
  -- Grain & Keys
  order_id STRING,
  deal_id STRING,
  lead_id INT64,
  club_id STRING,

  -- Order Product
  order_product_key STRING,
  order_product_name STRING,
  order_product_category STRING,
  order_product_type STRING,
  order_unit_price_usd NUMERIC,
  order_revenue_usd NUMERIC,

  -- Subscription Product
  subscription_id STRING,
  subscription_product_key STRING,
  subscription_product_name STRING,
  subscription_product_category STRING,
  subscription_product_type STRING,
  subscription_price_usd NUMERIC,
  subscription_start_date DATE,
  subscription_end_date DATE,
  subscription_status STRING,

  -- Order Attributes
  order_date DATE,
  quantity INT64,

  -- Deal Attributes
  deal_stage STRING,
  deal_created_at DATE,
  deal_close_date DATE,
  deal_amount_usd NUMERIC,
  deal_is_closed BOOL,
  deal_is_won BOOL,

  -- Club Attributes
  club_name_clean STRING,
  club_name_raw STRING,
  city STRING,
  league STRING,
  tier INT64,
  is_premier_league BOOL,

  -- Lead Attributes
  campaign_id INT64,
  channel STRING,
  country STRING,
  lead_score INT64,
  signup_date DATE
);
