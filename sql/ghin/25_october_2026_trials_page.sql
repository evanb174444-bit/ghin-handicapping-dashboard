-- October-only incremental export for GC Dashboard > Acquisition > Attribution > GHIN Trials.
-- Export all rows as trials_october_2026.csv. Run this entire file as one statement.
-- Includes October 1 through October 31: >= 2026-10-01 AND < 2026-11-01.
-- Preserve existing pre-October history. Replace October aggregates; do not add twice.
-- This is the page-specific alternative to full-history query 06, not a ninth required export.
-- Same-day membership matches are candidate GC attribution, not verified destinations.
-- Use the approved GC club-ID list during local processing. No score-table scan.
-- Observed at extraction; this does not certify an October 31 snapshot.
WITH data_0 AS (
SELECT
    statement_timestamp() AS retrieved_at,
    current_database() AS source_database,
    e.event_type,
    DATE_TRUNC('month', e.event_date)::date AS event_month,
    COUNT(*) AS trial_records,
    COUNT(DISTINCT t.golfer_id) AS unique_golfers,
    MIN(e.event_date) AS first_event_at,
    MAX(e.event_date) AS last_event_at
FROM public.trial_golfers t
CROSS JOIN LATERAL (
    VALUES
        ('Trial record created', t.created_at),
        ('Trial started', t.trial_start_date::timestamp),
        ('Sign-up recorded', t.sign_up_date)
) AS e(event_type, event_date)
WHERE e.event_date >= TIMESTAMP '2026-10-01'
  AND e.event_date < TIMESTAMP '2026-11-01'
GROUP BY e.event_type, DATE_TRUNC('month', e.event_date)::date
ORDER BY event_month, e.event_type
),
data_1 AS (
WITH conversions AS (
    SELECT DISTINCT golfer_id, sign_up_date::date AS conversion_date
    FROM public.trial_golfers
    WHERE sign_up_date >= TIMESTAMP '2026-10-01'
      AND sign_up_date <  TIMESTAMP '2026-11-01'
      AND golfer_id IS NOT NULL
), candidates AS (
    SELECT DISTINCT
        s.golfer_id, s.conversion_date,
        m.club_id, m.association_id,
        c.club_name, c.club_category, c.club_type,
        c.front_end_provider
    FROM conversions s
    JOIN public.v_golfer_clubs m
      ON m.golfer_id = s.golfer_id
     AND m.membership_creation_date >= s.conversion_date
     AND m.membership_creation_date < s.conversion_date + INTERVAL '1 day'
    JOIN public.v_clubs c ON c.club_id = m.club_id
    WHERE m.association_id <> 237
      AND c.is_test = 'No'
), match_counts AS (
    SELECT golfer_id, conversion_date, COUNT(*) AS candidate_count
    FROM candidates
    GROUP BY golfer_id, conversion_date
), attributed AS (
    SELECT s.golfer_id, s.conversion_date,
        CASE
            WHEN mc.candidate_count = 1 THEN 'One same-day candidate'
            WHEN mc.candidate_count > 1 THEN 'Multiple same-day candidates'
            ELSE 'No same-day candidate'
        END AS match_status,
        c.association_id, c.club_id, c.club_name,
        c.club_category, c.club_type, c.front_end_provider
    FROM conversions s
    LEFT JOIN match_counts mc
      ON mc.golfer_id = s.golfer_id
     AND mc.conversion_date = s.conversion_date
    LEFT JOIN candidates c
      ON c.golfer_id = s.golfer_id
     AND c.conversion_date = s.conversion_date
     AND mc.candidate_count = 1
)
SELECT statement_timestamp() AS retrieved_at,
    date_trunc('month', conversion_date)::date AS conversion_month,
    match_status, association_id, club_id, club_name,
    club_category, club_type, front_end_provider,
    COUNT(*) AS conversion_records,
    COUNT(DISTINCT golfer_id) AS unique_golfers
FROM attributed
GROUP BY date_trunc('month', conversion_date)::date,
         match_status, association_id, club_id, club_name,
         club_category, club_type, front_end_provider
ORDER BY conversion_month, conversion_records DESC, club_name
)
SELECT 'trial_monthly_history'::text AS dataset, 'manifest'::text AS record_type,
    statement_timestamp() AS extracted_at, current_database() AS source_database,
    current_setting('TimeZone') AS reporting_timezone, jsonb_build_object('period_start', '2026-10-01', 'period_end_exclusive', '2026-11-01') AS row_data
UNION ALL
SELECT 'trial_monthly_history'::text AS dataset, 'data'::text AS record_type,
    statement_timestamp() AS extracted_at, current_database() AS source_database,
    current_setting('TimeZone') AS reporting_timezone, to_jsonb(r) AS row_data FROM data_0 r
UNION ALL
SELECT 'ytd_trial_destinations'::text AS dataset, 'manifest'::text AS record_type,
    statement_timestamp() AS extracted_at, current_database() AS source_database,
    current_setting('TimeZone') AS reporting_timezone, jsonb_build_object('period_start', '2026-10-01', 'period_end_exclusive', '2026-11-01') AS row_data
UNION ALL
SELECT 'ytd_trial_destinations'::text AS dataset, 'data'::text AS record_type,
    statement_timestamp() AS extracted_at, current_database() AS source_database,
    current_setting('TimeZone') AS reporting_timezone, to_jsonb(r) AS row_data FROM data_1 r;
