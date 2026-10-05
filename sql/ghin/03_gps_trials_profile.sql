-- Export as gps_trials_profile.csv. Aggregate data only; no score-table scan.
-- Latest record timestamps indicate record activity, not summary refresh time.
WITH gps AS (
    SELECT active, status, subscription_app_type, subscription_type,
        purchase_type, product_id,
        COUNT(*) AS subscription_rows,
        COUNT(DISTINCT golfer_id) AS unique_golfers,
        COUNT(*) FILTER (WHERE golfer_id IS NULL) AS missing_golfer_id,
        MIN(initial_subscription_date) AS earliest_initial_subscription,
        MAX(initial_subscription_date) AS latest_initial_subscription,
        MAX(updated_at) AS latest_record_update,
        COUNT(*) FILTER (
            WHERE current_subscription_end_date < statement_timestamp()
        ) AS rows_with_past_end_date
    FROM public.gps_subscriptions
    GROUP BY active, status, subscription_app_type, subscription_type,
        purchase_type, product_id
), trials AS (
    SELECT COUNT(*) AS trial_rows,
        COUNT(DISTINCT golfer_id) AS unique_golfers,
        COUNT(*) FILTER (WHERE golfer_id IS NULL) AS missing_golfer_id,
        MIN(created_at) AS earliest_created_at,
        MAX(created_at) AS latest_created_at,
        MIN(trial_start_date) AS earliest_trial_start,
        MAX(trial_start_date) AS latest_trial_start,
        COUNT(*) FILTER (WHERE sign_up_date IS NOT NULL) AS rows_with_sign_up_date,
        MIN(sign_up_date) AS earliest_sign_up_date,
        MAX(sign_up_date) AS latest_sign_up_date,
        MAX(updated_at) AS latest_record_update,
        COUNT(*) FILTER (
            WHERE sign_up_date::date < trial_start_date
        ) AS signups_before_trial_start,
        COUNT(*) FILTER (
            WHERE "54_holes_completed" IS TRUE
        ) AS rows_with_54_holes_completed
    FROM public.trial_golfers
)
SELECT statement_timestamp() AS retrieved_at,
    'gps_subscriptions' AS source, to_jsonb(gps) AS metrics
FROM gps
UNION ALL
SELECT statement_timestamp(), 'trial_golfers', to_jsonb(trials)
FROM trials;
