-- Export as current_trial_pools.csv. Current snapshot only; no score joins.
-- Pool = unique golfers with a non-test trial-association membership (237).
-- Active takes precedence when a golfer has both active and inactive trial memberships.
WITH trial_memberships AS (
    SELECT m.golfer_id,
           BOOL_OR(m.status = 'Active') AS has_active,
           BOOL_OR(m.status = 'Inactive') AS has_inactive
    FROM public.v_golfer_clubs m
    JOIN public.v_clubs c ON c.club_id = m.club_id
    WHERE m.association_id = 237
      AND c.is_test = 'No'
      AND m.golfer_id IS NOT NULL
      AND m.status IN ('Active', 'Inactive')
    GROUP BY m.golfer_id
)
SELECT statement_timestamp() AS retrieved_at,
       current_database() AS source_database,
       COUNT(*) FILTER (WHERE has_active) AS active_trial_golfers,
       COUNT(*) FILTER (WHERE has_inactive AND NOT has_active) AS inactive_trial_golfers,
       COUNT(*) FILTER (WHERE has_active AND has_inactive) AS overlapping_status_golfers
FROM trial_memberships;
