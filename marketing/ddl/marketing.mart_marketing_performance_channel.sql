CREATE OR REPLACE TABLE marketing.mart_marketing_performance_channel (
    campaign_id INT64 NOT NULL,
    campaign_name STRING,
    channel STRING,
    lead_count INT64,
    spend_usd_channel FLOAT64,
    cac_usd_channel FLOAT64
);
