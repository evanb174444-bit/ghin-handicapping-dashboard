-- Read-only metadata; return these results to resolve provisional fields.
SELECT current_database(), current_setting('TimeZone'), statement_timestamp();
SELECT n.nspname, c.relname, a.attname, format_type(a.atttypid,a.atttypmod) AS data_type,
 col_description(c.oid,a.attnum) AS column_comment
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
JOIN pg_attribute a ON a.attrelid=c.oid
WHERE n.nspname='public' AND c.relname IN
 ('v_golfer_clubs','v_golfers','v_clubs','v_associations','golfer_clubs','golfers','clubs','associations')
 AND a.attnum>0 AND NOT a.attisdropped ORDER BY c.relname,a.attnum;
SELECT c.relname, pg_get_viewdef(c.oid,true) AS view_definition
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='public' AND c.relname IN ('v_golfer_clubs','v_golfers','v_clubs','v_associations')
AND c.relkind IN ('v','m');
