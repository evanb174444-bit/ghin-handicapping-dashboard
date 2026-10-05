-- Metadata only. Export as ghin_challenges_schema.csv.
WITH candidates AS (
    SELECT DISTINCT table_catalog, table_schema, table_name
    FROM information_schema.columns
    WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
      AND (
          table_name ~* '(challenge|competition|contest|leaderboard)'
          OR column_name ~* '(challenge|competition|contest|leaderboard)'
      )
)
SELECT c.table_schema, c.table_name, t.table_type,
       c.ordinal_position, c.column_name, c.data_type
FROM information_schema.columns c
JOIN candidates x
  ON x.table_catalog = c.table_catalog
 AND x.table_schema = c.table_schema
 AND x.table_name = c.table_name
LEFT JOIN information_schema.tables t
  ON t.table_catalog = c.table_catalog
 AND t.table_schema = c.table_schema
 AND t.table_name = c.table_name
ORDER BY c.table_schema, c.table_name, c.ordinal_position;
