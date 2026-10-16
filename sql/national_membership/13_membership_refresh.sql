-- Full current membership export, one source membership row per record.
-- No date or membership-status filter: current Active totals need older members,
-- and Creation Date acquisition must not discard now-inactive golfers.
-- Known test associations and all clubs not explicitly non-test are excluded.
-- Unknown association eligibility is retained only as Unresolved for audit.
-- Trial rows are separate from main All Members populations.
-- Validate membership_id uniqueness after joins before using any counts.
-- Current affiliations/types/statuses do not reconstruct historical snapshots.
-- This membership-based export cannot count golfers absent from v_golfer_clubs.
-- Export all results as membership_refresh_YYYY-MM-DD.csv. Keep raw IDs private.
SELECT
    statement_timestamp() AS extracted_at,
    current_database() AS source_database,
    current_setting('TimeZone') AS reporting_timezone,
    m.golfer_club_id AS membership_id,
    m.golfer_id,
    m.club_id,
    m.association_id,
    a.association_id AS matched_association_id,
    a.association_name,
    a.parent_federation,
    a.is_test AS association_is_test,
    CASE
        WHEN m.association_id = 237 THEN 'Trial'
        WHEN a.is_test IS DISTINCT FROM 'No' THEN 'Unresolved'
        WHEN a.parent_federation = 'United States Golf Association' THEN 'AGA'
        WHEN NULLIF(BTRIM(a.parent_federation), '') IS NOT NULL THEN 'International'
        ELSE 'Unresolved'
    END AS association_scope,
    m.status AS membership_status,
    m.usga_membership_type,
    CASE
        WHEN m.association_id = 237 THEN 'Trial'
        WHEN m.usga_membership_type = 'Standard' THEN 'Regular'
        WHEN m.usga_membership_type = 'Junior' THEN 'Junior'
        ELSE 'Unclassified'
    END AS member_population,
    m.membership_creation_date,
    m.golfer_creation_date,
    m.association_membership_creation_date,
    m.status_date AS membership_status_date,
    m.inactive_date,
    m.updated_at AS membership_updated_at,
    g.golfer_id AS matched_golfer_id,
    g.created_at AS golfer_record_created_at,
    g.status AS golfer_status,
    g.gender,
    g.age AS age_at_extraction,
    g.handicap_index,
    g.handicap_index_display,
    g.primary_club_id,
    c.club_name,
    c.association_id AS club_association_id,
    c.club_category,
    c.club_type,
    c.front_end_provider,
    c.status AS club_status,
    c.is_test AS club_is_test
FROM public.v_golfer_clubs m
JOIN public.v_clubs c ON c.club_id = m.club_id
LEFT JOIN public.v_golfers g ON g.golfer_id = m.golfer_id
LEFT JOIN public.v_associations a ON a.association_id = m.association_id
WHERE c.is_test = 'No'
  AND a.is_test IS DISTINCT FROM 'Yes';
