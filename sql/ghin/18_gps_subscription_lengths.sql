-- Export as gps_subscription_lengths.csv. Run the entire statement below.
-- Recorded term lengths, not total subscriber tenure or verified billing plans.
-- Cohorts overlap: active-flagged records may also have canceled/expired status.
-- Percentages use subscription records within each cohort, including missing/invalid dates.
-- Unique golfers within rows cannot be summed because a golfer may appear in multiple bands.
WITH source AS (
    SELECT golfer_id, active, LOWER(TRIM(status)) AS status,
           current_subscription_start_date AS starts_at,
           current_subscription_end_date AS ends_at
    FROM public.gps_subscriptions
), cohorts AS (
    SELECT 'Active-flagged' AS cohort, * FROM source WHERE active IS TRUE
    UNION ALL
    SELECT 'Expired status', * FROM source WHERE status = 'expired'
    UNION ALL
    SELECT 'Canceled status', * FROM source WHERE status IN ('canceled', 'cancelled')
), durations AS (
    SELECT *, EXTRACT(EPOCH FROM (ends_at - starts_at)) / 86400.0 AS term_days
    FROM cohorts
), banded AS (
    SELECT *, CASE
        WHEN starts_at IS NULL OR ends_at IS NULL OR ends_at <= starts_at THEN 4
        WHEN term_days < 330 THEN 1
        WHEN term_days <= 400 THEN 2
        ELSE 3 END AS band_order
    FROM durations
), counts AS (
    SELECT cohort, band_order,
           COUNT(*) AS subscription_records,
           COUNT(DISTINCT golfer_id) AS unique_golfers_within_band,
           COUNT(*) FILTER (WHERE active IS TRUE) AS active_flagged_records,
           COUNT(*) FILTER (WHERE starts_at <= statement_timestamp()
                              AND ends_at > statement_timestamp()) AS records_with_current_dates,
           COUNT(*) FILTER (WHERE starts_at IS NULL OR ends_at IS NULL) AS missing_date_records,
           COUNT(*) FILTER (WHERE ends_at <= starts_at) AS invalid_date_records
    FROM banded
    GROUP BY cohort, band_order
), cohort_names AS (
    SELECT DISTINCT cohort FROM cohorts
), bands(band_order, duration_band) AS (
    VALUES (1, 'Under 330 days'), (2, '330–400 days'),
           (3, 'Over 400 days'), (4, 'Missing / invalid dates')
)
SELECT statement_timestamp() AS retrieved_at, n.cohort, b.duration_band,
       COALESCE(c.subscription_records, 0) AS subscription_records,
       ROUND(100.0 * COALESCE(c.subscription_records, 0)
             / NULLIF(SUM(c.subscription_records) OVER (PARTITION BY n.cohort), 0), 2) AS pct_of_cohort_records,
       COALESCE(c.unique_golfers_within_band, 0) AS unique_golfers_within_band,
       COALESCE(c.active_flagged_records, 0) AS active_flagged_records,
       COALESCE(c.records_with_current_dates, 0) AS records_with_current_dates,
       COALESCE(c.missing_date_records, 0) AS missing_date_records,
       COALESCE(c.invalid_date_records, 0) AS invalid_date_records
FROM cohort_names n
CROSS JOIN bands b
LEFT JOIN counts c ON c.cohort = n.cohort AND c.band_order = b.band_order
ORDER BY n.cohort, b.band_order;
