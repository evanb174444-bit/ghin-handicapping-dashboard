-- Export as acquisition_history_2026-11-02.csv. Completed months through October 2026.
-- Prepared for November 2, 2026. SELECT only; not database-validated.
WITH qualifying AS (
    SELECT DISTINCT
           m.golfer_id,
           DATE_TRUNC('month', m.golfer_creation_date)::date AS reporting_month,
           CASE WHEN a.parent_federation = 'United States Golf Association'
                THEN 'AGA' ELSE 'International' END AS association_scope,
           CASE WHEN m.usga_membership_type = 'Standard' THEN 'Regular'
                WHEN m.usga_membership_type = 'Junior' THEN 'Junior'
                ELSE 'Unclassified' END AS member_population
    FROM public.v_golfer_clubs m
    JOIN public.v_clubs c ON c.club_id = m.club_id
    JOIN public.v_associations a ON a.association_id = m.association_id
    WHERE c.is_test = 'No'
      AND a.is_test = 'No'
      AND NULLIF(BTRIM(a.parent_federation), '') IS NOT NULL
      AND m.association_id <> 237
      AND m.golfer_creation_date >= DATE '2020-01-01'
      AND m.golfer_creation_date < DATE '2026-11-01'
), selections AS (
    SELECT q.golfer_id, q.reporting_month, s.scope, p.population
    FROM qualifying q
    CROSS JOIN LATERAL
        (VALUES (q.association_scope), ('All Associations')) s(scope)
    CROSS JOIN LATERAL
        (VALUES (q.member_population), ('All Members')) p(population)
)
SELECT reporting_month, scope, population,
       COUNT(DISTINCT golfer_id) AS new_golfers
FROM selections
GROUP BY reporting_month, scope, population
ORDER BY reporting_month, scope, population;
