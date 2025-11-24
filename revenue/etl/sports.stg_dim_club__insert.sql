INSERT INTO sports.stg_dim_club (
  club_id,
  club_name_raw,
  club_name_clean,
  city,
  country,
  league,
  tier,
  is_premier_league
)
SELECT
  TRIM(club_id) AS club_id,
  TRIM(club_name_raw) AS club_name_raw,
  TRIM(club_name_clean) AS club_name_clean,
  TRIM(city) AS city,
  TRIM(country) AS country,
  TRIM(league) AS league,
  tier,
  is_premier_league
FROM sports.dim_club;
