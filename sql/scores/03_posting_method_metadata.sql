-- Metadata only: identify the statistics field and any defined category labels.
SELECT
    a.attname AS column_name,
    t.typname AS type_name,
    t.typtype AS type_kind,
    e.enumlabel AS category_value
FROM pg_catalog.pg_attribute a
JOIN pg_catalog.pg_type t ON t.oid = a.atttypid
LEFT JOIN pg_catalog.pg_enum e ON e.enumtypid = t.oid
WHERE a.attrelid = 'public.scores'::regclass
  AND a.attname = 'statistics'
  AND NOT a.attisdropped
ORDER BY e.enumsortorder;
