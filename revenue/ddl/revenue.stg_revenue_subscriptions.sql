CREATE TABLE IF NOT EXISTS revenue.stg_revenue_subscriptions (
  subscription_id STRING,
  deal_id STRING,
  product_key STRING,
  price_usd NUMERIC,
  start_date DATE,
  end_date DATE,
  status STRING
);
