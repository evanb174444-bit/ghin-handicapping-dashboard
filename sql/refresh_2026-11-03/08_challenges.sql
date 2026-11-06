-- November 3 full-refresh package. Export ALL rows as challenges_2026-11-03.csv.
-- Export one CSV with all rows. dataset identifies each component; row_data is JSON. Manifest rows are metadata. Monthly history may include partial November; exclude it from completed-month charts.
-- Prepared for November 3, 2026. SELECT only; not database-validated.
WITH data_0 AS (
SELECT statement_timestamp() AS retrieved_at,
       id AS challenge_id,
       association_id,
       course_id,
       status,
       start_date,
       end_date,
       created_at,
       updated_at,
       no_of_golfers,
       no_of_ranked_golfers,
       no_of_posted_scores
FROM public.challenges
ORDER BY start_date, id
),
data_1 AS (
SELECT ch.id AS challenge_id,
       ch.name AS challenge_name,
       ch.course_id,
       ci.name AS course_name_by_id,
       ci.course_num AS course_number_by_id,
       cn.id AS course_record_id_by_number,
       cn.name AS course_name_by_number
FROM public.challenges ch
LEFT JOIN public.crs_courses ci ON ci.id = ch.course_id
LEFT JOIN public.crs_courses cn ON cn.course_num = ch.course_id
WHERE ch.status IS DISTINCT FROM 'deleted'
ORDER BY ch.id
)
SELECT 'ghin_challenges'::text AS dataset, 'manifest'::text AS record_type,
    statement_timestamp() AS extracted_at, current_database() AS source_database,
    current_setting('TimeZone') AS reporting_timezone, jsonb_build_object('report_month_end_exclusive', '2026-11-01', 'score_year_start', '2026-01-01') AS row_data
UNION ALL
SELECT 'ghin_challenges'::text AS dataset, 'data'::text AS record_type,
    statement_timestamp() AS extracted_at, current_database() AS source_database,
    current_setting('TimeZone') AS reporting_timezone, to_jsonb(r) AS row_data FROM data_0 r
UNION ALL
SELECT 'challenge_course_names'::text AS dataset, 'manifest'::text AS record_type,
    statement_timestamp() AS extracted_at, current_database() AS source_database,
    current_setting('TimeZone') AS reporting_timezone, jsonb_build_object('report_month_end_exclusive', '2026-11-01', 'score_year_start', '2026-01-01') AS row_data
UNION ALL
SELECT 'challenge_course_names'::text AS dataset, 'data'::text AS record_type,
    statement_timestamp() AS extracted_at, current_database() AS source_database,
    current_setting('TimeZone') AS reporting_timezone, to_jsonb(r) AS row_data FROM data_1 r;
