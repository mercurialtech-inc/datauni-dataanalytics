CREATE OR REPLACE TABLE marketing.stg_marketing_campaigns (
    campaign_id INT64 NOT NULL,
    name STRING,
    channel STRING,
    start_date DATE,
    end_date DATE,
    budget_usd FLOAT64
);
