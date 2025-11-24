INSERT INTO revenue.stg_revenue_subscriptions (
  subscription_id,
  deal_id,
  product_key,
  price_usd,
  start_date,
  end_date,
  status
)
SELECT
  TRIM(subscription_id) AS subscription_id,
  TRIM(deal_id) AS deal_id,
  TRIM(plan_id) AS product_key,
  SAFE_CAST(mrr_usd AS NUMERIC) AS price_usd,
  CAST(start_date AS DATE) AS start_date,
  CAST(end_date AS DATE) AS end_date,
  LOWER(TRIM(status)) AS status
FROM revenue.revenue_subscriptions;
