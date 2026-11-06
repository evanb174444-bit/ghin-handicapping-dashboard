-- November 2 refresh. Export ALL results as active_golfer_ytd_scores_2026-11-02.csv.
-- Based on sql/scores/17_active_golfer_ytd_score_counts.sql.
-- Current-state queries reflect actual execution time; history may include partial November.
-- Completed-month dashboard activity must stop before 2026-11-01.
-- Export ALL rows with headers as active_golfer_ytd_scores_2026-10-21.csv.
-- Local processing only: golfer IDs must not be published in the dashboard.
-- One row per currently active golfer, including zero qualifying scores.
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
      AND a.id <> 237
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
