CREATE OR REPLACE TABLE marketing.mart_marketing_performance_consolidated (
    campaign_id INT64 NOT NULL,
    campaign_name STRING,
    campaign_channel STRING,
    start_date DATE,
    end_date DATE,

    -- Spend (Aggregated)
    total_spend_usd FLOAT64,
    avg_daily_spend_usd FLOAT64,
    total_impressions INT64,
    total_clicks INT64,
    ctr FLOAT64,
    cpc FLOAT64,
    cpm FLOAT64,
    first_spend_date DATE,
    last_spend_date DATE,

    -- Leads (Aggregated)
    total_leads INT64,
    avg_lead_score FLOAT64,
    new_leads INT64,
    engaged_leads INT64,
    hot_leads INT64,
    first_signup DATE,
    last_signup DATE,

    -- CAC
    cac_usd FLOAT64,

    -- Channel Insights
    top_channel STRING,
    top_channel_leads INT64,

    -- Time Series (Flattened)
    daily_spend_usd FLOAT64,
    daily_impressions INT64,
    daily_clicks INT64,
    daily_leads INT64,
    daily_date DATE,

    -- Metadata
    data_refreshed_at TIMESTAMP
);
