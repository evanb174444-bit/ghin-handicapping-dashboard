-- Export as score_posting_counts_by_type_2026.csv.
-- Uses confirmed view: club_rates -> golf_association_rates.rate_type.
-- Unmapped types retained as unclassified; All Members always retains all eligible golfers.
WITH active_golfers AS (
    SELECT m.golfer_id,
        BOOL_OR(LOWER(TRIM(mt.usga_membership_type)) IN ('standard', 'regular')) AS is_regular,
        BOOL_OR(LOWER(TRIM(mt.usga_membership_type)) = 'junior') AS is_junior,
        BOOL_OR(COALESCE(LOWER(TRIM(mt.usga_membership_type)), '')
            NOT IN ('standard', 'regular', 'junior')) AS has_unclassified
    FROM public.golfer_clubs m
    JOIN public.clubs c ON c.id = m.club_id
    JOIN public.golf_associations a ON a.id = c.golf_association_id
    LEFT JOIN public.v_club_membership_types mt
        ON mt.club_membership_type_id = m.club_rate_id
       AND mt.club_id = m.club_id
    WHERE m.status = 'Active'
      AND m.golfer_id IS NOT NULL
      AND c.is_test = FALSE
      AND a.is_test = FALSE
      AND a.id <> 237
    GROUP BY m.golfer_id
),
score_counts AS (
    SELECT golfer_id, COUNT(*) AS score_count
    FROM public.scores
    WHERE created_at >= TIMESTAMP '2026-01-01'
      AND created_at < statement_timestamp()::timestamp
      AND deleted = FALSE
      AND penalty IS NOT TRUE
    GROUP BY golfer_id
),
banded AS (
    SELECT a.is_regular, a.is_junior, a.has_unclassified,
        CASE WHEN COALESCE(s.score_count, 0) = 0 THEN 1
             WHEN s.score_count <= 7 THEN 2 ELSE 3 END AS bucket_order
    FROM active_golfers a
    LEFT JOIN score_counts s ON s.golfer_id = a.golfer_id
),
counts AS (
    SELECT p.population, b.bucket_order, COUNT(*) AS golfer_count
    FROM banded b
    CROSS JOIN (VALUES ('all'), ('regular'), ('junior'), ('unclassified')) AS p(population)
    WHERE p.population = 'all'
       OR (p.population = 'regular' AND b.is_regular)
       OR (p.population = 'junior' AND b.is_junior)
       OR (p.population = 'unclassified' AND b.has_unclassified)
    GROUP BY p.population, b.bucket_order
),
complete_counts AS (
    SELECT p.population, b.bucket_order, b.posting_bucket,
        COALESCE(c.golfer_count, 0) AS golfer_count
    FROM (VALUES ('all'), ('regular'), ('junior'), ('unclassified')) AS p(population)
    CROSS JOIN (VALUES (1, '0 scores'), (2, '1–7 scores'), (3, '8+ scores')) AS b(bucket_order, posting_bucket)
    LEFT JOIN counts c ON c.population = p.population AND c.bucket_order = b.bucket_order
)
SELECT statement_timestamp() AS extracted_at,
    DATE '2026-01-01' AS score_period_start,
    statement_timestamp() AS score_period_end,
    population, posting_bucket, golfer_count,
    SUM(golfer_count) OVER (PARTITION BY population) AS population_total,
    ROUND(100.0 * golfer_count / NULLIF(SUM(golfer_count) OVER (PARTITION BY population), 0), 2)
        AS golfer_percentage
FROM complete_counts
ORDER BY CASE population WHEN 'all' THEN 1 WHEN 'regular' THEN 2 WHEN 'junior' THEN 3 ELSE 4 END,
    bucket_order;
