-- Current active trial membership population (association 237).
-- Counts all qualifying YTD scores for these golfers, not only scores flagged is_trial.
-- This does not measure every trial started this year or posting only during trial dates.
-- Export ALL rows with headers as active_trial_golfer_ytd_scores_2026.csv.
-- Local processing only: golfer IDs must not be published in the dashboard.
-- One row per currently active trial-association golfer, including zero qualifying scores.
-- Scores and active eligibility use the same statement snapshot.
-- Score timestamps use the database session timezone, consistent with prior exports.
WITH active_golfers AS (
    SELECT DISTINCT m.golfer_id
    FROM public.golfer_clubs m
    JOIN public.clubs c ON c.id = m.club_id
    JOIN public.golf_associations a ON a.id = c.golf_association_id
    WHERE m.status = 'Active'
      AND m.golfer_id IS NOT NULL
      AND c.is_test = FALSE
      AND a.is_test = FALSE
      AND a.id = 237
),
score_counts AS (
    SELECT golfer_id, COUNT(*) AS ytd_score_count
    FROM public.scores
    WHERE created_at >= TIMESTAMP '2026-01-01'
      AND created_at < statement_timestamp()::timestamp
      AND deleted = FALSE
      AND penalty IS NOT TRUE
    GROUP BY golfer_id
)
SELECT a.golfer_id,
       COALESCE(s.ytd_score_count, 0) AS ytd_score_count
FROM active_golfers a
LEFT JOIN score_counts s ON s.golfer_id = a.golfer_id;
