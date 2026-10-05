-- Export as gps_renewal_type_profile.csv. Run the entire statement.
-- Inspect the dedicated renewal-type field before interpreting its values.
-- Distinct golfer counts can overlap across groups; do not sum them as a unique total.
WITH active_golfers AS (
    SELECT DISTINCT golfer_id
    FROM public.gps_subscriptions
    WHERE active IS TRUE AND golfer_id IS NOT NULL
)
SELECT statement_timestamp() AS retrieved_at,
       COALESCE(NULLIF(TRIM(e.subscription_renewal_type), ''), '(missing)') AS subscription_renewal_type,
       COALESCE(NULLIF(TRIM(e.subscription_type), ''), '(missing)') AS subscription_type,
       COUNT(*) AS extract_records,
       COUNT(DISTINCT e.golfer_id) AS unique_golfers,
       COUNT(DISTINCT e.golfer_id) FILTER (WHERE a.golfer_id IS NOT NULL) AS unique_active_flagged_golfers,
       COUNT(DISTINCT e.golfer_id) FILTER (
           WHERE a.golfer_id IS NOT NULL
             AND e.subscription_start_date <= statement_timestamp()
             AND e.subscription_end_date > statement_timestamp()
       ) AS unique_active_golfers_with_current_extract_dates
FROM public.t_extract_golfers_enhanced_gps_subscriptions e
LEFT JOIN active_golfers a ON a.golfer_id = e.golfer_id
GROUP BY 2, 3
ORDER BY unique_active_flagged_golfers DESC, 2, 3;
