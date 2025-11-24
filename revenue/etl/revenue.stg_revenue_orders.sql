INSERT INTO revenue.stg_revenue_orders (
  order_id,
  deal_id,
  product_key,
  quantity,
  unit_price_usd,
  revenue_usd,
  order_date
)
SELECT
  TRIM(order_id) AS order_id,
  TRIM(deal_id) AS deal_id,
  TRIM(product_id) AS product_key,
  SAFE_CAST(quantity AS INT64) AS quantity,
  SAFE_CAST(unit_price_usd AS NUMERIC) AS unit_price_usd,
  SAFE_CAST(revenue_usd AS NUMERIC) AS revenue_usd,
  CAST(order_date AS DATE) AS order_date
FROM revenue.revenue_orders;
