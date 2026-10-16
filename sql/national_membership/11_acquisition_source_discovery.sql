-- Acquisition refresh: run on the reporting connection used for prior exports.
-- Read-only metadata discovery; does not scan or export golfer records.
-- Export results as acquisition_source_schema.csv.
-- Purpose: distinguish first golfer registration, first non-trial membership,
-- and first established Handicap Index before implementing acquisition counts.
-- Current Active-only extracts cannot establish complete historical acquisition.
WITH candidates AS (
    SELECT DISTINCT table_catalog, table_schema, table_name
    FROM information_schema.columns
    WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
      AND (
          table_name IN ('v_golfers', 'v_golfer_clubs', 'v_clubs')
          OR (
              table_name ~* '(golfer|membership|handicap|trial)'
              AND (
                  table_name ~* '(histor|audit|event|activat|conver)'
                  OR column_name ~* '(first|establish|creation|created|activat|conver)'
              )
          )
      )
)
SELECT statement_timestamp() AS extracted_at,
       current_database() AS source_database,
       c.table_schema, c.table_name, t.table_type,
       c.ordinal_position, c.column_name, c.data_type, c.is_nullable
FROM information_schema.columns c
JOIN candidates x USING (table_catalog, table_schema, table_name)
LEFT JOIN information_schema.tables t USING (table_catalog, table_schema, table_name)
ORDER BY c.table_schema, c.table_name, c.ordinal_position;
