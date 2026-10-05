-- Export as gps_unique_subscribers.csv.
-- Distinct golfers across all subscription rows; no score-table scan.
-- Active flag and date tests are reported separately, not assumed equivalent.
WITH per_golfer AS (
    SELECT golfer_id,
        BOOL_OR(active IS TRUE) AS active_flag,
        BOOL_OR(active IS TRUE AND subscription_app_type = 'iOS') AS active_ios,
        BOOL_OR(active IS TRUE AND subscription_app_type = 'Android') AS active_android,
        BOOL_OR(active IS TRUE AND subscription_app_type = 'manual') AS active_manual,
        BOOL_OR(active IS TRUE AND subscription_app_type IS NULL) AS active_unknown_platform,
        BOOL_OR(active IS TRUE AND status IN ('canceled','expired','on hold')) AS active_with_review_status,
        BOOL_OR(active IS TRUE
            AND current_subscription_start_date <= statement_timestamp()
            AND current_subscription_end_date > statement_timestamp()) AS active_with_current_dates,
        COUNT(*) FILTER (WHERE active IS TRUE) AS active_rows
    FROM public.gps_subscriptions
    WHERE golfer_id IS NOT NULL
    GROUP BY golfer_id
)
SELECT
    statement_timestamp() AS retrieved_at,
    COUNT(*) AS golfers_with_subscription_records,
    COUNT(*) FILTER (WHERE active_flag) AS active_unique_golfers,
    COUNT(*) FILTER (WHERE active_ios) AS active_ios_golfers,
    COUNT(*) FILTER (WHERE active_android) AS active_android_golfers,
    COUNT(*) FILTER (WHERE active_ios AND active_android) AS active_on_both_platforms,
    COUNT(*) FILTER (WHERE active_manual) AS active_manual_golfers,
    COUNT(*) FILTER (WHERE active_unknown_platform) AS active_unknown_platform_golfers,
    COUNT(*) FILTER (WHERE active_rows > 1) AS golfers_with_multiple_active_rows,
    COUNT(*) FILTER (WHERE active_with_current_dates) AS active_golfers_with_current_dates,
    COUNT(*) FILTER (WHERE active_flag AND active_with_current_dates IS NOT TRUE) AS active_golfers_without_current_dates,
    COUNT(*) FILTER (WHERE active_with_review_status) AS active_golfers_with_review_status
FROM per_golfer;
