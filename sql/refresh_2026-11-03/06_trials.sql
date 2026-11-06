-- November 3 full-refresh package. Export ALL rows as trials_full_refresh_2026-11-03.csv.
-- Run the ENTIRE statement. Full monthly event history stops before November1.
-- YTD club-level destinations cover Jan1–Oct31. Cumulative timing/association results cover
-- all retained conversions before November1; current pools/cohort outcomes are observed now.
-- Nine datasets, each with its own manifest. Five timing buckets 0 / 1 / 2-7 / 8-30 / 31+.
-- This version extends the narrow October handoff; do not compare its full/YTD totals
-- directly to October-only reference totals without selecting October first.
-- Prepared from confirmed project SQL; this combined package has NOT been database-executed.
WITH data_0 AS (
SELECT
    statement_timestamp() AS retrieved_at,
    current_database() AS source_database,
    e.event_type,
    DATE_TRUNC('month', e.event_date)::date AS event_month,
    COUNT(*) AS trial_records,
    COUNT(DISTINCT t.golfer_id) AS unique_golfers,
    MIN(e.event_date) AS first_event_at,
    MAX(e.event_date) AS last_event_at
FROM public.trial_golfers t
CROSS JOIN LATERAL (
    VALUES
        ('Trial record created', t.created_at),
        ('Trial started', t.trial_start_date::timestamp),
        ('Sign-up recorded', t.sign_up_date)
) AS e(event_type, event_date)
WHERE e.event_date < TIMESTAMP '2026-11-01'
GROUP BY e.event_type, DATE_TRUNC('month', e.event_date)::date
ORDER BY event_month, e.event_type
),
data_1 AS (
WITH conversions AS (
    SELECT DISTINCT golfer_id, sign_up_date::date AS conversion_date
    FROM public.trial_golfers
    WHERE sign_up_date >= TIMESTAMP '2026-01-01'
      AND sign_up_date <  TIMESTAMP '2026-11-01'
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
ORDER BY conversion_month, conversion_records DESC, club_name
),
-- All retained recorded signups before cutoff. No invented program-start date.
raw_conversions AS (
    SELECT golfer_id, sign_up_date, trial_start_date,
           CASE
             WHEN NOT isfinite(sign_up_date) THEN 'Non-finite conversion date'
             WHEN trial_start_date IS NULL THEN 'Missing trial-start date'
             WHEN NOT isfinite(trial_start_date) THEN 'Non-finite trial-start date'
             WHEN sign_up_date::date < trial_start_date::date THEN 'Conversion before trial start'
             ELSE 'Valid'
           END AS timing_status,
           CASE WHEN isfinite(sign_up_date) AND isfinite(trial_start_date)
                THEN sign_up_date::date - trial_start_date::date END AS elapsed_days
    FROM public.trial_golfers
    WHERE sign_up_date < TIMESTAMP '2026-11-01'
),
timing_bands(bucket_order, bucket_label, lower_days_inclusive, upper_days_inclusive) AS (
    VALUES (1, 'First day', 0, 0), (2, 'Next day', 1, 1),
           (3, 'First week', 2, 7), (4, 'First month', 8, 30),
           (5, 'Beyond 1 month', 31, NULL::integer)
),
timing_buckets AS (
    SELECT b.bucket_order, b.bucket_label, b.lower_days_inclusive, b.upper_days_inclusive,
           COUNT(r.sign_up_date) AS conversion_records,
           COUNT(DISTINCT r.golfer_id) AS unique_golfers,
           COUNT(r.sign_up_date)::numeric /
             NULLIF((SELECT COUNT(*) FROM raw_conversions WHERE timing_status = 'Valid'), 0)
             AS share_of_valid_conversions
    FROM timing_bands b
    LEFT JOIN raw_conversions r ON r.timing_status = 'Valid'
      AND r.elapsed_days >= b.lower_days_inclusive
      AND (b.upper_days_inclusive IS NULL OR r.elapsed_days <= b.upper_days_inclusive)
    GROUP BY b.bucket_order, b.bucket_label, b.lower_days_inclusive, b.upper_days_inclusive
),
timing_exception_labels(exception) AS (
    VALUES ('Missing trial-start date'), ('Non-finite trial-start date'),
           ('Non-finite conversion date'), ('Conversion before trial start')
),
timing_exceptions AS (
    SELECT e.exception, COUNT(r.sign_up_date) AS conversion_records,
           COUNT(DISTINCT r.golfer_id) AS unique_golfers,
           'Recorded conversion rows before cutoff; mutually exclusive timing exceptions'::text AS population
    FROM timing_exception_labels e
    LEFT JOIN raw_conversions r ON r.timing_status = e.exception
    GROUP BY e.exception
),
-- Same event grain and matching logic as original October query, extended to retained history.
conversions AS (
    SELECT DISTINCT golfer_id, sign_up_date::date AS conversion_date
    FROM public.trial_golfers
    WHERE sign_up_date < TIMESTAMP '2026-11-01' AND golfer_id IS NOT NULL
),
candidates AS (
    SELECT DISTINCT s.golfer_id, s.conversion_date,
           m.club_id, m.association_id, c.club_name, c.club_category,
           c.club_type, c.front_end_provider
    FROM conversions s
    JOIN public.v_golfer_clubs m ON m.golfer_id = s.golfer_id
     AND m.membership_creation_date >= s.conversion_date
     AND m.membership_creation_date < s.conversion_date + INTERVAL '1 day'
    JOIN public.v_clubs c ON c.club_id = m.club_id
    WHERE m.association_id <> 237 AND c.is_test = 'No'
),
match_counts AS (
    SELECT golfer_id, conversion_date, COUNT(*) AS candidate_count
    FROM candidates GROUP BY golfer_id, conversion_date
),
attributed AS (
    SELECT s.golfer_id, s.conversion_date,
           CASE WHEN mc.candidate_count = 1 THEN 'One same-day candidate'
                WHEN mc.candidate_count > 1 THEN 'Multiple same-day candidates'
                ELSE 'No same-day candidate' END AS match_status,
           c.club_id, c.association_id AS membership_association_id
    FROM conversions s
    LEFT JOIN match_counts mc ON mc.golfer_id = s.golfer_id AND mc.conversion_date = s.conversion_date
    LEFT JOIN candidates c ON c.golfer_id = s.golfer_id AND c.conversion_date = s.conversion_date
                         AND mc.candidate_count = 1
),
-- Resolve current destination club association only AFTER matching; never expand candidate count.
club_associations AS (
    SELECT c.club_id,
           CASE WHEN COUNT(DISTINCT c.association_id) = 1
                  AND COUNT(*) FILTER (WHERE c.association_id IS NULL) = 0
                THEN MIN(c.association_id) END AS association_id
    FROM public.v_clubs c
    JOIN (SELECT DISTINCT club_id FROM attributed WHERE club_id IS NOT NULL) ids USING (club_id)
    GROUP BY c.club_id
),
association_names AS (
    SELECT association_id,
           STRING_AGG(DISTINCT association_name, ' / ' ORDER BY association_name) AS association_name,
           COUNT(DISTINCT association_name) AS name_variants
    FROM public.v_associations GROUP BY association_id
),
resolved AS (
    SELECT a.*, ca.association_id, n.association_name,
           CASE WHEN a.match_status <> 'One same-day candidate' THEN 'Destination unresolved'
                WHEN ca.association_id IS NULL THEN 'Club association missing or conflicting'
                WHEN n.association_id IS NULL THEN 'Association lookup missing'
                WHEN n.name_variants <> 1 THEN 'Association name missing or conflicting'
                ELSE 'Resolved current club association' END AS association_resolution
    FROM attributed a LEFT JOIN club_associations ca ON ca.club_id = a.club_id
    LEFT JOIN association_names n ON n.association_id = ca.association_id
),
cumulative_destinations AS (
    SELECT association_id, association_name, match_status, association_resolution,
           COUNT(*) AS conversion_records, COUNT(DISTINCT golfer_id) AS unique_golfers
    FROM resolved
    GROUP BY association_id, association_name, match_status, association_resolution
),
source_exceptions AS (
    SELECT 'Missing conversion date'::text AS exception,
           COUNT(*) AS trial_records, COUNT(DISTINCT golfer_id) AS unique_golfers,
           'No signup date now; trial created OR started before cutoff. Outside conversion totals; historical conversion status unavailable.'::text AS population
    FROM public.trial_golfers
    WHERE sign_up_date IS NULL
      AND (created_at < TIMESTAMP '2026-11-01' OR trial_start_date < DATE '2026-11-01')
    UNION ALL
    SELECT 'Missing conversion date and no usable pre-cutoff trial date', COUNT(*), COUNT(DISTINCT golfer_id),
           'No signup date and neither creation nor trial-start establishes pre-cutoff eligibility; outside conversion totals.'
    FROM public.trial_golfers
    WHERE sign_up_date IS NULL
      AND NOT COALESCE(created_at < TIMESTAMP '2026-11-01' OR trial_start_date < DATE '2026-11-01', FALSE)
    UNION ALL
    SELECT 'Conversion date on/after cutoff', COUNT(*), COUNT(DISTINCT golfer_id),
           'Recorded signup is on/after cutoff; excluded from all cumulative conversion totals.'
    FROM public.trial_golfers WHERE sign_up_date >= TIMESTAMP '2026-11-01'
),
reconciliation AS (
    SELECT
      (SELECT COUNT(*) FROM raw_conversions) AS raw_conversion_records,
      (SELECT COUNT(*) FROM raw_conversions WHERE golfer_id IS NULL) AS conversion_records_missing_golfer_id,
      (SELECT COUNT(*) FROM raw_conversions WHERE golfer_id IS NOT NULL) AS conversion_records_with_golfer_id,
      (SELECT COUNT(*) FROM conversions) AS conversion_events_before_matching,
      (SELECT COUNT(*) FROM raw_conversions WHERE golfer_id IS NOT NULL) -
        (SELECT COUNT(*) FROM conversions) AS duplicate_golfer_day_records_collapsed,
      (SELECT COUNT(*) FROM attributed WHERE match_status = 'One same-day candidate') AS uniquely_matched_conversion_events,
      (SELECT COUNT(*) FROM attributed WHERE match_status = 'No same-day candidate') AS unmatched_conversion_events,
      (SELECT COUNT(*) FROM attributed WHERE match_status = 'Multiple same-day candidates') AS multiple_candidate_conversion_events,
      (SELECT SUM(conversion_records) FROM cumulative_destinations) AS destination_group_records,
      (SELECT COUNT(*) FROM raw_conversions WHERE timing_status = 'Valid') AS timing_classified_records,
      (SELECT COUNT(*) FROM raw_conversions WHERE timing_status <> 'Valid') AS timing_exception_records,
      (SELECT SUM(conversion_records) FROM timing_buckets) AS timing_bucket_records,
      (SELECT SUM(conversion_records) FROM timing_exceptions) AS timing_exception_group_records,
      (SELECT MIN(sign_up_date) FROM raw_conversions) AS actual_earliest_conversion_at,
      (SELECT MIN(sign_up_date) FROM raw_conversions WHERE isfinite(sign_up_date)) AS earliest_finite_conversion_at,
      (SELECT MIN(conversion_date) FROM conversions) AS earliest_destination_conversion_date,
      (SELECT COUNT(*) FROM resolved WHERE match_status = 'One same-day candidate'
         AND association_resolution <> 'Resolved current club association') AS matched_events_with_association_lookup_issue,
      (SELECT COUNT(*) FROM resolved WHERE match_status = 'One same-day candidate'
         AND association_id IS DISTINCT FROM membership_association_id) AS matched_events_with_membership_club_association_difference
)
,
trial_creation_cohorts AS (
SELECT
    statement_timestamp() AS retrieved_at,
    DATE_TRUNC('month', created_at)::date AS trial_created_month,
    COUNT(*) AS trials_created,
    COUNT(*) FILTER (WHERE sign_up_date IS NOT NULL) AS recorded_conversions,
    COUNT(*) FILTER (WHERE sign_up_date IS NULL) AS no_recorded_conversion,
    COUNT(*) FILTER (WHERE sign_up_date::date - trial_start_date = 0) AS same_day,
    COUNT(*) FILTER (WHERE sign_up_date::date - trial_start_date = 1) AS next_day,
    COUNT(*) FILTER (WHERE sign_up_date::date - trial_start_date BETWEEN 2 AND 7) AS days_2_to_7,
    COUNT(*) FILTER (WHERE sign_up_date::date - trial_start_date BETWEEN 8 AND 30) AS days_8_to_30,
    COUNT(*) FILTER (WHERE sign_up_date::date - trial_start_date > 30) AS days_31_plus,
    COUNT(*) FILTER (
        WHERE sign_up_date IS NOT NULL
          AND (trial_start_date IS NULL OR sign_up_date::date < trial_start_date)
    ) AS conversion_lag_unknown_or_invalid,
    COUNT(*) FILTER (WHERE trial_start_date <= CURRENT_DATE - 30) AS trials_observed_at_least_30_days,
    COUNT(*) FILTER (
        WHERE trial_start_date <= CURRENT_DATE - 30
          AND sign_up_date::date - trial_start_date BETWEEN 0 AND 30
    ) AS conversions_within_30_days_observed_cohort,
    COUNT(*) FILTER (
        WHERE trial_start_date::date <> created_at::date
    ) AS trial_start_differs_from_creation_date
FROM public.trial_golfers
WHERE created_at < TIMESTAMP '2026-11-01'
GROUP BY DATE_TRUNC('month', created_at)::date
ORDER BY trial_created_month
),
trial_current_pools AS (
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
FROM trial_memberships
)

SELECT 'trial_monthly_history'::text AS dataset, 'manifest'::text AS record_type, statement_timestamp() AS extracted_at,
 current_database() AS source_database, current_setting('TimeZone') AS reporting_timezone,
 '{"period_start": null, "period_start_meaning": "All retained event history before exclusive end", "period_end_exclusive": "2026-11-01", "population": "All trial rows; each created/start/signup event selected independently", "counting_unit": "Trial source records per event type", "filters": ["Event timestamp < 2026-11-01; no GC filter; missing event dates excluded for that event"], "timezone": "Use reporting_timezone envelope; do not change database session timezone", "date_arithmetic": "sign_up_date::date - trial_start_date::date; calendar days, not completed 24-hour intervals", "association_attribution": "October preserves membership association_id; cumulative association view resolves current destination club association after matching; neither proves association at conversion"}'::jsonb AS row_data
UNION ALL
SELECT 'trial_monthly_history'::text, 'data'::text, statement_timestamp(), current_database(), current_setting('TimeZone'), to_jsonb(r) FROM data_0 r
UNION ALL
SELECT 'ytd_trial_destinations'::text AS dataset, 'manifest'::text AS record_type, statement_timestamp() AS extracted_at,
 current_database() AS source_database, current_setting('TimeZone') AS reporting_timezone,
 '{"period_start": "2026-01-01", "period_start_meaning": "Inclusive", "period_end_exclusive": "2026-11-01", "population": "All recorded January–October 2026 signups with nonnull golfer_id", "counting_unit": "Distinct golfer_id + signup calendar date", "filters": ["Original same-day candidate matching unchanged", "m.association_id <> 237", "c.is_test = No", "Single candidate only attributed; no GC-only filter"], "timezone": "Use reporting_timezone envelope; do not change database session timezone", "date_arithmetic": "sign_up_date::date - trial_start_date::date; calendar days, not completed 24-hour intervals", "association_attribution": "October preserves membership association_id; cumulative association view resolves current destination club association after matching; neither proves association at conversion"}'::jsonb AS row_data
UNION ALL
SELECT 'ytd_trial_destinations'::text, 'data'::text, statement_timestamp(), current_database(), current_setting('TimeZone'), to_jsonb(r) FROM data_1 r
UNION ALL
SELECT 'trial_conversion_timing'::text AS dataset, 'manifest'::text AS record_type, statement_timestamp() AS extracted_at,
 current_database() AS source_database, current_setting('TimeZone') AS reporting_timezone,
 '{"period_start": null, "period_start_meaning": "All retained source history; no assumed program launch date", "period_end_exclusive": "2026-11-01", "population": "All retained signup records before cutoff, including missing golfer IDs", "counting_unit": "Trial source conversion records", "filters": ["Actual trial_start_date; signup calendar date minus trial-start calendar date", "Only nonnegative finite elapsed days enter buckets", "Share denominator = valid timing source rows; distinct golfers exclude NULL IDs"], "timezone": "Use reporting_timezone envelope; do not change database session timezone", "date_arithmetic": "sign_up_date::date - trial_start_date::date; calendar days, not completed 24-hour intervals", "association_attribution": "October preserves membership association_id; cumulative association view resolves current destination club association after matching; neither proves association at conversion"}'::jsonb AS row_data
UNION ALL
SELECT 'trial_conversion_timing'::text, 'data'::text, statement_timestamp(), current_database(), current_setting('TimeZone'), to_jsonb(r) FROM timing_buckets r
UNION ALL
SELECT 'trial_conversion_timing_exceptions'::text AS dataset, 'manifest'::text AS record_type, statement_timestamp() AS extracted_at,
 current_database() AS source_database, current_setting('TimeZone') AS reporting_timezone,
 '{"period_start": null, "period_start_meaning": "All retained source history; no assumed program launch date", "period_end_exclusive": "2026-11-01", "population": "Recorded conversions before cutoff; exclusive exception priority", "counting_unit": "Trial source conversion records", "filters": ["Priority: nonfinite signup, missing trial start, nonfinite trial start, negative elapsed days", "Sum exceptions plus valid buckets = raw conversions"], "timezone": "Use reporting_timezone envelope; do not change database session timezone", "date_arithmetic": "sign_up_date::date - trial_start_date::date; calendar days, not completed 24-hour intervals", "association_attribution": "October preserves membership association_id; cumulative association view resolves current destination club association after matching; neither proves association at conversion"}'::jsonb AS row_data
UNION ALL
SELECT 'trial_conversion_timing_exceptions'::text, 'data'::text, statement_timestamp(), current_database(), current_setting('TimeZone'), to_jsonb(r) FROM timing_exceptions r
UNION ALL
SELECT 'trial_conversion_source_exceptions'::text AS dataset, 'manifest'::text AS record_type, statement_timestamp() AS extracted_at,
 current_database() AS source_database, current_setting('TimeZone') AS reporting_timezone,
 '{"period_start": null, "period_start_meaning": "All retained source history; no assumed program launch date", "period_end_exclusive": "2026-11-01", "population": "Source rows outside applicable conversion populations", "counting_unit": "Trial source records", "filters": ["Missing signup is not a conversion and cannot be included in a dated conversion population", "Missing-date status observed at extraction, not certified as of cutoff"], "timezone": "Use reporting_timezone envelope; do not change database session timezone", "date_arithmetic": "sign_up_date::date - trial_start_date::date; calendar days, not completed 24-hour intervals", "association_attribution": "October preserves membership association_id; cumulative association view resolves current destination club association after matching; neither proves association at conversion"}'::jsonb AS row_data
UNION ALL
SELECT 'trial_conversion_source_exceptions'::text, 'data'::text, statement_timestamp(), current_database(), current_setting('TimeZone'), to_jsonb(r) FROM source_exceptions r
UNION ALL
SELECT 'cumulative_trial_destination_associations'::text AS dataset, 'manifest'::text AS record_type, statement_timestamp() AS extracted_at,
 current_database() AS source_database, current_setting('TimeZone') AS reporting_timezone,
 '{"period_start": null, "period_start_meaning": "All retained source history; no assumed program launch date", "period_end_exclusive": "2026-11-01", "population": "All retained signup events with nonnull golfer_id before cutoff", "counting_unit": "Distinct golfer_id + signup calendar date", "filters": ["Same candidate matching as October; no GC-only filter", "association_id = destination club CURRENT association from v_clubs after matching", "Do not use membership association as a silent fallback", "Multiple/no candidate groups retain NULL association"], "timezone": "Use reporting_timezone envelope; do not change database session timezone", "date_arithmetic": "sign_up_date::date - trial_start_date::date; calendar days, not completed 24-hour intervals", "association_attribution": "October preserves membership association_id; cumulative association view resolves current destination club association after matching; neither proves association at conversion"}'::jsonb AS row_data
UNION ALL
SELECT 'cumulative_trial_destination_associations'::text, 'data'::text, statement_timestamp(), current_database(), current_setting('TimeZone'), to_jsonb(r) FROM cumulative_destinations r
UNION ALL
SELECT 'trial_conversion_reconciliation'::text AS dataset, 'manifest'::text AS record_type, statement_timestamp() AS extracted_at,
 current_database() AS source_database, current_setting('TimeZone') AS reporting_timezone,
 '{"period_start": null, "period_start_meaning": "All retained source history; no assumed program launch date", "period_end_exclusive": "2026-11-01", "population": "Raw source conversions and deduplicated matching events", "counting_unit": "Counts explicitly named by unit", "filters": ["Raw conversions = valid timing + timing exceptions", "Raw conversions = missing-ID rows + duplicate golfer/day rows collapsed + matching events", "Matching events = unique + unmatched + multiple-candidate events"], "timezone": "Use reporting_timezone envelope; do not change database session timezone", "date_arithmetic": "sign_up_date::date - trial_start_date::date; calendar days, not completed 24-hour intervals", "association_attribution": "October preserves membership association_id; cumulative association view resolves current destination club association after matching; neither proves association at conversion"}'::jsonb AS row_data
UNION ALL
SELECT 'trial_conversion_reconciliation'::text, 'data'::text, statement_timestamp(), current_database(), current_setting('TimeZone'), to_jsonb(r) FROM reconciliation r
UNION ALL
SELECT 'trial_cohorts'::text, 'manifest'::text, statement_timestamp(), current_database(), current_setting('TimeZone'), '{"period_start": null, "period_end_exclusive": "2026-11-01", "population": "Trials created before November; conversion outcomes observed through extraction", "counting_unit": "Trial source rows grouped by creation month; distinct golfers where present", "filters": ["Created_at < 2026-11-01; no GC-only filter"], "timing_definition": "Legacy cohort diagnostic fields preserved; requested 5 timing groups remain in trial_conversion_timing", "timezone": "Database session; see reporting_timezone"}'::jsonb
UNION ALL
SELECT 'trial_cohorts'::text, 'data'::text, statement_timestamp(), current_database(), current_setting('TimeZone'), to_jsonb(r) FROM trial_creation_cohorts r
UNION ALL
SELECT 'current_trial_pools'::text, 'manifest'::text, statement_timestamp(), current_database(), current_setting('TimeZone'), '{"period_start": null, "period_end_exclusive": null, "snapshot": "statement_timestamp", "population": "Current association237 memberships at explicitly non-test clubs, Active/Inactive statuses", "counting_unit": "Distinct golfers; Active takes precedence over Inactive", "filters": ["No October creation-date filter; all retained qualifying memberships"], "timezone": "Database session; see reporting_timezone"}'::jsonb
UNION ALL
SELECT 'current_trial_pools'::text, 'data'::text, statement_timestamp(), current_database(), current_setting('TimeZone'), to_jsonb(r) FROM trial_current_pools r;
