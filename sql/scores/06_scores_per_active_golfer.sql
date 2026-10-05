-- Export as score_averages_by_member_type_2026.csv.
-- Current active primary-club cohort; not historical membership at August 31.
-- Zero-posting golfers included. Scores and denominator use exactly the same cohort.
WITH eligible AS (
    SELECT DISTINCT
        g.golfer_id,
        m.usga_membership_type,
        a.parent_federation
    FROM public.v_golfers g
    JOIN public.v_clubs c ON c.club_id = g.primary_club_id
    JOIN public.v_associations a ON a.association_id = c.association_id
    JOIN public.v_golfer_clubs m
        ON m.golfer_id = g.golfer_id
       AND m.club_id = g.primary_club_id
    WHERE m.status = 'Active'
      AND m.usga_membership_type IN ('Standard', 'Junior')
      AND c.is_test = 'No'
      AND a.is_test = 'No'
      AND a.association_id <> 237
),
cohorts AS (
    SELECT DISTINCT
        scope.association_scope,
        CASE WHEN e.usga_membership_type = 'Standard'
             THEN 'regular' ELSE 'junior' END AS population,
        e.golfer_id
    FROM eligible e
    CROSS JOIN (VALUES ('all'), ('aga'), ('international'))
        AS scope(association_scope)
    WHERE scope.association_scope = 'all'
       OR (scope.association_scope = 'aga'
           AND e.parent_federation = 'United States Golf Association')
       OR (scope.association_scope = 'international'
           AND NULLIF(TRIM(e.parent_federation), '') IS NOT NULL
           AND e.parent_federation <> 'United States Golf Association')
),
scores_by_golfer AS (
    SELECT golfer_id, COUNT(*) AS score_count
    FROM public.scores
    WHERE created_at >= TIMESTAMP '2026-01-01'
      AND created_at < TIMESTAMP '2026-09-01'
      AND deleted = FALSE
      AND penalty IS NOT TRUE
    GROUP BY golfer_id
)
SELECT
    statement_timestamp() AS extracted_at,
    current_database() AS source_database,
    DATE '2026-01-01' AS score_period_start,
    DATE '2026-08-31' AS score_period_end,
    c.association_scope,
    c.population,
    COUNT(*) AS unique_active_golfers,
    COUNT(*) FILTER (WHERE COALESCE(s.score_count, 0) = 0)
        AS golfers_with_zero_scores,
    SUM(COALESCE(s.score_count, 0)) AS cohort_score_count,
    ROUND(SUM(COALESCE(s.score_count, 0))::numeric / COUNT(*), 2)
        AS scores_per_golfer
FROM cohorts c
LEFT JOIN scores_by_golfer s ON s.golfer_id = c.golfer_id
GROUP BY c.association_scope, c.population
ORDER BY c.association_scope, c.population;
