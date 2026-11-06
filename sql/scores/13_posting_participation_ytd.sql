-- Export as score_posting_participation_2026.csv.
-- Aggregate output only. Membership and demographics are current at extraction.
-- Scores use created_at, matching the current dashboard. Excludes trials association.
-- Each scope/population deduplicates golfers independently; do not sum populations/scopes.
WITH params AS (
    SELECT DATE '2026-01-01' AS period_start,
           DATE '2026-09-01' AS period_end_exclusive
),
eligible AS (
    SELECT DISTINCT m.golfer_id, m.usga_membership_type, a.parent_federation
    FROM public.v_golfer_clubs m
    JOIN public.v_clubs c ON c.club_id = m.club_id
    JOIN public.v_associations a ON a.association_id = c.association_id
    WHERE m.status = 'Active' AND m.golfer_id IS NOT NULL
      AND c.is_test = 'No' AND a.is_test = 'No' AND a.association_id <> 237
),
cohorts AS (
    SELECT DISTINCT e.golfer_id, s.association_scope, p.population
    FROM eligible e
    CROSS JOIN (VALUES ('all'), ('aga'), ('international')) AS s(association_scope)
    CROSS JOIN (VALUES ('all'), ('regular'), ('junior')) AS p(population)
    WHERE (s.association_scope = 'all'
        OR (s.association_scope = 'aga' AND e.parent_federation = 'United States Golf Association')
        OR (s.association_scope = 'international'
            AND NULLIF(TRIM(e.parent_federation), '') IS NOT NULL
            AND e.parent_federation <> 'United States Golf Association'))
      AND (p.population = 'all'
        OR (p.population = 'regular' AND e.usga_membership_type = 'Standard')
        OR (p.population = 'junior' AND e.usga_membership_type = 'Junior'))
),
demographics AS (
    SELECT g.golfer_id,
        CASE WHEN COUNT(DISTINCT NULLIF(TRIM(g.gender), '')) = 1
             THEN MIN(NULLIF(TRIM(g.gender), '')) ELSE 'Unknown' END AS gender,
        CASE WHEN COUNT(DISTINCT g.age) = 1 THEN MIN(g.age) END AS age
    FROM public.v_golfers g
    WHERE EXISTS (SELECT 1 FROM eligible e WHERE e.golfer_id = g.golfer_id)
    GROUP BY g.golfer_id
),
score_counts AS (
    SELECT s.golfer_id, COUNT(*) AS score_count
    FROM public.scores s CROSS JOIN params p
    WHERE s.created_at >= p.period_start AND s.created_at < p.period_end_exclusive
      AND s.deleted = FALSE AND s.penalty IS NOT TRUE
      AND EXISTS (SELECT 1 FROM eligible e WHERE e.golfer_id = s.golfer_id)
    GROUP BY s.golfer_id
),
classified AS (
    SELECT c.association_scope, c.population, COALESCE(d.gender, 'Unknown') AS gender,
        CASE WHEN d.age IS NULL OR d.age < 0 OR d.age > 120 THEN 'Unknown'
             WHEN d.age < 18 THEN 'Under 18' WHEN d.age < 25 THEN '18-24'
             WHEN d.age < 35 THEN '25-34' WHEN d.age < 45 THEN '35-44'
             WHEN d.age < 55 THEN '45-54' WHEN d.age < 65 THEN '55-64'
             WHEN d.age < 75 THEN '65-74' ELSE '75+' END AS age_band,
        CASE WHEN COALESCE(s.score_count, 0) = 0 THEN '0'
             WHEN s.score_count <= 7 THEN '1-7' ELSE '8+' END AS posting_band,
        COALESCE(s.score_count, 0) AS score_count
    FROM cohorts c
    LEFT JOIN demographics d ON d.golfer_id = c.golfer_id
    LEFT JOIN score_counts s ON s.golfer_id = c.golfer_id
)
SELECT statement_timestamp() AS extracted_at,
    p.period_start AS score_period_start, p.period_end_exclusive - 1 AS score_period_end,
    c.association_scope, c.population, c.gender, c.age_band, c.posting_band,
    COUNT(*) AS golfer_count, SUM(c.score_count) AS scores_in_band
FROM classified c CROSS JOIN params p
GROUP BY p.period_start, p.period_end_exclusive,
    c.association_scope, c.population, c.gender, c.age_band, c.posting_band
ORDER BY c.association_scope, c.population, c.gender, c.age_band, c.posting_band;
