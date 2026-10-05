-- January–September 2026; export as ytd_trial_destinations.csv.
-- Same-day membership matches are candidate attribution, not verified destinations.
-- Single read-only SELECT; no score-table joins.
WITH conversions AS (
    SELECT DISTINCT golfer_id, sign_up_date::date AS conversion_date
    FROM public.trial_golfers
    WHERE sign_up_date >= TIMESTAMP '2026-01-01'
      AND sign_up_date <  TIMESTAMP '2026-10-01'
      AND golfer_id IS NOT NULL
), candidates AS (
    SELECT DISTINCT
        s.golfer_id, s.conversion_date,
        m.club_id, m.association_id,
        c.club_name, c.club_category, c.club_type,
        c.front_end_provider
    FROM conversions s
    JOIN public.v_golfer_clubs m
      ON m.golfer_id = s.golfer_id
     AND m.membership_creation_date >= s.conversion_date
     AND m.membership_creation_date < s.conversion_date + INTERVAL '1 day'
    JOIN public.v_clubs c ON c.club_id = m.club_id
    WHERE m.association_id <> 237
      AND c.is_test = 'No'
), match_counts AS (
    SELECT golfer_id, conversion_date, COUNT(*) AS candidate_count
    FROM candidates
    GROUP BY golfer_id, conversion_date
), attributed AS (
    SELECT s.golfer_id, s.conversion_date,
        CASE
            WHEN mc.candidate_count = 1 THEN 'One same-day candidate'
            WHEN mc.candidate_count > 1 THEN 'Multiple same-day candidates'
            ELSE 'No same-day candidate'
        END AS match_status,
        c.association_id, c.club_id, c.club_name,
        c.club_category, c.club_type, c.front_end_provider
    FROM conversions s
    LEFT JOIN match_counts mc
      ON mc.golfer_id = s.golfer_id
     AND mc.conversion_date = s.conversion_date
    LEFT JOIN candidates c
      ON c.golfer_id = s.golfer_id
     AND c.conversion_date = s.conversion_date
     AND mc.candidate_count = 1
)
SELECT statement_timestamp() AS retrieved_at,
    date_trunc('month', conversion_date)::date AS conversion_month,
    match_status, association_id, club_id, club_name,
    club_category, club_type, front_end_provider,
    COUNT(*) AS conversion_records,
    COUNT(DISTINCT golfer_id) AS unique_golfers
FROM attributed
GROUP BY date_trunc('month', conversion_date)::date,
         match_status, association_id, club_id, club_name,
         club_category, club_type, front_end_provider
ORDER BY conversion_month, conversion_records DESC, club_name;

