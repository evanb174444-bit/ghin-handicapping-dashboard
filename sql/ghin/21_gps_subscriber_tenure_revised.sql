-- Export as gps_subscriber_tenure_revised.csv. Run this entire statement.
-- Same-day differences between initial and current-term start timestamps are allowed.
-- One golfer per cohort. Cohorts can overlap: canceled golfers may still be active.
-- Tenure is time since the earliest retained initial subscription date, NOT verified continuous membership.
-- Active: through today. Canceled: through scheduled end (may be future). Expired: through end date.
-- Canceled/expired cohorts use the golfer's most recently updated subscription record.
-- Percentages use valid-tenure golfers only. No individual identifiers are exported.
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
ORDER BY cohort;
