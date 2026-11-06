-- November 3 full-refresh package. Export ALL rows as gc_current_snapshot_2026-11-03.csv.
-- Single read-only PostgreSQL export query; verified against supplied schema metadata.
-- Archived memberships and Archived golfer profiles are excluded as requested.
-- All other statuses (including NULL), dates, and handicap states are retained.
-- Every lookup joins a verified primary key: no membership-row multiplication.
-- captured_at is actual statement start in UTC; source timestamps stay unmodified.
-- GHIN number equals golfer_id, confirmed by Evan.
-- inactive_date is the membership expiration field, confirmed by Evan.
-- Original inactive_date and inactive_flag are also retained.
-- status_date is raw; its precise business meaning is not documented by the schema.
-- membership_versions is preserved as raw JSON, without asserting event completeness.
SELECT
    to_char(statement_timestamp() AT TIME ZONE 'UTC',
            'YYYY-MM-DD"T"HH24:MI:SS.US"Z"') AS captured_at,
    'UTC'::text AS captured_at_timezone,
    current_database() AS source_database,
    current_setting('TimeZone') AS database_session_timezone,
    'Unconfirmed: source timestamps have no timezone'::text AS source_timestamp_timezone,
    m.id AS golfer_club_id,
    m.golfer_id,
    m.golfer_id AS ghin_number,
    m.club_id,
    c.club_number,
    c.club_name,
    c.golf_association_id AS association_id,
    a.name AS association_name,
    m.golf_association_id AS membership_association_id_raw,
    m.status AS membership_status,
    -- Reproduces the verified reporting-view creation-date rule.
    COALESCE(m.create_db2_ts, m.created_at)::date AS membership_creation_date,
    COALESCE(m.create_db2_ts, m.created_at) AS membership_creation_timestamp_raw,
    m.created_at AS membership_record_created_at,
    m.create_db2_ts AS membership_legacy_creation_timestamp_raw,
    m.status_date AS membership_status_date,
    m.inactive_date AS membership_expiration_date,
    m.inactive_date AS inactive_date_raw,
    m.inactive_flag AS inactive_flag_raw,
    g.handicap_index_display AS handicap_index,
    g.handicap_index AS handicap_index_value_raw,
    g.handicap_index_display AS handicap_index_display_raw,
    g.handicap_index_type AS handicap_index_type_raw,
    g.index_type AS index_type_raw,
    g.hi_withdrawn AS hi_withdrawn_raw,
    g.rev_date AS handicap_revision_date_raw,
    CASE
        WHEN upper(btrim(g.handicap_index_display))='NH' THEN 'NH'
        WHEN upper(btrim(g.handicap_index_display))='WD' THEN 'WD'
        WHEN g.hi_withdrawn IS TRUE THEN 'withdrawn_flag_review_display'
        WHEN btrim(g.handicap_index_display) ~ '^[+-]?[0-9]+([.][0-9]+)?$'
            THEN 'numeric_display'
        WHEN NULLIF(btrim(g.handicap_index_display),'') IS NULL
             AND g.handicap_index IS NULL THEN 'missing'
        WHEN NULLIF(btrim(g.handicap_index_display),'') IS NULL
            THEN 'value_only_unresolved'
        ELSE 'other_display'
    END AS handicap_state,
    CASE g.gender WHEN 'M' THEN 'Male' WHEN 'F' THEN 'Female'
                  ELSE g.gender END AS gender,
    g.gender AS gender_raw,
    g.date_of_birth,
    ar.rate_type AS usga_membership_type,
    ar.membership_description,
    m.club_rate_id,
    cr.golf_association_rate_id AS resolved_association_rate_id,
    m.golf_association_rate_id AS membership_association_rate_id_raw,
    m.membership_code AS membership_code_raw,
    m.local_number,
    NULLIF(concat_ws(' ', NULLIF(btrim(g.prefix),''),
                          NULLIF(btrim(g.first_name),''),
                          NULLIF(btrim(g.middle_name),''),
                          NULLIF(btrim(g.last_name),''),
                          NULLIF(btrim(g.suffix),'')), '') AS full_name,
    g.first_name, g.middle_name, g.last_name, g.prefix, g.suffix,
    g.status AS golfer_status_raw,
    m.updated_at AS membership_updated_at,
    g.updated_at AS golfer_updated_at,
    m.auto_renew_enabled,
    m.auto_renew_date AS auto_renew_date_raw,
    m.auto_renew_inactive_date AS auto_renew_inactive_date_raw,
    m.auto_renew_disabled_on AS auto_renew_disabled_on_raw,
    m.auto_renew_failed,
    m.membership_versions AS membership_versions_raw,
    g.id AS matched_golfer_id,
    c.id AS matched_club_id,
    a.id AS matched_association_id,
    count(*) OVER () AS exported_membership_rows,
    count(*) OVER (PARTITION BY m.golfer_id, m.club_id) AS golfer_club_membership_record_count
FROM public.golfer_clubs m
LEFT JOIN public.golfers g ON g.id=m.golfer_id
LEFT JOIN public.clubs c ON c.id=m.club_id
LEFT JOIN public.golf_associations a ON a.id=c.golf_association_id
-- Same membership-type lineage as the verified reporting view.
LEFT JOIN public.club_rates cr ON cr.id=m.club_rate_id
LEFT JOIN public.golf_association_rates ar ON ar.id=cr.golf_association_rate_id
WHERE m.club_id IN (
    54806, 54807, 54808, 54809, 54810, 54811, 54812, 54813,
    54814, 54815, 54816, 54817, 54818, 54819, 54820, 54821,
    54822, 54823, 54824, 54825, 54827, 54828, 54830, 54831,
    54832, 54833, 54834, 54835, 54836, 54837, 54838, 54839,
    54840, 54841, 54842, 54843, 54844, 54845, 54846, 54847,
    54849, 54850, 54851, 54852, 54853, 54854, 54855, 54856,
    54857, 54858, 54859, 54860, 54861, 54862, 54863, 54864,
    54865
)
AND m.status IS DISTINCT FROM 'Archived'
AND g.status IS DISTINCT FROM 'Archived';
