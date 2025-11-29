CREATE OR REPLACE TABLE sports.mart_player_season_agg AS
WITH pos_norm AS (
  SELECT
    dp.player_name,
    dp.club_name,
    dp.position_role AS position_role_original,
    CASE
      WHEN dp.position_role IN ('GK','RB','CB','LB','DM','CM','AM','RW','LW','CF') THEN dp.position_role
      WHEN dp.position_role = 'RB/CB' THEN 'CB'
      WHEN dp.position_role = 'CB/LB' THEN 'CB'
      WHEN dp.position_role = 'LW/CF' THEN 'LW'
      WHEN dp.position_role = 'LW/FW' THEN 'LW'
      WHEN dp.position_role = 'CM/MID' THEN 'CM'
      WHEN dp.position_role = 'AM/FW' THEN 'AM'
      WHEN dp.position_role = 'CF/FW' THEN 'CF'
      WHEN dp.position_role = 'CB/FB' THEN 'CB'
      WHEN dp.position_role = 'LW/FWD' THEN 'LW'
      WHEN dp.position_role = 'RW/FWD' THEN 'RW'
      ELSE dp.position_role
    END AS position_role_normalized,
    CASE
      WHEN dp.position_role IN ('GK') THEN 'GK'
      WHEN dp.position_role = 'RB/CB' THEN 'RB'
      WHEN dp.position_role = 'CB/LB' THEN 'LB'
      WHEN dp.position_role = 'LW/CF' THEN 'CF'
      WHEN dp.position_role = 'LW/FW' THEN 'FW'
      WHEN dp.position_role = 'CM/MID' THEN 'MID'
      WHEN dp.position_role = 'AM/FW' THEN 'FW'
      WHEN dp.position_role = 'CF/FW' THEN 'FW'
      WHEN dp.position_role = 'CB/FB' THEN 'FB'
      WHEN dp.position_role = 'LW/FWD' THEN 'FWD'
      WHEN dp.position_role = 'RW/FWD' THEN 'FWD'
      ELSE NULL
    END AS position_role_secondary,
    CASE
      WHEN dp.position_role IN ('GK') THEN 'GK'
      WHEN dp.position_role IN ('RB','CB','LB','RB/CB','CB/LB','CB/FB') THEN 'DEF'
      WHEN dp.position_role IN ('DM','CM','AM','AM/FWD','CM/MID') THEN 'MID'
      WHEN dp.position_role IN ('RW','LW','CF','LW/CF','LW/FW','CF/FW','LW/FWD','RW/FWD') THEN 'FWD'
      ELSE 'MID'
    END AS position_group_normalized,
    dp.age,
    dp.preferred_foot,
    dp.market_value_eur
  FROM sports.dim_players dp
)

SELECT
  fps.player_name,
  fps.club_name,
  pn.position_role_normalized as position_role_primary,
  pn.position_role_secondary,
  pn.position_group_normalized as position_group,
  pn.age,
  pn.preferred_foot,
  pn.market_value_eur,
  fps.season,
  COUNT(*) AS matches_played,
  SUM(minutes_played) AS total_minutes,
  SUM(goals) AS total_goals,
  SUM(assists) AS total_assists,
  SUM(shots) AS total_shots,
  SUM(shots_on_target) AS total_sot,
  SUM(xg) AS total_xg,
  SUM(xa) AS total_xa,
  SUM(passes) AS total_passes,
  AVG(pass_accuracy) AS avg_pass_accuracy,
  SUM(tackles) AS total_tackles,
  SUM(interceptions) AS total_interceptions,
  SUM(dribbles) AS total_dribbles,
  SUM(dribbles_completed) AS total_dribbles_completed,
  SUM(sprints) AS total_sprints,
  SUM(distance_km) AS total_distance_km,
  AVG(top_speed_kmh) AS avg_top_speed_kmh,
  AVG(rating) AS avg_rating,
  STDDEV(rating) AS rating_stddev
FROM sports.fact_player_match_stats fps
JOIN pos_norm pn
  ON fps.player_name = pn.player_name
  AND fps.club_name = pn.club_name
GROUP BY 1,2,3,4,5,6,7,8,9;
