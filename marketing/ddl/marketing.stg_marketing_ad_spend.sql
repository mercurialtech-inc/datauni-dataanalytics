CREATE OR REPLACE TABLE marketing.stg_marketing_ad_spend (
    campaign_id INT64,
    spend_date DATE,
    channel STRING,
    impressions INT64,
    clicks INT64,
    spend_usd FLOAT64,
    ctr FLOAT64,     -- clicks / impressions
    cpc FLOAT64,     -- spend / clicks
    cpm FLOAT64      -- spend per 1000 impressions
);
