-- One read-only metadata query. Follow dependencies beneath the reporting views.
WITH RECURSIVE sources(oid) AS (
    SELECT c.oid
    FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
    WHERE n.nspname='public'
      AND c.relname IN ('v_golfer_clubs_common','v_golfers_common','clubs','golf_associations')
    UNION
    SELECT d.refobjid
    FROM sources s
    JOIN pg_rewrite r ON r.ev_class=s.oid
    JOIN pg_depend d ON d.classid='pg_rewrite'::regclass AND d.objid=r.oid
    JOIN pg_class target ON target.oid=d.refobjid
    JOIN pg_namespace tn ON tn.oid=target.relnamespace
    WHERE d.refclassid='pg_class'::regclass
      AND tn.nspname NOT IN ('pg_catalog','information_schema')
      AND target.relkind IN ('r','p','v','m','f')
)
SELECT n.nspname AS schema_name, c.relname AS source_name,
       current_setting('TimeZone') AS database_session_timezone,
       CASE WHEN c.relkind IN ('v','m') THEN pg_get_viewdef(c.oid,true) END AS view_definition,
       obj_description(c.oid,'pg_class') AS source_comment,
       (SELECT jsonb_agg(jsonb_build_object(
           'column',a.attname,'type',format_type(a.atttypid,a.atttypmod),
           'comment',col_description(c.oid,a.attnum)) ORDER BY a.attnum)
        FROM pg_attribute a WHERE a.attrelid=c.oid AND a.attnum>0 AND NOT a.attisdropped) AS columns,
       (SELECT jsonb_agg(jsonb_build_object(
           'name',k.conname,'definition',pg_get_constraintdef(k.oid,true)))
        FROM pg_constraint k WHERE k.conrelid=c.oid) AS constraints
FROM sources s JOIN pg_class c ON c.oid=s.oid
JOIN pg_namespace n ON n.oid=c.relnamespace
ORDER BY n.nspname,c.relname;
