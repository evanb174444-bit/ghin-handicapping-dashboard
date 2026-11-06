-- Export one CSV with all rows. dataset identifies each component; row_data is JSON. Manifest rows are metadata. Monthly history may include partial November; exclude it from completed-month charts.
-- Prepared for November 2, 2026. SELECT only; not database-validated.
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
WHERE e.event_date IS NOT NULL
GROUP BY e.event_type, DATE_TRUNC('month', e.event_date)::date
ORDER BY event_month, e.event_type
),
data_1 AS (
SELECT
    statement_timestamp() AS retrieved_at,
    DATE_TRUNC('month', created_at)::date AS trial_created_month,
    COUNT(*) AS trials_created,
    COUNT(*) FILTER (WHERE sign_up_date IS NOT NULL) AS recorded_conversions,
    COUNT(*) FILTER (WHERE sign_up_date IS NULL) AS no_recorded_conversion,
    COUNT(*) FILTER (WHERE sign_up_date::date - trial_start_date = 0) AS same_day,
    COUNT(*) FILTER (WHERE sign_up_date::date - trial_start_date = 1) AS next_day,
    COUNT(*) FILTER (WHERE sign_up_date::date - trial_start_date BETWEEN 2 AND 7) AS days_2_to_7,
    COUNT(*) FILTER (WHERE sign_up_date::date - trial_start_date BETWEEN 8 AND 30) AS days_8_to_30,
    COUNT(*) FILTER (WHERE sign_up_date::date - trial_start_date > 30) AS days_31_plus,
    COUNT(*) FILTER (
        WHERE sign_up_date IS NOT NULL
          AND (trial_start_date IS NULL OR sign_up_date::date < trial_start_date)
    ) AS conversion_lag_unknown_or_invalid,
    COUNT(*) FILTER (WHERE trial_start_date <= CURRENT_DATE - 30) AS trials_observed_at_least_30_days,
    COUNT(*) FILTER (
        WHERE trial_start_date <= CURRENT_DATE - 30
          AND sign_up_date::date - trial_start_date BETWEEN 0 AND 30
    ) AS conversions_within_30_days_observed_cohort,
    COUNT(*) FILTER (
        WHERE trial_start_date::date <> created_at::date
    ) AS trial_start_differs_from_creation_date
FROM public.trial_golfers
GROUP BY DATE_TRUNC('month', created_at)::date
ORDER BY trial_created_month
),
data_2 AS (
WITH trial_memberships AS (
    SELECT m.golfer_id,
           BOOL_OR(m.status = 'Active') AS has_active,
           BOOL_OR(m.status = 'Inactive') AS has_inactive
    FROM public.v_golfer_clubs m
    JOIN public.v_clubs c ON c.club_id = m.club_id
    WHERE m.association_id = 237
      AND c.is_test = 'No'
      AND m.golfer_id IS NOT NULL
      AND m.status IN ('Active', 'Inactive')
    GROUP BY m.golfer_id
)
SELECT statement_timestamp() AS retrieved_at,
       current_database() AS source_database,
       COUNT(*) FILTER (WHERE has_active) AS active_trial_golfers,
       COUNT(*) FILTER (WHERE has_inactive AND NOT has_active) AS inactive_trial_golfers,
       COUNT(*) FILTER (WHERE has_active AND has_inactive) AS overlapping_status_golfers
FROM trial_memberships
),
data_3 AS (
WITH conversions AS (
    SELECT DISTINCT golfer_id, sign_up_date::date AS conversion_date
    FROM public.trial_golfers
    WHERE sign_up_date >= TIMESTAMP '2026-01-01'
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
    current_setting('TimeZone') AS reporting_timezone, jsonb_build_object('report_month_end_exclusive', '2026-11-01', 'score_year_start', '2026-01-01') AS row_data
UNION ALL
SELECT 'trial_monthly_history'::text AS dataset, 'data'::text AS record_type,
    statement_timestamp() AS extracted_at, current_database() AS source_database,
    current_setting('TimeZone') AS reporting_timezone, to_jsonb(r) AS row_data FROM data_0 r
UNION ALL
SELECT 'trial_cohorts'::text AS dataset, 'manifest'::text AS record_type,
    statement_timestamp() AS extracted_at, current_database() AS source_database,
    current_setting('TimeZone') AS reporting_timezone, jsonb_build_object('report_month_end_exclusive', '2026-11-01', 'score_year_start', '2026-01-01') AS row_data
UNION ALL
SELECT 'trial_cohorts'::text AS dataset, 'data'::text AS record_type,
    statement_timestamp() AS extracted_at, current_database() AS source_database,
    current_setting('TimeZone') AS reporting_timezone, to_jsonb(r) AS row_data FROM data_1 r
UNION ALL
SELECT 'current_trial_pools'::text AS dataset, 'manifest'::text AS record_type,
    statement_timestamp() AS extracted_at, current_database() AS source_database,
    current_setting('TimeZone') AS reporting_timezone, jsonb_build_object('report_month_end_exclusive', '2026-11-01', 'score_year_start', '2026-01-01') AS row_data
UNION ALL
SELECT 'current_trial_pools'::text AS dataset, 'data'::text AS record_type,
    statement_timestamp() AS extracted_at, current_database() AS source_database,
    current_setting('TimeZone') AS reporting_timezone, to_jsonb(r) AS row_data FROM data_2 r
UNION ALL
SELECT 'ytd_trial_destinations'::text AS dataset, 'manifest'::text AS record_type,
    statement_timestamp() AS extracted_at, current_database() AS source_database,
    current_setting('TimeZone') AS reporting_timezone, jsonb_build_object('report_month_end_exclusive', '2026-11-01', 'score_year_start', '2026-01-01') AS row_data
UNION ALL
SELECT 'ytd_trial_destinations'::text AS dataset, 'data'::text AS record_type,
    statement_timestamp() AS extracted_at, current_database() AS source_database,
    current_setting('TimeZone') AS reporting_timezone, to_jsonb(r) AS row_data FROM data_3 r;
