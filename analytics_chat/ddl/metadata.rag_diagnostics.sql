CREATE TABLE IF NOT EXISTS `metadata.rag_diagnostics` (
  domain STRING NOT NULL,
  metric_key STRING NOT NULL,                     -- FK → rag_metrics.metric_key
  change_type STRING NOT NULL,                    -- increase | decrease | volatility
  likely_causes ARRAY<STRING>,                    -- Ranked explanations
  checks_to_perform ARRAY<STRING>,                -- chart_ids or metric_keys
  exec_friendly_summary STRING,                   -- 3–5 sentence narrative
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
