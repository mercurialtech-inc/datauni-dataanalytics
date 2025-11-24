INSERT INTO revenue.stg_revenue_product (
  product_key,
  product_name,
  product_category,
  price_usd,
  product_type
)
SELECT
  TRIM(product_key) AS product_key,
  TRIM(product_name) AS product_name,
  TRIM(product_category) AS product_category,
  SAFE_CAST(price_usd AS NUMERIC) AS price_usd,
  LOWER(TRIM(product_type)) AS product_type
FROM revenue.revenue_products;
