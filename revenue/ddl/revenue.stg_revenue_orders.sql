CREATE TABLE IF NOT EXISTS revenue.stg_revenue_orders (
  order_id STRING,
  deal_id STRING,
  product_key STRING,
  quantity INT64,
  unit_price_usd NUMERIC,
  revenue_usd NUMERIC,
  order_date DATE
);
