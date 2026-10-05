-- Export as gps_tenure_date_diagnostics.csv. Run the entire statement.
-- Uses the same golfer selection and validation rules as query 19.
-- One row per cohort and exact combination of failed rules; rows sum to each cohort total.
-- This examines today's live records, so counts may differ from the October 4 export.
-- Missing-date classification takes precedence, matching query 19; individual flags still show overlaps.
-- No golfer identifiers or personal details are exported.
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
                  OR (starts_at IS NOT NULL AND h.first_subscription_at > starts_at)
                  OR (cohort = 'Latest record expired' AND tenure_end > statement_timestamp()) THEN 'Invalid dates'
                ELSE 'Valid' END AS date_quality
    FROM cohorts c JOIN history h USING (golfer_id)
), flags AS (
    SELECT *,
           first_subscription_at IS NULL AS missing_initial,
           tenure_end IS NULL AS missing_endpoint,
           COALESCE(first_subscription_at > statement_timestamp(), FALSE) AS initial_in_future,
           COALESCE(tenure_end < first_subscription_at, FALSE) AS endpoint_before_initial,
           COALESCE(first_subscription_at > starts_at, FALSE) AS term_start_before_initial,
           COALESCE(cohort = 'Latest record expired' AND tenure_end > statement_timestamp(), FALSE) AS expired_with_future_end
    FROM measured
), classified AS (
    SELECT *, COALESCE(NULLIF(CONCAT_WS(' + ',
        CASE WHEN missing_initial THEN 'Missing first subscription date' END,
        CASE WHEN missing_endpoint THEN 'Missing end date' END,
        CASE WHEN initial_in_future THEN 'First subscription date in future' END,
        CASE WHEN endpoint_before_initial THEN 'End before first subscription' END,
        CASE WHEN term_start_before_initial THEN 'Term start before first subscription' END,
        CASE WHEN expired_with_future_end THEN 'Expired status with future end' END
    ), ''), 'Passed all checks') AS rule_combination
    FROM flags
), breakdown AS (
    SELECT cohort, date_quality, rule_combination,
           COUNT(*) AS golfers,
           COUNT(*) FILTER (WHERE retained_subscription_records > 1) AS golfers_with_multiple_records,
           COUNT(*) FILTER (WHERE active IS TRUE) AS active_flagged_golfers,
           COUNT(*) FILTER (WHERE term_start_before_initial AND first_subscription_at::date = starts_at::date) AS start_conflicts_on_same_calendar_day,
           COUNT(*) FILTER (WHERE term_start_before_initial AND first_subscription_at - starts_at <= INTERVAL '1 day') AS start_conflicts_within_24_hours,
           ROUND(AVG(EXTRACT(EPOCH FROM (first_subscription_at - starts_at)) / 86400.0)
                 FILTER (WHERE term_start_before_initial), 2) AS average_days_initial_after_term_start,
           ROUND((PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (first_subscription_at - starts_at)) / 86400.0)
                 FILTER (WHERE term_start_before_initial))::numeric, 2) AS median_days_initial_after_term_start,
           ROUND(AVG(EXTRACT(EPOCH FROM (tenure_end - statement_timestamp()::timestamp)) / 86400.0)
                 FILTER (WHERE expired_with_future_end), 2) AS average_days_until_expired_record_ends
    FROM classified
    GROUP BY cohort, date_quality, rule_combination
)
SELECT statement_timestamp() AS retrieved_at, cohort, date_quality, rule_combination,
       golfers,
       ROUND(100.0 * golfers / NULLIF(SUM(golfers) OVER (PARTITION BY cohort), 0), 2) AS pct_of_cohort,
       golfers_with_multiple_records, active_flagged_golfers,
       start_conflicts_on_same_calendar_day, start_conflicts_within_24_hours,
       average_days_initial_after_term_start, median_days_initial_after_term_start,
       average_days_until_expired_record_ends
FROM breakdown
ORDER BY cohort, date_quality, golfers DESC, rule_combination;
