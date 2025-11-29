# End-to-End Sports Analytics: xG, Finishing, Conceding & Tactical Insights

This project demonstrates a complete end-to-end football analytics solution using  
**BigQuery + SQL Modeling + ETL Pipelines + Looker Studio Dashboards.**

It includes match-level data ingestion, data modeling, ETL transformations, aggregated mart tables,  
and a fully designed Elite Club Intelligence Dashboard for tactical performance analysis.

---

## Key Features

### Full Data Modeling (raw → mart)
- Raw tables for match-level stats & club metadata  
- Aggregated match-grain performance mart  
- Season-level mart for club-wide KPIs  
- Attacking metrics: goals, xG, shot volume, conversion efficiency  
- Defensive metrics: goals conceded, xG conceded, defensive ratio  
- Discipline metrics: fouls, cards, aggression markers  
- Possession trends & control indicators  

### SQL Transformations (ETL)
All SQL scripts used to create:
- **mart_player_season_agg**  
- **mart_player_scout_agg*  
- **mart_club_match_agg**  

### Looker Studio Dashboard
Interactive dashboard including:
- Filters + KPIs  
- Rating trend  
- Goals scored over seasons  
- xG progression  
- Goals vs xG finishing realization  
- Finishing efficiency vs EPL benchmark  
- Defensive conceding vs expected conceded  
- Discipline & possession combo chart  
- Season comparison table with bar indicators  


---

## Dashboard Preview

Images of each section:

| Dashboard Section | Preview |
|------------------|----------|
| Filters| images/Filter Overview.png |
| KPI + Goals | images/KPI Goals.png |
| xg + Goals + Coversion | images/xg Goals.png |
| xG Conceded | images/Defense xG_C.png |
| Defensive Profile| images/Defense Profile.png |

---

## Live Dashboard
https://lookerstudio.google.com/reporting/19797420-8743-415d-a926-8727b12e04ce

---

## Project Structure

Organized, modular, and reproducible sports analytics workflow:

### datasets/
- dim_club_subscription.csv  
- dim_players.csv 
- fact_match_all.csv 
- fact_player_match_stats.csv  
 

### etl/  
Data load & transformation SQL:
- sports.mart_club_season_agg__insert.sql  
- sports.mart_player_scout_agg__insert.sql  
- sports.mart_player_season_agg__insert.sql  
- error_updates.sql  (data cleaning)

### docs/  
Project documentation:
- DataOrb_Elite_Club_Intelligence (PDF)  
- Elite Intelligence Arsenal Executive Summary (PDF)  


### README.md  
Full project explanation, setup steps & dashboard preview images.

---

