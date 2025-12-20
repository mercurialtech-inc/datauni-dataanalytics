CREATE TABLE IF NOT EXISTS `metadata.rag_metrics` (
  domain STRING NOT NULL,                         -- marketing | revenue | sports
  metric_key STRING NOT NULL,                     -- e.g. mrr, cac, lead_quality
  metric_name STRING NOT NULL,                    -- Human-readable
  definition STRING NOT NULL,                     -- Exec-safe definition
  calculation_summary STRING,                     -- High-level logic (no SQL)
  common_drivers ARRAY<STRING>,                   -- Why it goes up/down
  interpretation_notes STRING,                    -- How PMs/Execs should read it
  related_metrics ARRAY<STRING>,                  -- e.g. churn, subs, pricing
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at);
