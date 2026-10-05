-- Export as trial_cohorts.csv. No score or membership joins.
-- Cohorts follow Created At, matching the existing Tableau trial-creation report.
-- Conversion lag follows Trial Start Date; counts reflect the current source records.
SELECT
    statement_timestamp() AS retrieved_at,
    DATE_TRUNC('month', created_at)::date AS trial_created_month,
    COUNT(*) AS trials_created,
    COUNT(*) FILTER (WHERE sign_up_date IS NOT NULL) AS recorded_conversions,
    COUNT(*) FILTER (WHERE sign_up_date IS NULL) AS no_recorded_conversion,
    COUNT(*) FILTER (WHERE sign_up_date::date - trial_start_date = 0) AS same_day,
    COUNT(*) FILTER (WHERE sign_up_date::date - trial_start_date = 1) AS next_day,
    COUNT(*) FILTER (WHERE sign_up_date::date - trial_start_date BETWEEN 2 AND 7) AS days_2_to_7,
    COUNT(*) FILTER (WHERE sign_up_date::date - trial_start_date BETWEEN 8 AND 30) AS days_8_to_30,
    COUNT(*) FILTER (WHERE sign_up_date::date - trial_start_date > 30) AS days_31_plus,
    COUNT(*) FILTER (
        WHERE sign_up_date IS NOT NULL
          AND (trial_start_date IS NULL OR sign_up_date::date < trial_start_date)
    ) AS conversion_lag_unknown_or_invalid,
    COUNT(*) FILTER (WHERE trial_start_date <= CURRENT_DATE - 30) AS trials_observed_at_least_30_days,
    COUNT(*) FILTER (
        WHERE trial_start_date <= CURRENT_DATE - 30
          AND sign_up_date::date - trial_start_date BETWEEN 0 AND 30
    ) AS conversions_within_30_days_observed_cohort,
    COUNT(*) FILTER (
        WHERE trial_start_date::date <> created_at::date
    ) AS trial_start_differs_from_creation_date
FROM public.trial_golfers
GROUP BY DATE_TRUNC('month', created_at)::date
ORDER BY trial_created_month;
