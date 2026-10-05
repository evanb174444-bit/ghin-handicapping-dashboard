-- Export as score_posting_bands_2026.csv.
-- Current active Regular/Junior memberships, including zero posters.
-- Each golfer counts once per scope/population, regardless of membership count.
-- A golfer with both membership types appears in both populations.
-- Association scope follows active membership affiliation, not residence.
-- Scores cover January-August 2026; membership eligibility is current at export.
WITH eligible AS (
    SELECT DISTINCT
        m.golfer_id,
        CASE WHEN m.usga_membership_type = 'Standard'
             THEN 'regular' ELSE 'junior' END AS population,
        a.parent_federation
    FROM public.v_golfer_clubs m
    JOIN public.v_clubs c ON c.club_id = m.club_id
    JOIN public.v_associations a ON a.association_id = c.association_id
    WHERE m.status = 'Active'
      AND m.usga_membership_type IN ('Standard', 'Junior')
      AND m.golfer_id IS NOT NULL
      AND c.is_test = 'No'
      AND a.is_test = 'No'
      AND a.association_id <> 237
),
cohorts AS (
    SELECT DISTINCT s.association_scope, e.population, e.golfer_id
    FROM eligible e
    CROSS JOIN (VALUES ('all'), ('aga'), ('international'))
        AS s(association_scope)
    WHERE s.association_scope = 'all'
       OR (s.association_scope = 'aga'
           AND e.parent_federation = 'United States Golf Association')
       OR (s.association_scope = 'international'
           AND NULLIF(TRIM(e.parent_federation), '') IS NOT NULL
           AND e.parent_federation <> 'United States Golf Association')
),
scores_by_golfer AS (
    SELECT golfer_id, COUNT(*) AS score_count
    FROM public.scores
    WHERE created_at >= TIMESTAMP '2026-01-01'
      AND created_at <  TIMESTAMP '2026-09-01'
      AND deleted = FALSE
      AND penalty IS NOT TRUE
    GROUP BY golfer_id
),
banded AS (
    SELECT c.association_scope, c.population,
        COALESCE(s.score_count, 0) AS score_count,
        CASE
            WHEN s.score_count >= 50 THEN 1
            WHEN s.score_count >= 25 THEN 2
            WHEN s.score_count >= 10 THEN 3
            WHEN s.score_count >= 6 THEN 4
            WHEN s.score_count >= 1 THEN 5
            ELSE 6
        END AS band_order
    FROM cohorts c
    LEFT JOIN scores_by_golfer s ON s.golfer_id = c.golfer_id
),
aggregated AS (
    SELECT association_scope, population, band_order,
        COUNT(*) AS golfer_count,
        SUM(score_count) AS scores_in_band
    FROM banded
    GROUP BY 1, 2, 3
),
complete_bands AS (
    SELECT s.association_scope, p.population, b.band_order, b.posting_band,
        COALESCE(a.golfer_count, 0) AS golfer_count,
        COALESCE(a.scores_in_band, 0) AS scores_in_band
    FROM (VALUES ('all'), ('aga'), ('international')) AS s(association_scope)
    CROSS JOIN (VALUES ('regular'), ('junior')) AS p(population)
    CROSS JOIN (VALUES
        (1, '50+'), (2, '25-49'), (3, '10-24'),
        (4, '6-9'), (5, '1-5'), (6, '0')
    ) AS b(band_order, posting_band)
    LEFT JOIN aggregated a
        ON a.association_scope = s.association_scope
       AND a.population = p.population
       AND a.band_order = b.band_order
),
results AS (
    SELECT *, SUM(golfer_count) OVER (
        PARTITION BY association_scope, population
    ) AS total_unique_active_golfers
    FROM complete_bands
)
SELECT
    statement_timestamp() AS extracted_at,
    current_database() AS source_database,
    DATE '2026-01-01' AS score_period_start,
    DATE '2026-08-31' AS score_period_end,
    association_scope, population, band_order, posting_band,
    golfer_count, total_unique_active_golfers,
    ROUND(100.0 * golfer_count / NULLIF(total_unique_active_golfers, 0), 2)
        AS golfer_percent,
    scores_in_band
FROM results
ORDER BY association_scope, population, band_order;
