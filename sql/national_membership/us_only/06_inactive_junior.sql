-- U.S. working scope: USGA parent federation; includes Golf PR, excludes Guam.
-- Export this SELECT to its own CSV: 06_inactive_junior_YYYY-MM-DD.csv
-- Production BigData reporting connection; read-only.
-- No LIMIT: export using Query the database, not Use fetched rows.
-- Current state at execution; not a certified historical snapshot.
SELECT
    statement_timestamp() AS extracted_at,
    current_database() AS source_database,
    m.golfer_club_id AS membership_id,
    m.golfer_id,
    m.club_id,
    m.association_id,
    m.status AS membership_status,
    m.usga_membership_type,
    m.membership_creation_date,
    m.status_date AS membership_status_date,
    m.inactive_date,
    m.golfer_creation_date,
    m.association_membership_creation_date,
    m.updated_at AS membership_updated_at,
    g.golfer_id AS matched_golfer_id,
    g.created_at AS golfer_record_created_at,
    g.gender,
    g.age AS age_at_extraction,
    g.handicap_index,
    g.handicap_index_display,
    g.primary_club_id,
    g.status AS golfer_status,
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
WHERE m.status = 'Inactive'
  AND c.is_test = 'No'
  AND EXISTS (
      SELECT 1 FROM public.v_associations a
      WHERE a.association_id = m.association_id
        AND a.parent_federation = 'United States Golf Association'
        AND a.is_test = 'No'
  )
  AND m.association_id IS DISTINCT FROM 237
  AND m.usga_membership_type = 'Junior';
