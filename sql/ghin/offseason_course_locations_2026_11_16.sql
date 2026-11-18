-- Read-only course-location lookup for the offseason dashboard.
-- Export as offseason_course_locations_2026-11-16.csv (all rows, headers).
-- Both ID interpretations are returned for validation against score course names.
-- No golfer identifiers included. No course/association geography is inferred.
WITH scored_courses AS (
 SELECT DISTINCT s.course_id::text AS score_course_id
 FROM public.scores s
 WHERE s.offseason IS TRUE
   AND s.course_id IS NOT NULL
)
SELECT s.score_course_id,
       ci.id AS course_record_id_by_id,
       ci.course_num AS course_number_by_id,
       ci.name AS course_name_by_id,
       ci.city AS city_by_id,
       ci.state AS state_by_id,
       ci.country AS country_by_id,
       cn.id AS course_record_id_by_number,
       cn.course_num AS course_number_by_number,
       cn.name AS course_name_by_number,
       cn.city AS city_by_number,
       cn.state AS state_by_number,
       cn.country AS country_by_number
FROM scored_courses s
LEFT JOIN public.crs_courses ci ON ci.id::text = s.score_course_id
LEFT JOIN public.crs_courses cn ON cn.course_num::text = s.score_course_id
ORDER BY s.score_course_id;
