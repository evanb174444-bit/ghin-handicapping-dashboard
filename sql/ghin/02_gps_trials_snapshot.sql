-- Export as gps_trials_snapshot.csv.
-- Read a bounded sample of the existing summary tables, not the scores table.
-- retrieved_at is query time, NOT the source tables' refresh time.
SELECT
    statement_timestamp() AS retrieved_at,
    current_database() AS source_database,
    't_extract_gps_subscription_count' AS source_table,
    to_jsonb(s) AS metrics
FROM (
    SELECT *
    FROM public.t_extract_gps_subscription_count
    LIMIT 10
) s
UNION ALL
SELECT
    statement_timestamp(),
    current_database(),
    't_extract_trials',
    to_jsonb(t)
FROM (
    SELECT *
    FROM public.t_extract_trials
    LIMIT 10
) t;
