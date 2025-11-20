CREATE OR REPLACE TABLE marketing.mart_marketing_performance_consolidated AS
WITH funnel AS (
    SELECT
        l.campaign_id,
        l.channel,
        l.lead_score,
        l.signup_date,
        CASE
            WHEN l.lead_score < 40 THEN 'New'
            WHEN l.lead_score < 70 THEN 'Engaged'
            ELSE 'Hot'
        END AS lead_status
    FROM marketing.stg_marketing_leads l
),

daily_leads AS (
    SELECT
        campaign_id,
        signup_date AS daily_date,
        COUNT(*) AS daily_leads
    FROM funnel
    GROUP BY campaign_id, daily_date
),

daily_spend AS (
    SELECT
        campaign_id,
        spend_date AS daily_date,
        SUM(spend_usd) AS daily_spend_usd,
        SUM(impressions) AS daily_impressions,
        SUM(clicks) AS daily_clicks
    FROM marketing.stg_marketing_ad_spend
    GROUP BY campaign_id, daily_date
),

-- union all daily dates so no loss of rows
all_dates AS (
    SELECT campaign_id, daily_date FROM daily_spend
    UNION DISTINCT
    SELECT campaign_id, daily_date FROM daily_leads
),

-- merge spend + leads (1 row per campaign/day)
final_daily AS (
    SELECT
        d.campaign_id,
        d.daily_date,
        COALESCE(ds.daily_spend_usd, 0) AS daily_spend_usd,
        COALESCE(ds.daily_impressions, 0) AS daily_impressions,
        COALESCE(ds.daily_clicks, 0) AS daily_clicks,
        COALESCE(dl.daily_leads, 0) AS daily_leads
    FROM all_dates d
    LEFT JOIN daily_spend ds 
        ON d.campaign_id = ds.campaign_id
       AND d.daily_date = ds.daily_date
    LEFT JOIN daily_leads dl 
        ON d.campaign_id = dl.campaign_id
       AND d.daily_date = dl.daily_date
),

-- aggregated leads per campaign
aggregated_leads AS (
    SELECT
        campaign_id,
        COUNT(*) AS total_leads,
        AVG(lead_score) AS avg_lead_score,
        COUNTIF(lead_status = 'New') AS new_leads,
        COUNTIF(lead_status = 'Engaged') AS engaged_leads,
        COUNTIF(lead_status = 'Hot') AS hot_leads,
        MIN(signup_date) AS first_signup,
        MAX(signup_date) AS last_signup
    FROM funnel
    GROUP BY campaign_id
),

-- aggregated spend per campaign
aggregated_spend AS (
    SELECT
        campaign_id,
        SUM(daily_spend_usd) AS total_spend_usd,
        AVG(daily_spend_usd) AS avg_daily_spend_usd,
        SUM(daily_impressions) AS total_impressions,
        SUM(daily_clicks) AS total_clicks,
        SAFE_DIVIDE(SUM(daily_clicks), SUM(daily_impressions)) AS ctr,
        SAFE_DIVIDE(SUM(daily_spend_usd), SUM(daily_clicks)) AS cpc,
        SAFE_DIVIDE(SUM(daily_spend_usd)*1000, SUM(daily_impressions)) AS cpm,
        MIN(daily_date) AS first_spend_date,
        MAX(daily_date) AS last_spend_date
    FROM final_daily
    GROUP BY campaign_id
),

-- top channel per campaign
channel_summary AS (
    SELECT
        campaign_id,
        channel,
        COUNT(*) AS channel_leads,
        ROW_NUMBER() OVER (PARTITION BY campaign_id ORDER BY COUNT(*) DESC) AS rn
    FROM funnel
    GROUP BY campaign_id, channel
)

-- FINAL SELECT: 1 ROW PER (campaign, daily_date)
SELECT
    c.campaign_id,
    m.short_name AS campaign_name,
    c.channel AS campaign_channel,
    c.start_date,
    c.end_date,

    -- daily grain fields
    fd.daily_date,
    fd.daily_spend_usd,
    fd.daily_impressions,
    fd.daily_clicks,
    fd.daily_leads,

    -- aggregated spend
    s.total_spend_usd,
    s.avg_daily_spend_usd,
    s.total_impressions,
    s.total_clicks,
    s.ctr,
    s.cpc,
    s.cpm,
    s.first_spend_date,
    s.last_spend_date,

    -- aggregated leads
    l.total_leads,
    l.avg_lead_score,
    l.new_leads,
    l.engaged_leads,
    l.hot_leads,
    l.first_signup,
    l.last_signup,

    -- CAC
    SAFE_DIVIDE(s.total_spend_usd, NULLIF(l.total_leads, 0)) AS cac_usd,

    -- top channel
    cs.channel AS top_channel,
    cs.channel_leads AS top_channel_leads,

    CURRENT_TIMESTAMP() AS data_refreshed_at

FROM marketing.stg_marketing_campaigns c
LEFT JOIN final_daily fd ON c.campaign_id = fd.campaign_id
LEFT JOIN aggregated_spend s ON c.campaign_id = s.campaign_id
LEFT JOIN aggregated_leads l ON c.campaign_id = l.campaign_id
LEFT JOIN marketing.stg_campaign_name_map m
  ON c.campaign_id = m.campaign_id
LEFT JOIN channel_summary cs 
       ON c.campaign_id = cs.campaign_id 
      AND cs.rn = 1

ORDER BY c.campaign_id, fd.daily_date;
