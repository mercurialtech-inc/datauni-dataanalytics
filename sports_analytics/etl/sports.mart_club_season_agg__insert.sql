CREATE OR REPLACE TABLE sports.mart_club_match_agg AS
WITH base AS (

  SELECT
    fm.match_id,
    fm.season,
    fm.match_date,
    fm.home_club AS club_name,
    fm.home_goals AS goals_scored,
    fm.away_goals AS goals_conceded,
    fm.home_xg     AS xg,
    fm.away_xg     AS xg_conceded,
    fm.possession_home AS possession,
    fm.shots_home  AS shots,
    fm.shots_on_target_home AS shots_on_target,
    fm.fouls_home  AS fouls,
    fm.yellow_cards_home AS yellow_cards,
    fm.red_cards_home     AS red_cards
  FROM sports.fact_matches fm

  UNION ALL

  SELECT
    fm.match_id,
    fm.season,
    fm.match_date,
    fm.away_club AS club_name,
    fm.away_goals AS goals_scored,
    fm.home_goals AS goals_conceded,
    fm.away_xg     AS xg,
    fm.home_xg     AS xg_conceded,
    fm.possession_away AS possession,
    fm.shots_away  AS shots,
    fm.shots_on_target_away AS shots_on_target,
    fm.fouls_away  AS fouls,
    fm.yellow_cards_away AS yellow_cards,
    fm.red_cards_away     AS red_cards
  FROM sports.fact_matches fm
)

SELECT
  b.*,
  dc.customer_type,
  dc.subscription_tier

FROM base b
LEFT JOIN sports.dim_club_subscription dc
  ON b.club_name = dc.club_name;
