-- Export one CSV with all rows. dataset identifies each component; row_data is JSON. Manifest rows are metadata. Monthly history may include partial November; exclude it from completed-month charts.
-- Prepared for November 2, 2026. SELECT only; not database-validated.
WITH data_0 AS (
WITH active_records AS (
    SELECT
        golfer_id,
        COALESCE(NULLIF(TRIM(status), ''), '(missing)') AS status,
        COALESCE(NULLIF(TRIM(subscription_app_type), ''), '(missing)') AS platform,
        CASE
            WHEN current_subscription_start_date IS NULL
              OR current_subscription_end_date IS NULL
                THEN 'Missing date'
            WHEN current_subscription_start_date > statement_timestamp()
                THEN 'Future start'
            WHEN current_subscription_end_date <= statement_timestamp()
                THEN 'Ended'
            ELSE 'Current dates'
        END AS date_state
    FROM public.gps_subscriptions
    WHERE active IS TRUE
      AND golfer_id IS NOT NULL
), per_golfer AS (
    SELECT
        golfer_id,
        CASE
            WHEN BOOL_OR(date_state = 'Current dates')
                THEN 'At least one current date range'
            WHEN BOOL_OR(date_state = 'Missing date')
                THEN 'No confirmed current range; missing dates present'
            ELSE 'All date ranges outside current period'
        END AS date_coverage,
        STRING_AGG(DISTINCT status, ' / ' ORDER BY status) AS active_statuses,
        STRING_AGG(DISTINCT platform, ' / ' ORDER BY platform) AS platforms,
        COUNT(*) AS active_subscription_rows
    FROM active_records
    GROUP BY golfer_id
)
SELECT
    statement_timestamp() AS retrieved_at,
    date_coverage,
    active_statuses,
    platforms,
    COUNT(*) AS unique_golfers,
    SUM(active_subscription_rows) AS active_subscription_rows,
    COUNT(*) FILTER (
        WHERE active_subscription_rows > 1
    ) AS golfers_with_multiple_active_rows
FROM per_golfer
GROUP BY date_coverage, active_statuses, platforms
ORDER BY date_coverage, unique_golfers DESC
),
data_1 AS (
SELECT
    statement_timestamp() AS retrieved_at,
    DATE_TRUNC('month', created_at)::date AS activity_month,
    COALESCE(NULLIF(TRIM(status), ''), '(missing)') AS activity_status,
    COUNT(*) AS activity_records,
    COUNT(DISTINCT golfer_id) AS unique_golfers,
    COUNT(DISTINCT subscription_id) AS unique_subscriptions,
    COUNT(*) FILTER (WHERE golfer_id IS NULL) AS missing_golfer_id,
    COUNT(*) FILTER (WHERE subscription_id IS NULL) AS missing_subscription_id,
    MIN(created_at) AS first_activity_at,
    MAX(created_at) AS last_activity_at,
    MAX(updated_at) AS latest_record_update
FROM public.gps_activities
GROUP BY
    DATE_TRUNC('month', created_at)::date,
    COALESCE(NULLIF(TRIM(status), ''), '(missing)')
ORDER BY activity_month, activity_status
),
data_2 AS (
WITH source AS (
    SELECT id, golfer_id, active, LOWER(TRIM(status)) AS status,
           initial_subscription_date AS initial_at,
           current_subscription_start_date AS starts_at,
           current_subscription_end_date AS ends_at,
           current_subscription_cancellation_date AS canceled_at,
           updated_at, created_at
    FROM public.gps_subscriptions
    WHERE golfer_id IS NOT NULL
), history AS (
    SELECT golfer_id, MIN(initial_at) AS first_subscription_at,
           COUNT(*) AS retained_subscription_records
    FROM source
    GROUP BY golfer_id
), latest AS (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY golfer_id ORDER BY COALESCE(updated_at, created_at) DESC NULLS LAST, id DESC
    ) AS row_num
    FROM source
), active_latest AS (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY golfer_id ORDER BY
            CASE WHEN starts_at <= statement_timestamp() AND ends_at > statement_timestamp() THEN 0 ELSE 1 END,
            COALESCE(updated_at, created_at) DESC NULLS LAST, id DESC
    ) AS row_num
    FROM source
    WHERE active IS TRUE
), cohorts AS (
    SELECT 'Active-flagged' AS cohort, golfer_id, active, starts_at, ends_at, canceled_at,
           statement_timestamp()::timestamp AS tenure_end
    FROM active_latest WHERE row_num = 1
    UNION ALL
    SELECT 'Latest record canceled', golfer_id, active, starts_at, ends_at, canceled_at, ends_at
    FROM latest WHERE row_num = 1 AND status IN ('canceled', 'cancelled')
    UNION ALL
    SELECT 'Latest record expired', golfer_id, active, starts_at, ends_at, canceled_at, ends_at
    FROM latest WHERE row_num = 1 AND status = 'expired'
), measured AS (
    SELECT c.*, h.first_subscription_at, h.retained_subscription_records,
           CASE WHEN h.first_subscription_at IS NULL OR tenure_end IS NULL THEN 'Missing dates'
                WHEN h.first_subscription_at > statement_timestamp()
                  OR tenure_end < h.first_subscription_at
                  OR (starts_at IS NOT NULL AND h.first_subscription_at::date > starts_at::date)
                  OR (cohort = 'Latest record expired' AND tenure_end > statement_timestamp()) THEN 'Invalid dates'
                ELSE 'Valid' END AS date_quality
    FROM cohorts c JOIN history h USING (golfer_id)
), valid_metrics AS (
    SELECT *,
           CASE WHEN date_quality = 'Valid' THEN
               EXTRACT(EPOCH FROM (tenure_end - first_subscription_at)) / 86400.0 / 365.2425 * 12
           END AS tenure_months,
           CASE WHEN date_quality = 'Valid' THEN
               EXTRACT(EPOCH FROM (LEAST(tenure_end, statement_timestamp()::timestamp) - first_subscription_at)) / 86400.0 / 365.2425 * 12
           END AS elapsed_months_to_date,
           CASE WHEN cohort = 'Latest record canceled'
                     AND first_subscription_at IS NOT NULL
                     AND canceled_at >= first_subscription_at
                     AND canceled_at <= statement_timestamp() THEN
               EXTRACT(EPOCH FROM (canceled_at - first_subscription_at)) / 86400.0 / 365.2425 * 12
           END AS months_to_cancel,
           CASE WHEN date_quality <> 'Valid' THEN NULL
                WHEN tenure_end < first_subscription_at + INTERVAL '1 year' THEN 1
                WHEN tenure_end < first_subscription_at + INTERVAL '2 years' THEN 2
                WHEN tenure_end < first_subscription_at + INTERVAL '3 years' THEN 3
                ELSE 4 END AS tenure_band
    FROM measured
)
SELECT statement_timestamp() AS retrieved_at, cohort,
       COUNT(*) AS unique_golfers,
       COUNT(*) FILTER (WHERE date_quality = 'Valid') AS valid_tenure_golfers,
       COUNT(*) FILTER (WHERE date_quality = 'Missing dates') AS missing_date_golfers,
       COUNT(*) FILTER (WHERE date_quality = 'Invalid dates') AS invalid_date_golfers,
       ROUND(AVG(tenure_months)::numeric, 1) AS average_tenure_months,
       ROUND((PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY tenure_months))::numeric, 1) AS median_tenure_months,
       ROUND(AVG(elapsed_months_to_date)::numeric, 1) AS average_elapsed_months_to_date,
       COUNT(*) FILTER (WHERE tenure_band = 1) AS under_1_year,
       COUNT(*) FILTER (WHERE tenure_band = 2) AS from_1_to_under_2_years,
       COUNT(*) FILTER (WHERE tenure_band = 3) AS from_2_to_under_3_years,
       COUNT(*) FILTER (WHERE tenure_band = 4) AS at_least_3_years,
       ROUND(100.0 * COUNT(*) FILTER (WHERE tenure_band = 1) / NULLIF(COUNT(tenure_months), 0), 1) AS under_1_year_pct,
       ROUND(100.0 * COUNT(*) FILTER (WHERE tenure_band = 2) / NULLIF(COUNT(tenure_months), 0), 1) AS from_1_to_under_2_years_pct,
       ROUND(100.0 * COUNT(*) FILTER (WHERE tenure_band = 3) / NULLIF(COUNT(tenure_months), 0), 1) AS from_2_to_under_3_years_pct,
       ROUND(100.0 * COUNT(*) FILTER (WHERE tenure_band = 4) / NULLIF(COUNT(tenure_months), 0), 1) AS at_least_3_years_pct,
       COUNT(*) FILTER (WHERE retained_subscription_records > 1) AS golfers_with_multiple_records,
       COUNT(*) FILTER (WHERE active IS TRUE) AS active_flagged_golfers,
       COUNT(*) FILTER (WHERE starts_at <= statement_timestamp() AND ends_at > statement_timestamp()) AS selected_records_with_current_dates,
       COUNT(months_to_cancel) AS golfers_with_valid_cancellation_date,
       ROUND(AVG(months_to_cancel)::numeric, 1) AS average_months_until_cancellation,
       ROUND((PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY months_to_cancel))::numeric, 1) AS median_months_until_cancellation,
       (SELECT COUNT(*) FROM public.gps_subscriptions WHERE golfer_id IS NULL) AS source_records_missing_golfer_id
FROM valid_metrics
GROUP BY cohort
ORDER BY cohort
),
data_3 AS (
WITH active_records AS (
    SELECT golfer_id,
           LOWER(TRIM(COALESCE(status, ''))) AS status,
           current_subscription_start_date AS starts_at,
           current_subscription_end_date AS ends_at
    FROM public.gps_subscriptions
    WHERE active IS TRUE AND golfer_id IS NOT NULL
), per_golfer AS (
    SELECT golfer_id, COUNT(*) AS active_records,
           BOOL_OR(status = 'auto-renewal on') AS has_on,
           BOOL_OR(status = 'auto-renewal off') AS has_off,
           BOOL_OR(COALESCE(starts_at <= statement_timestamp()
                           AND ends_at > statement_timestamp(), FALSE)) AS has_current_dates
    FROM active_records
    GROUP BY golfer_id
)
SELECT statement_timestamp() AS retrieved_at,
       COUNT(*) AS active_flagged_golfers,
       COUNT(*) FILTER (WHERE has_on AND NOT has_off) AS explicitly_on_without_off_label,
       COUNT(*) FILTER (WHERE has_off AND NOT has_on) AS explicitly_off_without_on_label,
       COUNT(*) FILTER (WHERE has_on AND has_off) AS conflicting_on_and_off_labels,
       COUNT(*) FILTER (WHERE NOT has_on AND NOT has_off) AS no_explicit_on_off_label,
       COUNT(*) FILTER (WHERE has_on) AS golfers_with_any_explicit_on_label,
       COUNT(*) FILTER (WHERE has_on AND NOT has_off AND has_current_dates) AS explicitly_on_with_current_dates,
       COUNT(*) FILTER (WHERE active_records > 1) AS golfers_with_multiple_active_records,
       COALESCE(SUM(active_records), 0) AS active_subscription_records,
       (SELECT COUNT(*) FROM public.gps_subscriptions
        WHERE active IS TRUE AND golfer_id IS NULL) AS active_records_missing_golfer_id
FROM per_golfer
)
SELECT 'gps_active_reconciliation'::text AS dataset, 'manifest'::text AS record_type,
    statement_timestamp() AS extracted_at, current_database() AS source_database,
    current_setting('TimeZone') AS reporting_timezone, jsonb_build_object('report_month_end_exclusive', '2026-11-01', 'score_year_start', '2026-01-01') AS row_data
UNION ALL
SELECT 'gps_active_reconciliation'::text AS dataset, 'data'::text AS record_type,
    statement_timestamp() AS extracted_at, current_database() AS source_database,
    current_setting('TimeZone') AS reporting_timezone, to_jsonb(r) AS row_data FROM data_0 r
UNION ALL
SELECT 'gps_monthly_activity'::text AS dataset, 'manifest'::text AS record_type,
    statement_timestamp() AS extracted_at, current_database() AS source_database,
    current_setting('TimeZone') AS reporting_timezone, jsonb_build_object('report_month_end_exclusive', '2026-11-01', 'score_year_start', '2026-01-01') AS row_data
UNION ALL
SELECT 'gps_monthly_activity'::text AS dataset, 'data'::text AS record_type,
    statement_timestamp() AS extracted_at, current_database() AS source_database,
    current_setting('TimeZone') AS reporting_timezone, to_jsonb(r) AS row_data FROM data_1 r
UNION ALL
SELECT 'gps_subscriber_tenure_revised'::text AS dataset, 'manifest'::text AS record_type,
    statement_timestamp() AS extracted_at, current_database() AS source_database,
    current_setting('TimeZone') AS reporting_timezone, jsonb_build_object('report_month_end_exclusive', '2026-11-01', 'score_year_start', '2026-01-01') AS row_data
UNION ALL
SELECT 'gps_subscriber_tenure_revised'::text AS dataset, 'data'::text AS record_type,
    statement_timestamp() AS extracted_at, current_database() AS source_database,
    current_setting('TimeZone') AS reporting_timezone, to_jsonb(r) AS row_data FROM data_2 r
UNION ALL
SELECT 'gps_active_auto_renew_status'::text AS dataset, 'manifest'::text AS record_type,
    statement_timestamp() AS extracted_at, current_database() AS source_database,
    current_setting('TimeZone') AS reporting_timezone, jsonb_build_object('report_month_end_exclusive', '2026-11-01', 'score_year_start', '2026-01-01') AS row_data
UNION ALL
SELECT 'gps_active_auto_renew_status'::text AS dataset, 'data'::text AS record_type,
    statement_timestamp() AS extracted_at, current_database() AS source_database,
    current_setting('TimeZone') AS reporting_timezone, to_jsonb(r) AS row_data FROM data_3 r;
