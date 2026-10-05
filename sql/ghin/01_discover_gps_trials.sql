-- Run on the same Production BigData reporting connection used for scores.
-- Export all results as gps_trials_schema.csv.
-- Read-only metadata lookup: no golfer, membership, or score records are scanned.
-- Names are discovery candidates, not confirmed product sources.
WITH candidate_objects AS (
    SELECT DISTINCT table_catalog, table_schema, table_name
    FROM information_schema.columns
    WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
      AND (
          table_name ~* '(trial|gps|subscription|subscriber|premium|purchase|receipt|entitlement|revenuecat|sign_?up|conver)'
          OR column_name ~* '(trial|gps|subscription|subscriber|premium|purchase|receipt|entitlement|revenuecat|sign_?up|conver)'
      )
)
SELECT
    c.table_schema,
    c.table_name,
    t.table_type,
    c.ordinal_position,
    c.column_name,
    c.data_type,
    c.udt_name,
    c.is_nullable
FROM information_schema.columns c
JOIN candidate_objects o
  ON o.table_catalog = c.table_catalog
 AND o.table_schema = c.table_schema
 AND o.table_name = c.table_name
LEFT JOIN information_schema.tables t
  ON t.table_catalog = c.table_catalog
 AND t.table_schema = c.table_schema
 AND t.table_name = c.table_name
ORDER BY c.table_schema, c.table_name, c.ordinal_position;
