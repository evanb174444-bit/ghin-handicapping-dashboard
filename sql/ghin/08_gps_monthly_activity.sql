-- Export as gps_monthly_activity.csv.
-- Monthly activity records by source status; not historical active-subscriber totals.
-- No score-table scan and no individual identifiers exported.
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
ORDER BY activity_month, activity_status;
