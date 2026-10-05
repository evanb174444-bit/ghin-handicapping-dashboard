-- Small metadata query to identify the association ID/name lookup.
-- Does not scan golfer or membership populations.
SELECT table_name,
       string_agg(column_name, ', ' ORDER BY ordinal_position) AS available_columns
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name ILIKE '%association%'
  AND (table_name LIKE 'v_%' OR table_name IN ('associations', 'association'))
GROUP BY table_name
ORDER BY table_name;
