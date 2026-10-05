-- Export as gps_active_auto_renew_status.csv. Run the entire statement.
-- Counts unique golfers across active-flagged GPS subscription records.
-- This measures explicit current status labels, NOT verified auto-renew enrollment.
-- New, renewed, canceled and other statuses do not establish an on/off setting.
-- The four status groups are mutually exclusive and sum to active_flagged_golfers.
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
FROM per_golfer;
