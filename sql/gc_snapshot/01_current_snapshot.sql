-- SUPERSEDED: supplied schema proves v_golfer_clubs and v_golfers exclude Archived.
-- Do not use this provisional query for the requested complete snapshot.
-- PostgreSQL. SELECT only. Provisional mapping: read FIELD_MAPPING.txt before use.
-- One statement = one MVCC snapshot for ordinary local PostgreSQL relations.
-- Set session TimeZone to UTC before running if you want captured_at rendered in UTC.
WITH scope(club_id) AS (VALUES
    (54806),
    (54807),
    (54808),
    (54809),
    (54810),
    (54811),
    (54812),
    (54813),
    (54814),
    (54815),
    (54816),
    (54817),
    (54818),
    (54819),
    (54820),
    (54821),
    (54822),
    (54823),
    (54824),
    (54825),
    (54827),
    (54828),
    (54830),
    (54831),
    (54832),
    (54833),
    (54834),
    (54835),
    (54836),
    (54837),
    (54838),
    (54839),
    (54840),
    (54841),
    (54842),
    (54843),
    (54844),
    (54845),
    (54846),
    (54847),
    (54849),
    (54850),
    (54851),
    (54852),
    (54853),
    (54854),
    (54855),
    (54856),
    (54857),
    (54858),
    (54859),
    (54860),
    (54861),
    (54862),
    (54863),
    (54864),
    (54865)
), base AS (
 SELECT m.* FROM public.v_golfer_clubs m JOIN scope s ON s.club_id=m.club_id
), club_lookup AS (
 SELECT c.club_id, count(*) AS matches, jsonb_agg(to_jsonb(c)) AS records
 FROM public.v_clubs c JOIN scope s ON s.club_id=c.club_id GROUP BY c.club_id
), golfer_lookup AS (
 SELECT g.golfer_id, count(*) AS matches, jsonb_agg(to_jsonb(g)) AS records
 FROM public.v_golfers g
 WHERE EXISTS (SELECT 1 FROM base m WHERE m.golfer_id=g.golfer_id)
 GROUP BY g.golfer_id
), association_lookup AS (
 SELECT a.association_id, count(*) AS matches, jsonb_agg(to_jsonb(a)) AS records
 FROM public.v_associations a GROUP BY a.association_id
), joined AS (
 SELECT m.*, c.matches AS club_matches, g.matches AS golfer_matches,
        CASE WHEN c.matches=1 THEN c.records->0 END AS club,
        CASE WHEN g.matches=1 THEN g.records->0 END AS golfer,
        c.records AS club_records, g.records AS golfer_records
 FROM base m
 LEFT JOIN club_lookup c ON c.club_id=m.club_id
 LEFT JOIN golfer_lookup g ON g.golfer_id=m.golfer_id
), snapshot AS (
 SELECT statement_timestamp() AS captured_at,
 current_database() AS source_database, current_setting('TimeZone') AS source_session_timezone,
 current_setting('TimeZone') AS capture_timezone,
 m.golfer_club_id, m.golfer_id, m.club_id,
 NULL::text AS ghin_number, NULL::text AS club_number,
 m.club->>'club_name' AS club_name,
 m.club->>'association_id' AS association_id,
 CASE WHEN a.matches=1 THEN a.records->0->>'association_name' END AS association_name,
 m.association_id AS membership_association_id_raw,
 m.status AS membership_status, m.membership_creation_date,
 m.status_date AS membership_status_date,
 NULL::text AS membership_expiration_date,
 m.inactive_date AS inactive_date_raw,
 m.updated_at AS membership_updated_at,
 m.golfer->>'handicap_index_display' AS handicap_index,
 m.golfer->>'handicap_index' AS handicap_index_value_raw,
 m.golfer->>'handicap_index_display' AS handicap_index_display_raw,
 CASE
 WHEN upper(btrim(m.golfer->>'handicap_index_display'))='NH' THEN 'NH'
 WHEN upper(btrim(m.golfer->>'handicap_index_display'))='WD' THEN 'WD'
 WHEN btrim(m.golfer->>'handicap_index_display') ~ '^[+-]?[0-9]+([.][0-9]+)?$' THEN 'numeric_display'
 WHEN nullif(btrim(m.golfer->>'handicap_index_display'),'') IS NULL
      AND nullif(btrim(m.golfer->>'handicap_index'),'') IS NULL THEN 'missing'
 WHEN nullif(btrim(m.golfer->>'handicap_index_display'),'') IS NULL THEN 'value_only_unresolved'
 ELSE 'other_display' END AS handicap_state,
 m.golfer->>'gender' AS gender,
 NULL::text AS date_of_birth,
 m.usga_membership_type, NULL::text AS local_number, NULL::text AS full_name,
 m.club_matches, m.golfer_matches, a.matches AS association_matches,
 to_jsonb(m) - ARRAY['club','golfer','club_records','golfer_records','club_matches','golfer_matches'] AS membership_record_raw,
 m.club_records AS club_records_raw, m.golfer_records AS golfer_records_raw,
 a.records AS association_records_raw
 FROM joined m
 LEFT JOIN association_lookup a ON a.association_id::text=m.club->>'association_id'
)
SELECT * FROM snapshot;
