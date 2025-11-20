CREATE OR REPLACE TABLE marketing.mart_marketing_performance (
    campaign_id INT64 NOT NULL,
    campaign_name STRING,
    budget_usd FLOAT64,
    
    total_leads INT64,
    avg_lead_score FLOAT64,
    
    new_leads INT64,
    engaged_leads INT64,
    hot_leads INT64,
    
    first_signup DATE,
    last_signup DATE,
    avg_lead_age_days FLOAT64,
    
    total_spend_usd FLOAT64,
    cac_usd FLOAT64,
    
    data_refreshed_at TIMESTAMP
);
