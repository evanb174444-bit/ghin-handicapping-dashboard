-- DIAGNOSTIC ONLY: omits approved test, trial, and association population filters.
-- Do not use as a validated acquisition export. See docs/KNOWLEDGE_BASE.md.
-- New golfer: distinct GHIN golfer ID with golfer-record Creation Date in period.
-- Source field: public.v_golfers.created_at (golfer_record_created_at in prior exports).
-- No Active-status, membership-creation-date, or trial-conversion filter.
-- Scope: all golfer records exposed by this view; no association/test exclusions.
-- Confirm this scope before using as an AGA-only headline.
-- Read-only. Export the full query result as new_golfers_monthly_YYYY-MM-DD.csv.
-- Calendar months use the reporting connection's timezone, included in output.
-- Includes completed months since January 2020; excludes the current partial month.
WITH bounds AS (
    SELECT DATE '2020-01-01' AS start_date,
           date_trunc('month', CURRENT_DATE)::date AS end_exclusive
), first_creation AS (
    SELECT golfer_id, MIN(created_at) AS creation_date
    FROM public.v_golfers
    WHERE golfer_id IS NOT NULL
    GROUP BY golfer_id
), monthly AS (
    SELECT date_trunc('month', g.creation_date)::date AS reporting_month,
           COUNT(*) AS new_golfers
    FROM first_creation g
    CROSS JOIN bounds b
    WHERE g.creation_date >= b.start_date
      AND g.creation_date < b.end_exclusive
    GROUP BY 1
), months AS (
    SELECT generate_series(b.start_date::timestamp,
                           b.end_exclusive::timestamp - INTERVAL '1 month',
                           INTERVAL '1 month')::date AS reporting_month
    FROM bounds b
)
SELECT statement_timestamp() AS extracted_at,
       current_database() AS source_database,
       current_setting('TimeZone') AS reporting_timezone,
       'All golfer records in v_golfers' AS reporting_scope,
       m.reporting_month,
       COALESCE(n.new_golfers, 0) AS new_golfers
FROM months m
LEFT JOIN monthly n USING (reporting_month)
ORDER BY m.reporting_month;
