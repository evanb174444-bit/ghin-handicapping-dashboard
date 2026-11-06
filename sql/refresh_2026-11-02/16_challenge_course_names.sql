-- November 2 refresh. Export ALL results as challenge_course_names_2026-11-02.csv.
-- Based on sql/ghin/17_challenge_course_names.sql.
-- Current-state queries reflect actual execution time; history may include partial November.
-- Completed-month dashboard activity must stop before 2026-11-01.
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
ORDER BY ch.id;
