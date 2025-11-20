INSERT INTO marketing.stg_marketing_leads (
    lead_id,
    club_name,
    contact_email,
    country,
    signup_date,
    channel,
    campaign_id,
    lead_score
)
SELECT
    CAST(lead_id AS INT64) AS lead_id,
    TRIM(club_name) AS club_name,
    TRIM(contact_email) AS contact_email,
    TRIM(country) AS country,
    SAFE_CAST(signup_date AS DATE) AS signup_date,
    TRIM(channel) AS channel,
    CAST(campaign_id AS INT64) AS campaign_id,
    SAFE_CAST(lead_score AS FLOAT64) AS lead_score
FROM marketing.marketing_leads
WHERE lead_id IS NOT NULL
  AND campaign_id IS NOT NULL;
