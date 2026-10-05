-- Reusable Scores export: score_monthly_dashboard_2025_2026.csv
-- Change the reporting bounds in params for subsequent refreshes.
-- Exclusive end date; current/prior extract tables must cover the requested years.
-- Raw application/API labels are retained for reviewed dashboard mappings.
-- Deduplicate extract membership rows by score ID before joining scores.
-- Hole counts describe score records, not independently deduplicated rounds.
WITH params AS (
    SELECT TIMESTAMP '2025-01-01' AS start_at,
           TIMESTAMP '2026-09-01' AS end_at
),
extract_labels AS (
    SELECT
        score_id,
        COALESCE(NULLIF(TRIM(score_posting_method), ''), 'Unknown') AS posting_method,
        COALESCE(NULLIF(TRIM(posting_application), ''), 'Unknown') AS posting_application,
        COALESCE(NULLIF(TRIM(posting_application_api), ''), 'Not supplied') AS posting_application_api,
        COALESCE(NULLIF(TRIM(source), ''), 'Not supplied') AS posting_source
    FROM public.t_extract_current_year_scores
    WHERE s_created_at >= (SELECT start_at FROM params)
      AND s_created_at < (SELECT end_at FROM params)
      AND score_id IS NOT NULL
    UNION
    SELECT
        score_id,
        COALESCE(NULLIF(TRIM(score_posting_method), ''), 'Unknown'),
        COALESCE(NULLIF(TRIM(posting_application), ''), 'Unknown'),
        COALESCE(NULLIF(TRIM(posting_application_api), ''), 'Not supplied'),
        COALESCE(NULLIF(TRIM(source), ''), 'Not supplied')
    FROM public.t_extract_previous_year_scores
    WHERE s_created_at >= (SELECT start_at FROM params)
      AND s_created_at < (SELECT end_at FROM params)
      AND score_id IS NOT NULL
),
labels_by_score AS (
    SELECT
        score_id,
        CASE WHEN COUNT(DISTINCT posting_method) = 1
             THEN MIN(posting_method) ELSE 'Conflicting labels' END AS posting_method,
        CASE WHEN COUNT(DISTINCT posting_application) = 1
             THEN MIN(posting_application) ELSE 'Conflicting labels' END AS posting_application,
        CASE WHEN COUNT(DISTINCT posting_application_api) = 1
             THEN MIN(posting_application_api) ELSE 'Conflicting labels' END AS posting_application_api,
        CASE WHEN COUNT(DISTINCT posting_source) = 1
             THEN MIN(posting_source) ELSE 'Conflicting labels' END AS posting_source
    FROM extract_labels
    GROUP BY score_id
),
scores_by_golfer AS (
    SELECT
        DATE_TRUNC('month', s.created_at)::date AS posting_month,
        s.golfer_id,
        s.status,
        s.is_trial,
        COALESCE(e.posting_method, 'Missing from extract') AS posting_method,
        COALESCE(e.posting_application, 'Missing from extract') AS posting_application,
        COALESCE(e.posting_application_api, 'Missing from extract') AS posting_application_api,
        COALESCE(e.posting_source, 'Missing from extract') AS posting_source,
        s.number_of_holes,
        s.number_of_played_holes,
        COUNT(*) AS score_count
    FROM public.scores s
    LEFT JOIN labels_by_score e ON e.score_id = s.id
    WHERE s.created_at >= (SELECT start_at FROM params)
      AND s.created_at < (SELECT end_at FROM params)
      AND s.deleted = FALSE
      AND s.penalty IS NOT TRUE
    GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
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
        s.posting_method,
        s.posting_application,
        s.posting_application_api,
        s.posting_source,
        s.number_of_holes,
        s.number_of_played_holes,
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
    posting_method,
    posting_application,
    posting_application_api,
    posting_source,
    number_of_holes,
    number_of_played_holes,
    SUM(score_count) AS score_count
FROM classified
GROUP BY 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18
ORDER BY 3, 4, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18;
