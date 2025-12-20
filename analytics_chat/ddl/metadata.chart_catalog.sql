CREATE OR REPLACE TABLE metadata.chart_catalog (
  chart_id STRING NOT NULL,
  project_name STRING NOT NULL,
  chart_title STRING NOT NULL,
  description STRING,
  tags ARRAY<STRING>,
  allowed_filters ARRAY<STRING>,       -- ["campaign","channel"], ["date"], etc.
  render_engine STRING,                -- "looker", "python", "bigquery"
  looker_report_id STRING,
  looker_page_id STRING,
  default_viz_type STRING,
  sql_template STRING,                 -- optional for RAG, null for Looker
  is_active BOOL DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
