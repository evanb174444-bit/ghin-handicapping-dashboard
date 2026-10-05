-- Export all rows as score_monthly_counts_by_association_2025_2026.csv.
-- Includes trials, Temporary, UnderReview, and unknown statuses.
-- Association and member type use CURRENT primary-club records, not posting-time history.
-- is_regular/is_junior are independent flags; All Members sums each row once.
-- No Active membership filter: do not discard historical scores of now-inactive golfers.
-- Test/unknown/trial-association buckets are retained for reconciliation.
WITH scores_by_golfer AS (
    SELECT
        DATE_TRUNC('month', created_at)::date AS posting_month,
        golfer_id,
        status,
        is_trial,
        COUNT(*) AS score_count
    FROM public.scores
    WHERE created_at >= TIMESTAMP '2025-01-01'
      AND created_at <  TIMESTAMP '2026-09-01'
      AND deleted = false
      AND penalty IS NOT TRUE
    GROUP BY 1, 2, 3, 4
),
primary_associations AS (
    SELECT DISTINCT
        g.golfer_id,
        c.club_id,
        c.is_test AS club_is_test,
        a.association_id,
        a.association_name,
        a.parent_federation,
        a.is_test AS association_is_test
    FROM public.v_golfers g
    LEFT JOIN public.v_clubs c ON c.club_id = g.primary_club_id
    LEFT JOIN public.v_associations a
        ON a.association_id = c.association_id
),
golfer_mapping AS (
    -- Exactly one mapping row per golfer prevents score multiplication.
    SELECT
        golfer_id,
        COUNT(*) AS mapping_count,
        MIN(club_id) AS club_id,
        MIN(association_id) AS association_id,
        MIN(association_name) AS association_name,
        MIN(parent_federation) AS parent_federation,
        MIN(club_is_test) AS club_is_test,
        MIN(association_is_test) AS association_is_test
    FROM primary_associations
    GROUP BY golfer_id
),
membership_flags AS (
    SELECT
        m.golfer_id,
        BOOL_OR(COALESCE(mc.usga_membership_type = 'Standard', false))
            AS is_regular,
        BOOL_OR(COALESCE(mc.usga_membership_type = 'Junior', false))
            AS is_junior,
        BOOL_OR(mc.usga_membership_type IS NULL
            OR mc.usga_membership_type NOT IN ('Standard', 'Junior'))
            AS has_unclassified_membership
    FROM golfer_mapping m
    JOIN public.v_golfer_clubs mc
        ON mc.golfer_id = m.golfer_id AND mc.club_id = m.club_id
    WHERE m.mapping_count = 1
    GROUP BY m.golfer_id
),
classified AS (
    SELECT
        s.posting_month,
        s.status,
        s.is_trial,
        s.score_count,
        f.is_regular,
        f.is_junior,
        f.has_unclassified_membership,
        CASE
            WHEN m.mapping_count > 1 THEN 'ambiguous'
            WHEN m.club_is_test = 'Yes'
              OR m.association_is_test = 'Yes' THEN 'test'
            WHEN m.association_id = 237 THEN 'trial_association'
            WHEN m.association_id IS NULL
              OR m.club_is_test IS DISTINCT FROM 'No'
              OR m.association_is_test IS DISTINCT FROM 'No'
              OR NULLIF(TRIM(m.parent_federation), '') IS NULL
                THEN 'unknown'
            WHEN m.parent_federation = 'United States Golf Association'
                THEN 'aga'
            ELSE 'international'
        END AS association_scope,
        CASE WHEN m.mapping_count = 1 THEN m.association_id END
            AS association_id,
        CASE WHEN m.mapping_count = 1 THEN m.association_name END
            AS association_name,
        CASE WHEN m.mapping_count = 1 THEN m.parent_federation END
            AS parent_federation
    FROM scores_by_golfer s
    LEFT JOIN golfer_mapping m ON m.golfer_id = s.golfer_id
    LEFT JOIN membership_flags f ON f.golfer_id = s.golfer_id
)
SELECT
    statement_timestamp() AS extracted_at,
    current_database() AS source_database,
    posting_month,
    association_scope,
    association_id,
    association_name,
    parent_federation,
    status,
    is_trial,
    is_regular,
    is_junior,
    has_unclassified_membership,
    SUM(score_count) AS score_count
FROM classified
GROUP BY 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
ORDER BY 3, 4, 6, 8, 9, 10, 11, 12;
