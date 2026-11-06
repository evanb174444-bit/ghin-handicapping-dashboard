-- PLAN CHECK ONLY: does not execute the aggregation.
-- All Members only; Regular/Junior coding is not yet verified in this database.
-- January-August 2026, currently active non-test memberships, excluding association 237.
-- Age at extraction. No personal identifiers or exact dates of birth returned.
EXPLAIN (COSTS TRUE, VERBOSE FALSE)
WITH active_golfers AS (
    SELECT m.golfer_id,
        BOOL_OR(a.parent_federation = 'United States Golf Association') AS in_aga,
        BOOL_OR(NULLIF(TRIM(a.parent_federation), '') IS NOT NULL
            AND a.parent_federation <> 'United States Golf Association') AS in_international
    FROM public.golfer_clubs m
    JOIN public.clubs c ON c.id = m.club_id
    JOIN public.golf_associations a ON a.id = c.golf_association_id
    WHERE m.status = 'Active'
      AND m.golfer_id IS NOT NULL
      AND c.is_test = FALSE
      AND a.is_test = FALSE
      AND a.id <> 237
    GROUP BY m.golfer_id
),
ytd_scores AS (
    SELECT s.golfer_id, COUNT(*) AS score_count
    FROM public.scores s
    WHERE s.created_at >= TIMESTAMP '2026-01-01'
      AND s.created_at < TIMESTAMP '2026-09-01'
      AND s.deleted = FALSE
      AND s.penalty IS NOT TRUE
    GROUP BY s.golfer_id
),
golfer_counts AS (
    SELECT a.golfer_id, a.in_aga, a.in_international,
        COALESCE(NULLIF(TRIM(g.gender), ''), 'Unknown') AS gender,
        EXTRACT(YEAR FROM AGE(CURRENT_DATE, g.date_of_birth)) AS age,
        COALESCE(s.score_count, 0) AS score_count
    FROM active_golfers a
    LEFT JOIN public.golfers g ON g.id = a.golfer_id
    LEFT JOIN ytd_scores s ON s.golfer_id = a.golfer_id
),
banded AS (
    SELECT in_aga, in_international, gender, score_count,
        CASE WHEN age IS NULL OR age < 0 OR age > 120 THEN 'Unknown'
             WHEN age < 18 THEN 'Under 18'
             WHEN age < 25 THEN '18-24'
             WHEN age < 35 THEN '25-34'
             WHEN age < 45 THEN '35-44'
             WHEN age < 55 THEN '45-54'
             WHEN age < 65 THEN '55-64'
             WHEN age < 75 THEN '65-74'
             ELSE '75+' END AS age_band,
        CASE WHEN score_count = 0 THEN '0'
             WHEN score_count <= 7 THEN '1-7'
             ELSE '8+' END AS posting_band
    FROM golfer_counts
)
SELECT statement_timestamp() AS extracted_at,
    DATE '2026-01-01' AS score_period_start,
    DATE '2026-08-31' AS score_period_end,
    sc.association_scope, 'all' AS population,
    b.gender, b.age_band, b.posting_band,
    COUNT(*) AS golfer_count,
    SUM(b.score_count) AS scores_in_band
FROM banded b
CROSS JOIN (VALUES ('all'), ('aga'), ('international')) AS sc(association_scope)
WHERE sc.association_scope = 'all'
   OR (sc.association_scope = 'aga' AND b.in_aga)
   OR (sc.association_scope = 'international' AND b.in_international)
GROUP BY sc.association_scope, b.gender, b.age_band, b.posting_band
ORDER BY sc.association_scope, b.gender, b.age_band, b.posting_band;
