-- Metadata only. Export ALL rows as challenge_participant_schema.csv.
-- Does not read challenge, participant, score, or audit record contents.
-- Rejected-challenge relationships are discovery results, never assumed participants.
WITH relations AS (
    SELECT c.oid, n.nspname AS schema_name, c.relname AS object_name, c.relkind
    FROM pg_catalog.pg_class c
    JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relkind IN ('r', 'p', 'v', 'm', 'f')
      AND n.nspname NOT IN ('pg_catalog', 'information_schema')
      AND n.nspname !~ '^pg_toast|^pg_temp'
), columns AS (
    SELECT r.*, a.attnum, a.attname AS column_name,
           pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type
    FROM relations r JOIN pg_catalog.pg_attribute a ON a.attrelid = r.oid
    WHERE a.attnum > 0 AND NOT a.attisdropped
), candidates AS (
    SELECT DISTINCT oid FROM columns
    WHERE object_name ~* '(challenge|leaderboard|participant|contest|competition|registration|enrollment)'
       OR column_name ~* '(challenge|leaderboard|contest|competition)'
    UNION
    SELECT con.conrelid FROM pg_catalog.pg_constraint con
    JOIN relations target ON target.oid = con.confrelid
    WHERE con.contype = 'f' AND target.object_name = 'challenges'
    UNION
    SELECT rw.ev_class
    FROM pg_catalog.pg_depend dep
    JOIN pg_catalog.pg_rewrite rw ON rw.oid = dep.objid
    JOIN relations target ON target.oid = dep.refobjid
    WHERE dep.classid = 'pg_rewrite'::regclass
      AND dep.refclassid = 'pg_class'::regclass
      AND target.object_name = 'challenges'
)
SELECT statement_timestamp() AS extracted_at, current_database() AS source_database,
       'column'::text AS section, c.schema_name, c.object_name,
       jsonb_build_object('position', c.attnum, 'column', c.column_name,
                         'type', c.data_type, 'relation_kind', c.relkind) AS details
FROM columns c JOIN candidates x ON x.oid = c.oid
UNION ALL
SELECT statement_timestamp(), current_database(), 'foreign_key', r.schema_name, r.object_name,
       jsonb_build_object('constraint', con.conname,
                         'definition', pg_catalog.pg_get_constraintdef(con.oid))
FROM pg_catalog.pg_constraint con JOIN relations r ON r.oid = con.conrelid
WHERE con.contype = 'f'
  AND (con.conrelid IN (SELECT oid FROM candidates)
       OR con.confrelid IN (SELECT oid FROM candidates))
UNION ALL
SELECT statement_timestamp(), current_database(), 'index', r.schema_name, r.object_name,
       jsonb_build_object('definition', pg_catalog.pg_get_indexdef(i.indexrelid))
FROM pg_catalog.pg_index i JOIN relations r ON r.oid = i.indrelid
JOIN candidates x ON x.oid = r.oid
UNION ALL
SELECT statement_timestamp(), current_database(), 'view_definition', r.schema_name, r.object_name,
       jsonb_build_object('definition', pg_catalog.pg_get_viewdef(r.oid, TRUE))
FROM relations r JOIN candidates x ON x.oid = r.oid
WHERE r.relkind IN ('v', 'm')
ORDER BY section, schema_name, object_name;
