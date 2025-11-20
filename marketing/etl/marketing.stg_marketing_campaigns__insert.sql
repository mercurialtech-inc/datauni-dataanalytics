INSERT INTO marketing.stg_marketing_campaigns (
    campaign_id,
    name,
    channel,
    start_date,
    end_date,
    budget_usd
)
SELECT
    CAST(campaign_id AS INT64) AS campaign_id,
    TRIM(name) AS name,
    TRIM(channel) AS channel,
    SAFE_CAST(start_date AS DATE) AS start_date,
    SAFE_CAST(end_date AS DATE) AS end_date,
    SAFE_CAST(budget_usd AS FLOAT64) AS budget_usd
FROM marketing.marketing_campaigns
WHERE campaign_id IS NOT NULL;
