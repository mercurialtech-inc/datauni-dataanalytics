CREATE TABLE IF NOT EXISTS `metadata.rag_charts` (
  chart_id STRING NOT NULL,                       -- FK → chart_catalog.chart_id
  domain STRING NOT NULL,
  primary_metrics ARRAY<STRING>,                  -- metric_keys
  questions_answered ARRAY<STRING>,               -- Natural language
  when_to_use STRING,                             -- Analytical guidance
  common_followups ARRAY<STRING>,                 -- chart_ids or metric_keys
  caveats STRING,                                 -- Exec guardrails
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
