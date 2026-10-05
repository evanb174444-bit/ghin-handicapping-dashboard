-- Export as ghin_challenges.csv. One row per challenge; no golfer or score-table joins.
-- Golfer counts are challenge-level counters, not deduplicated across challenges.
SELECT statement_timestamp() AS retrieved_at,
       id AS challenge_id,
       association_id,
       course_id,
       status,
       start_date,
       end_date,
       created_at,
       updated_at,
       no_of_golfers,
       no_of_ranked_golfers,
       no_of_posted_scores
FROM public.challenges
ORDER BY start_date, id;
