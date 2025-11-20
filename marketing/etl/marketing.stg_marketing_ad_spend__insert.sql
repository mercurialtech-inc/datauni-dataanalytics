INSERT INTO marketing.stg_marketing_ad_spend
SELECT
    campaign_id,
    spend_date,
    channel,
    impressions,
    clicks,
    spend_usd,
    
    -- CTR
    SAFE_DIVIDE(clicks, impressions) AS ctr,

    -- CPC
    SAFE_DIVIDE(spend_usd, clicks) AS cpc,

    -- CPM
    SAFE_DIVIDE(spend_usd * 1000, impressions) AS cpm

FROM marketing.marketing_ad_spend
WHERE campaign_id IS NOT NULL
  AND spend_date IS NOT NULL
  AND channel IS NOT NULL;
