# End-to-End Revenue Analytics: ARR, MRR, Customer Spend & Product Insights

This project demonstrates a complete end-to-end revenue analytics solution using  
**BigQuery + SQL Modeling + ETL Pipelines + Looker Studio Dashboards.**

It includes data ingestion, data modeling, ETL transformations, a consolidated mart table,  
and a fully designed Revenue Performance Dashboard.

---

## Key Features

### Full Data Modeling (staging → mart)
- Structured staging layers for clubs, deals, orders, subscriptions, and products  
- Consolidated monthly-grain and transaction-grain revenue mart  
- Customer-level metrics: total spend, product mix, MRR, ARR, subscription penetration  
- Product-level revenue attribution and segmentation  
- Revenue trend rollups for forecast and seasonality analysis  

### SQL Transformations (ETL)
All SQL scripts used to create:
- **stg_orders**  
- **stg_subscriptions**  
- **stg_products**  
- **stg_deals**  
- **stg_clubs**  
- **revenue_performance_mart**  
- **product_revenue_mart**  
- **club_revenue_profile**  
- **mapping tables** (product names, plan names, club normalization)

### Looker Studio Dashboard
Interactive dashboard including:
- Filters + KPIs  
- Monthly Revenue Trend (One-Time & Subscription)  
- ARR & MRR indicators  
- Product revenue breakdown  
- Top spending clubs  
- Subscription penetration by club  
- Product adoption visualization  
- Deal funnel representation  

A public version of the dashboard can be added below if deployed.

---

## Dashboard Preview

Images of each section:

| Dashboard Section | Preview |
|------------------|----------|
| Filters + KPIs | images/KPI.png & Filter Overview.png |
| Revenue Product | images/Revenue Product.png |
| One-Time Subs Trend | images/Monthly Trend.png |
| Subscription Penetration | images/Prod Subs Club.png |
| Revenue by Club | images/Revenue Club.png |
| Deal Funnel | images/Subs Product Composition.png |
| Subs Revenue Mix | images/Subscription Mix.png |

## Live Dashboard
https://lookerstudio.google.com/reporting/8363d8ae-bc1f-4060-8d2f-6bdbe6d5e0c8

---

## Project Structure

Organized, modular, and reproducible end-to-end analytics workflow:

### datasets/
- revenue_deals.csv  
- revenue_orders.csv  
- revenue_product_unified.csv  
- revenue_subscriptions.csv  
- sports_dim_club.csv  

### ddl/  
Table creation scripts for all staging & mart layers:
- revenue.stg_revenue_deals.sql  
- revenue.stg_revenue_orders.sql  
- revenue.stg_revenue_product.sql  
- revenue.stg_revenue_subscriptions.sql  
- sports.stg_dim_club.sql  
- revenue.mart_revenue.sql   

### etl/  
Data load & transformation SQL:
- revenue.mart_revenue__insert.sql  
- revenue.stg_revenue_deals__insert.sql  
- revenue.stg_revenue_orders.sql  
- revenue.stg_revenue_product__insert.sql  
- revenue.stg_revenue_subscriptions__insert.sql  
- sports.stg_dim_club__insert.sql  

### docs/  
Project documentation:
- Revenue Performance Executive Summary.pdf  
- DataOrb_Revenue_Dashboard.pdf  

### images/  
Dashboard section visuals:
- Filter Overview.png  
- KPI.png  
- Monthly Trend.png  
- Prod Subs Club.png  
- Revenue Club.png  
- Revenue Product.png  
- Subs Product Composition.png  
- Subscription Mix.png 

### README.md  
Full project explanation, setup steps & dashboard links.

