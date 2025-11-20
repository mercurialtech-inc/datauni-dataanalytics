CREATE OR REPLACE TABLE marketing.stg_campaign_name_map AS
SELECT
  CAST(campaign_id AS INT64) AS campaign_id,
  short_name
FROM marketing.marketing_campaign_name_map;