-- Small mapping lookup only: no score scan and no individual golfer records.
-- Export as score_membership_type_mapping.csv.
SELECT
    'Membership type' AS section,
    COALESCE(membership_type, '(null)') AS name,
    NULL::text AS definition,
    COUNT(*) AS records
FROM public.membership_types
GROUP BY membership_type
UNION ALL
SELECT
    'Mapping view' AS section,
    viewname AS name,
    definition,
    NULL::bigint AS records
FROM pg_views
WHERE schemaname = 'public'
  AND viewname IN (
      'v_club_membership_types',
      'v_association_membership_types'
  )
ORDER BY section, name;
