-- Export as trial_conversion_creation_dates_2026-10-13.csv.
-- Summary: at most 27 rows across 2024–2026 (nine categories per year).
-- Aggregate only: no personal records exported. All membership statuses retained.
-- Tests whether the CURRENT Creation Date aligns with trial or conversion.
-- Cannot prove an ID/date changed historically without before/after records.
WITH conversions AS (
    SELECT DISTINCT golfer_id, created_at::date AS trial_created_date,
           trial_start_date::date AS trial_start_date,
           sign_up_date::date AS conversion_date
    FROM public.trial_golfers
    WHERE sign_up_date >= DATE '2024-01-01'
      AND sign_up_date < DATE_TRUNC('month', CURRENT_DATE)
      AND golfer_id IS NOT NULL
), members AS (
    SELECT m.golfer_id,
           MIN(m.golfer_creation_date::date) AS creation_date,
           MAX(m.golfer_creation_date::date) AS max_creation_date,
           COUNT(*) FILTER (WHERE m.golfer_creation_date IS NULL) AS missing_date_rows
    FROM public.v_golfer_clubs m
    JOIN public.v_clubs c ON c.club_id=m.club_id
    JOIN public.v_associations a ON a.association_id=m.association_id
    WHERE c.is_test='No' AND a.is_test='No'
      AND a.parent_federation='United States Golf Association'
      AND m.association_id<>237
      AND EXISTS (SELECT 1 FROM conversions t WHERE t.golfer_id=m.golfer_id)
    GROUP BY m.golfer_id
), classified AS (
    SELECT t.*, m.creation_date,
      CASE
        WHEN m.golfer_id IS NULL THEN 'No qualifying AGA membership on linked golfer_id'
        WHEN m.creation_date IS NULL THEN 'Missing Creation Date'
        WHEN m.creation_date<>m.max_creation_date THEN 'Conflicting Creation Dates'
        WHEN m.missing_date_rows>0 THEN 'Some membership rows missing Creation Date'
        WHEN t.trial_created_date=t.conversion_date
             AND m.creation_date=t.conversion_date THEN 'Trial and conversion same day: ambiguous'
        WHEN m.creation_date=t.trial_created_date THEN 'Creation Date matches trial created date'
        WHEN m.creation_date=t.conversion_date THEN 'Creation Date matches conversion date'
        WHEN m.creation_date=t.trial_start_date THEN 'Creation Date matches trial start date'
        WHEN m.creation_date<t.conversion_date THEN 'Other Creation Date before conversion'
        ELSE 'Creation Date after conversion'
      END AS date_relationship
    FROM conversions t
    LEFT JOIN members m ON m.golfer_id=t.golfer_id
)
SELECT EXTRACT(YEAR FROM conversion_date)::integer AS conversion_year,
       date_relationship,
       COUNT(*) AS distinct_conversion_records,
       COUNT(DISTINCT golfer_id) AS unique_golfers,
       COUNT(DISTINCT golfer_id) FILTER (
           WHERE EXTRACT(YEAR FROM creation_date) < EXTRACT(YEAR FROM conversion_date)
       ) AS golfers_with_creation_in_earlier_year
FROM classified
GROUP BY 1,2
ORDER BY 1,2;
