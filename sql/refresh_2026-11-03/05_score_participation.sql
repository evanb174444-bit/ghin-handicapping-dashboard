-- November 3 full-refresh package. Export ALL rows as score_participation_2026-11-03.csv.
-- Export as score_participation_2026-11-03.csv. Current active golfers; YTD scores through execution. One row per population/golfer; populations may overlap. One score-table aggregation.
-- Prepared for November 3, 2026. SELECT only; not database-validated.
WITH active_golfers AS (
    SELECT DISTINCT m.golfer_id,
        CASE WHEN a.id = 237 THEN 'trial' ELSE 'non_trial' END AS population
    FROM public.golfer_clubs m
    JOIN public.clubs c ON c.id = m.club_id
    JOIN public.golf_associations a ON a.id = c.golf_association_id
    WHERE m.status = 'Active'
      AND m.golfer_id IS NOT NULL
      AND c.is_test = FALSE
      AND a.is_test = FALSE
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
SELECT statement_timestamp() AS extracted_at,
       current_database() AS source_database,
       current_setting('TimeZone') AS reporting_timezone,
       TIMESTAMP '2026-01-01' AS score_period_start,
       statement_timestamp() AS score_period_end_exclusive,
       a.population, a.golfer_id,
       COALESCE(s.ytd_score_count, 0) AS ytd_score_count
FROM active_golfers a
LEFT JOIN score_counts s ON s.golfer_id = a.golfer_id;
