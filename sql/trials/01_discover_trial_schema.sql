-- Run on the Production BigData reporting connection.
-- Read-only metadata lookup; does not scan golfer or score records.
-- Export as trial_schema.csv.
WITH candidate_objects AS (
    SELECT DISTINCT table_catalog, table_schema, table_name
    FROM information_schema.columns
    WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
      AND (
          table_name ILIKE '%trial%'
          OR column_name ILIKE '%trial%'
          OR column_name ILIKE '%sign_up%'
          OR column_name ILIKE '%signup%'
          OR column_name ILIKE '%conver%'
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
