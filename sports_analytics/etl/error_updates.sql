/*
During data validation I found out that I had made a mistake in id creation and after doing root-cause analysis I figured the query to write 
to make sure the data integrity is maintained
*/

-- 1. Validtion Failure 1
SELECT DISTINCT fps.match_id 
FROM sports.fact_player_match_stats fps 
WHERE fps.match_id NOT IN (SELECT match_id FROM sports.fact_matches);

-- Fix
UPDATE sports.fact_player_match_stats
SET match_id = REPLACE(match_id, 'AST', 'AVL')
WHERE match_id LIKE '%_AST_%';

UPDATE sports.fact_player_match_stats
SET match_id = REPLACE(match_id, 'MAN', 'UNI')
WHERE match_id LIKE '%_MAN_%';

UPDATE sports.fact_player_match_stats SET match_id = 'M_2024_CHE_AVL' WHERE match_id = 'M_2024_CHE_AST';
UPDATE sports.fact_player_match_stats SET match_id = 'M_2024_TOT_AVL' WHERE match_id = 'M_2024_TOT_AST';
UPDATE sports.fact_player_match_stats SET match_id = 'M_2024_LIV_UNI' WHERE match_id = 'M_2024_LIV_MAN';
UPDATE sports.fact_player_match_stats SET match_id = 'M_2024_LIV_AVL' WHERE match_id = 'M_2024_LIV_AST';
UPDATE sports.fact_player_match_stats SET match_id = 'M_2024_ARS_UNI' WHERE match_id = 'M_2024_ARS_MAN';
UPDATE sports.fact_player_match_stats SET match_id = 'M_2024_UNI_AVL' WHERE match_id = 'M_2024_UNI_AST';
UPDATE sports.fact_player_match_stats SET match_id = 'M_2024_TOT_UNI' WHERE match_id = 'M_2024_TOT_MAN';
UPDATE sports.fact_player_match_stats SET match_id = 'M_2024_CHE_UNI' WHERE match_id = 'M_2024_CHE_MAN';
UPDATE sports.fact_player_match_stats SET match_id = 'M_2024_AVL_UNI' WHERE match_id = 'M_2024_AVL_MAN';
UPDATE sports.fact_player_match_stats SET match_id = 'M_2024_ARS_AVL' WHERE match_id = 'M_2024_ARS_AST';
----------------------------------