CREATE OR REPLACE TABLE marketing.stg_marketing_leads (
    lead_id INT64 NOT NULL,
    club_name STRING,
    contact_email STRING,
    country STRING,
    signup_date DATE,
    channel STRING,
    campaign_id INT64,
    lead_score FLOAT64
);
