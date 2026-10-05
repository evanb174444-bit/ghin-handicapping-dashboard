-- Export as trial_monthly_history.csv.
-- Aggregate counts only; one source table, no score or membership joins.
-- Sign-up dates are reported as recorded, pending confirmation of conversion rules.
SELECT
    statement_timestamp() AS retrieved_at,
    current_database() AS source_database,
    e.event_type,
    DATE_TRUNC('month', e.event_date)::date AS event_month,
    COUNT(*) AS trial_records,
    COUNT(DISTINCT t.golfer_id) AS unique_golfers,
    MIN(e.event_date) AS first_event_at,
    MAX(e.event_date) AS last_event_at
FROM public.trial_golfers t
CROSS JOIN LATERAL (
    VALUES
        ('Trial record created', t.created_at),
        ('Trial started', t.trial_start_date::timestamp),
        ('Sign-up recorded', t.sign_up_date)
) AS e(event_type, event_date)
WHERE e.event_date IS NOT NULL
GROUP BY e.event_type, DATE_TRUNC('month', e.event_date)::date
ORDER BY event_month, e.event_type;
