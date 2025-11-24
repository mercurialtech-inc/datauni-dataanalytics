INSERT INTO revenue.stg_revenue_deals (
  deal_id,
  lead_id,
  club_id,
  campaign_id,
  deal_stage,
  created_at,
  close_date,
  amount_usd,
  is_closed,
  is_won
)
SELECT
  TRIM(deal_id) AS deal_id,
  SAFE_CAST(lead_id AS INT64) AS lead_id,
  TRIM(club_id) AS club_id,
  SAFE_CAST(campaign_id AS INT64) AS campaign_id,
  LOWER(TRIM(deal_stage)) AS deal_stage,
  CAST(created_at as DATE) AS created_at,
  CAST(close_date as DATE) AS close_date,
  SAFE_CAST(amount_usd AS NUMERIC) AS amount_usd,
  SAFE_CAST(is_closed AS BOOL) AS is_closed,
  SAFE_CAST(is_won AS BOOL) AS is_won
FROM revenue.revenue_deals;
