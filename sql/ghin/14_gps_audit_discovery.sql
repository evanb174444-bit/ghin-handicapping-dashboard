-- Metadata only: determine how to search audits without scanning the full log.
SELECT 'index' AS section, indexname AS name, indexdef AS details
FROM pg_indexes
WHERE schemaname = 'public' AND tablename = 'audits'
UNION ALL
SELECT 'type_statistics', attname, most_common_vals::text
FROM pg_stats
WHERE schemaname = 'public' AND tablename = 'audits'
  AND attname IN ('auditable_type', 'associated_type')
UNION ALL
SELECT 'column_type', column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'audits'
  AND column_name IN ('audited_changes', 'auditable_type', 'created_at')
ORDER BY section, name;
