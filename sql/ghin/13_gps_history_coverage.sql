-- Export as gps_history_coverage.csv. Aggregate-only history coverage check.
-- Retained intervals are not yet verified historical entitlement records.
WITH periods AS (
    SELECT 'enhanced_gps_extract' AS source,
           golfer_id, subscription_start_date AS starts_at,
           subscription_end_date AS ends_at
    FROM public.t_extract_golfers_enhanced_gps_subscriptions
    UNION ALL
    SELECT 'gps_subscriptions', golfer_id,
           current_subscription_start_date,
           current_subscription_end_date
    FROM public.gps_subscriptions
), per_golfer AS (
    SELECT source, golfer_id,
           COUNT(DISTINCT (starts_at, ends_at)) FILTER (
               WHERE starts_at IS NOT NULL AND ends_at > starts_at
           ) AS distinct_periods
    FROM periods
    WHERE golfer_id IS NOT NULL
    GROUP BY source, golfer_id
), history AS (
    SELECT source,
           COUNT(*) FILTER (WHERE distinct_periods > 1) AS golfers_with_multiple_periods,
           MAX(distinct_periods) AS most_periods_per_golfer
    FROM per_golfer
    GROUP BY source
)
SELECT statement_timestamp() AS retrieved_at,
       p.source,
       COUNT(*) AS period_rows,
       COUNT(DISTINCT p.golfer_id) AS unique_golfers,
       MIN(p.starts_at) AS earliest_start,
       MAX(p.starts_at) AS latest_start,
       MAX(p.ends_at) AS latest_end,
       COUNT(*) FILTER (
           WHERE p.starts_at IS NULL OR p.ends_at IS NULL
       ) AS rows_missing_dates,
       COUNT(*) FILTER (
           WHERE p.ends_at <= p.starts_at
       ) AS invalid_period_rows,
       COUNT(*) FILTER (WHERE p.golfer_id IS NULL) AS rows_missing_golfer,
       COUNT(*) FILTER (
           WHERE p.ends_at > p.starts_at
             AND p.ends_at < TIMESTAMP '2026-01-01'
       ) AS valid_periods_ended_before_2026,
       COUNT(DISTINCT p.golfer_id) FILTER (
           WHERE p.starts_at <= statement_timestamp()
             AND p.ends_at > statement_timestamp()
       ) AS golfers_with_current_date_coverage,
       h.golfers_with_multiple_periods,
       h.most_periods_per_golfer
FROM periods p
LEFT JOIN history h ON h.source = p.source
GROUP BY p.source, h.golfers_with_multiple_periods, h.most_periods_per_golfer
ORDER BY p.source;
