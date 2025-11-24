CREATE TABLE IF NOT EXISTS revenue.stg_revenue_deals (
  deal_id STRING,
  lead_id INT64,
  club_id STRING,
  campaign_id INT64,
  deal_stage STRING,
  created_at DATE,
  close_date DATE,
  amount_usd NUMERIC,
  is_closed BOOL,
  is_won BOOL
);
