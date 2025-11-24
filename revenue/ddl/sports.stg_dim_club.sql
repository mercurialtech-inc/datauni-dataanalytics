CREATE TABLE IF NOT EXISTS sports.stg_dim_club (
  club_id STRING,
  club_name_raw STRING,
  club_name_clean STRING,
  city STRING,
  country STRING,
  league STRING,
  tier INT64,
  is_premier_league BOOL
);
