-- Export as gps_active_reconciliation.csv.
-- Each active golfer contributes to exactly one output group.
-- No score or membership joins; no individual identifiers exported.
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
ORDER BY date_coverage, unique_golfers DESC;
