# Extended trial export through October 2026

Run [26_extended_trials_through_october_2026.sql](26_extended_trials_through_october_2026.sql) as one statement in DBeaver on the confirmed reporting connection. Export all results with headers, complete JSON text, and the existing CSV settings as **trials_extended_through_october_2026.csv**. Preserve the database session timezone; the prior export reports America/New_York.

The query uses the confirmed fields already queried successfully: `trial_golfers.golfer_id`, `created_at`, `trial_start_date`, `sign_up_date`; membership creation/club/association fields in `v_golfer_clubs`; and club/association lookup fields already used in the dashboard exports. It does not invent a trial conversion flag, payment field, program launch date, or historical association table.

## Output

The envelope stays `dataset, record_type, extracted_at, source_database, reporting_timezone, row_data`. Each dataset has a manifest describing its date range, population, counting unit and filters. Manifest rows are metadata, not metrics.

| Dataset | What it contains |
|---|---|
| trial_monthly_history | Original October creation/start/signup events; original CTE unchanged |
| ytd_trial_destinations | Original October same-day candidate matches; original CTE unchanged despite legacy YTD name |
| trial_conversion_timing | Seven requested elapsed-day buckets, counts, distinct golfers, valid-conversion shares |
| trial_conversion_timing_exceptions | Missing/nonfinite trial starts, nonfinite conversion dates, and negative elapsed days; exclusive categories |
| trial_conversion_source_exceptions | Missing signup dates and post-cutoff signups, outside cumulative conversion totals |
| cumulative_trial_destination_associations | All retained pre-November conversions, grouped by destination club's current association and match status |
| trial_conversion_reconciliation | Raw counts, duplicate/missing-ID bridge, matched/unmatched/multiple counts, timing totals and earliest dates |

## Timing definition and exception populations

Timing uses **sign_up_date::date minus trial_start_date::date**. This is the existing project's calendar-day arithmetic, not a count of completed 24-hour periods. No substitution of `created_at` for trial start occurs. The requested buckets differ from the older project display (same day, next day, 2–7, 8–30, 31+); this export implements the user's explicit new bucket request. No independent database-owned bucket definition has been established.

All timing conversions are retained source rows with signup before November 1, 2026, including missing golfer IDs. Distinct golfers exclude NULL IDs. Shares divide by source conversion records with valid nonnegative finite elapsed days. Empty buckets return zero counts; shares are NULL when no valid conversions exist.

Timing exceptions have a mutually exclusive priority: nonfinite signup date, missing trial start, nonfinite trial start, conversion before trial start. Valid timing plus those exceptions equals all raw pre-cutoff conversion rows. Nonfinite dates are reported rather than silently coerced. Actual earliest dates are returned alongside the earliest finite conversion timestamp.

A missing signup cannot be assigned to a dated conversion population. The export therefore reports such source rows separately: those created OR started before cutoff, and those without either date establishing pre-cutoff eligibility. They do not enter timing/destination conversion totals. Their missing-date status is observed now, not a reconstructed October 31 status. Post-cutoff signups are another separate exclusion.

## Destination definition and counting bridge

Matching is unchanged: a distinct golfer/signup calendar date is compared to memberships created on that same day, excluding membership association 237 and clubs not explicitly non-test. Candidate identity retains exactly the original club/association/name/category/type/provider columns. No Active-only or GC-only filter is added. Multiple candidates remain unresolved even when they happen to belong to the same association.

The new cumulative association section resolves the **current destination club association** from `v_clubs.association_id` only after a single candidate is identified. The original October section still returns the membership association ID, unchanged. Neither is verified historical association-at-conversion. Reconciliation reports disagreements between the membership association and current club association. Club association conflicts and missing/conflicting names are flagged; lookup grouping prevents duplicate lookup rows from multiplying counts. Unmatched/multiple-candidate groups have NULL associations.

Destination events exclude missing golfer IDs and collapse duplicate same-golfer/same-calendar-day rows, exactly as October matching did. They can differ from raw timing conversion-record counts. Required bridges:

- Raw conversion rows = missing-golfer-ID rows + collapsed duplicate golfer/day rows + destination events before matching.
- Destination events = uniquely matched + unmatched + multiple-candidate events = sum of cumulative association group conversion counts.
- Raw conversion rows = timing-classified records + timing exception records = sum of bucket counts + sum of exception group counts.

Distinct golfer counts across dates/associations can overlap; do not sum group distinct counts into a cumulative unique total.

## Previous-export references

The previously inspected October export contained 12,665 creation records and 5,076 signup events. The supplied reference for same-day GC candidate matches is 4,199; GC classification uses the separately approved club-ID list. Unmatched is 206 and multiple-candidate is 22. Reconcile reruns to these references and document any differences; do not hard-code the results. Source records and membership attribution are live and may change between runs. These references are not guaranteed database invariants.

## Execution status

The extended SQL is prepared, with the two October CTEs verified identical to the executed original. It has not been run against the database. **A cumulative exported CSV cannot be produced from the October-only CSV.** Run the extended query in DBeaver and supply its result. No website data has been changed or published by this query-extension work.

The local helper `scripts/unpack_dashboard_bundles.py` recognizes all seven dataset names. It preserves manifests in the original raw CSV and records source metadata/counts when splitting data rows. The raw export remains authoritative for detailed manifest definitions.
