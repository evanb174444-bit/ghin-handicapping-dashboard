SELECT
    n.nspname AS schema_name,
    c.relname AS source_name,
    CASE
        WHEN c.relkind IN ('v', 'm')
        THEN pg_get_viewdef(c.oid, true)
    END AS view_definition,
    obj_description(c.oid, 'pg_class') AS source_comment,
    (
        SELECT jsonb_agg(
            jsonb_build_object(
                'column', a.attname,
                'type', format_type(a.atttypid, a.atttypmod),
                'comment', col_description(c.oid, a.attnum)
            )
            ORDER BY a.attnum
        )
        FROM pg_attribute a
        WHERE a.attrelid = c.oid
          AND a.attnum > 0
          AND NOT a.attisdropped
    ) AS columns
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relname IN (
      'v_golfer_clubs', 'golfer_clubs',
      'v_golfers',      'golfers',
      'v_clubs',        'clubs',
      'v_associations', 'associations'
  )
ORDER BY c.relname;
