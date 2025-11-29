CREATE OR REPLACE TABLE sports.mart_player_scout_agg AS
WITH base AS (
    SELECT
        psa.player_name,
        psa.club_name,
        MAX(psa.position_role_primary) AS position_role,
        MAX(psa.position_group) AS position_group,
        MAX(psa.age) AS age,
        MAX(psa.preferred_foot) AS preferred_foot,
        MAX(psa.market_value_eur) AS market_value_eur,

        SUM(psa.total_goals) AS total_goals,
        SUM(psa.total_assists) AS total_assists,
        SUM(psa.total_xg) AS total_xg,
        SUM(psa.total_xa) AS total_xa,
        SUM(psa.total_minutes) AS total_minutes,
        SUM(psa.matches_played) AS matches_played_total,

        AVG(psa.avg_rating) AS avg_rating_career,
        MAX(psa.avg_top_speed_kmh) AS top_speed_max,
        SUM(psa.total_distance_km) AS distance_total,

        SUM(psa.total_tackles) AS total_tackles,
        SUM(psa.total_interceptions) AS total_interceptions

    FROM sports.mart_player_season_agg psa
    GROUP BY 1,2
)

SELECT
    *,
    SAFE_DIVIDE(total_goals, total_minutes) * 90 AS goals_per_90,
    SAFE_DIVIDE(total_assists, total_minutes) * 90 AS assists_per_90,
    SAFE_DIVIDE(total_xg, total_minutes) * 90 AS xg_per_90,
    SAFE_DIVIDE(total_xa, total_minutes) * 90 AS xa_per_90,

    SAFE_DIVIDE(total_tackles, total_minutes) * 90 AS tackles_per_90,
    SAFE_DIVIDE(total_interceptions, total_minutes) * 90 AS interceptions_per_90,

    CASE 
        WHEN position_group = 'FWD' THEN SAFE_DIVIDE(total_goals, total_xg)
        ELSE NULL
    END AS finishing_efficiency_fwd,

    CASE 
        WHEN position_group = 'MID' THEN SAFE_DIVIDE(total_assists, matches_played_total)
        ELSE NULL
    END AS creative_index_mid,

    CASE 
        WHEN position_group = 'DEF' THEN 
            (SAFE_DIVIDE(total_tackles, total_minutes)*90 + SAFE_DIVIDE(total_interceptions, total_minutes)*90) / 2
        ELSE NULL
    END AS defensive_index_def,

    SAFE_DIVIDE(market_value_eur, avg_rating_career) AS value_per_rating,

    (top_speed_max * 0.6) + (distance_total / 200 * 0.4) AS athletic_index

FROM base;
