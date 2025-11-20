# End-to-End Marketing Analytics: Spend, Leads, CAC & Funnel Insights

This project demonstrates a complete end-to-end marketing analytics solution using  
**BigQuery + SQL Modeling + ETL Pipelines + Looker Studio Dashboards.**

It includes data ingestion, data modeling, ETL transformations, a consolidated mart table,  
and a fully designed Marketing Performance Dashboard.

---

## Key Features

### Full Data Modeling (staging → mart)
- Structured staging layers for campaigns, leads, ad spend  
- Consolidated daily-grain performance mart  
- Campaign-level metrics: leads, spend, CAC, lead status, funnel counts  
- Monthly time-series rollups for trend visualizations  

### SQL Transformations (ETL)
All SQL scripts used to create:
- **stg_campaigns**  
- **stg_leads**  
- **stg_ad_spend**  
- **marketing_performance_mart**  
- **mapping tables** (campaign names, channels, lead buckets)

### Looker Studio Dashboard
Interactive dashboard including:
- Filters + KPIs  
- Campaign performance  
- Lead quality table + score bar  
- Funnel breakdown  
- Monthly trend (spend, leads, CAC)  
- Campaign efficiency scatter plot  

A public version of the dashboard is available below.

---

## Dashboard Preview

Images of each section:

| Dashboard Section | Preview |
|------------------|----------|
| Filters + KPIs | images/KPI.png |
| Campaign Overview | images/Campaign.png |
| Lead Quality | images/Lead Quality.png |
| Funnel Breakdown | images/Funnel Breakdown.png |
| Monthly Trend | images/Monthly Trend.png |
| Campaign Efficiency | images/Campaign Efficiency.png |

---

## Live Dashboard
https://lookerstudio.google.com/reporting/d32d1831-28ad-4826-abbd-16528cdcd557

---

## 📁 Project Structure
marketing/
│
├── datasets/
│     ├── marketing_campaigns.csv
│     ├── marketing_leads.csv
│     └── ad_spend.csv
│     └── campaign_name_map.csv
│
├── ddl/
│     ├── marketing.mart_marketing_performance.sql
│     ├── marketing.mart_marketing_performance_channel.sql
│     └── marketing.mart_marketing_performance_consolidated.sql
│     └── marketing.stg_campaign_name_map.sql
│     └── marketing.stg_marketing_ad_spend.sql
│     └── marketing.stg_marketing_campaigns.sql
│     └── marketing.stg_marketing_leads.sql
│
├── docs/
│     ├── Marketing Performance Executive Summary.pdf
│     └── DataOrb_Marketing_Dashboard.pdf
│
├── etl/
│     ├── marketing.mart_marketing_performance_consolidated__insert.sql
│     ├── marketing.stg_campaign_name_map__insert.sql
│     └── marketing.stg_marketing_ad_spend__insert.sql
│     └── marketing.stg_marketing_campaigns__insert.sql
│     └── marketing.stg_marketing_leads__insert.sql
│
├── images/
│     ├── KPI.png
│     ├── Campaign.png
│     ├── Lead Quality.png
│     ├── Funnel Breakdown.png
│     ├── Monthly Trend.png
│     └── Campaign Efficiency.png
│
│
└── README.md

