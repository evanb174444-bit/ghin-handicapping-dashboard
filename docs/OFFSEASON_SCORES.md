# Offseason score posting

Local view: Scores → Offseason. November 16 intake is installed locally; no publication is authorized by this intake.

## Definition and dates

Offseason is the stored boolean `public.scores.offseason IS TRUE`. Evan corrected the earlier calendar-based assumption. Do not infer classification from AGA inactive dates or a shared winter window. The current export has 29,320 score rows, all with score type I. The source flag, not an assumed meaning of that type code, controls eligibility.

Group by exported `created_at` (posting timestamp); retain `played_at` separately in private source files. Timestamp values are preserved without timezone conversion because the export did not include timezone metadata. Eligible AGA posting dates run October 26–November 16, 2026. The latest day/week/month is partial; chart and table labels stop at the loaded boundary. This export does not establish complete historical flag coverage.

## Matching and exclusions

The original CSV is archived in `data/raw/offseason/2026-11-16/`. The matched CSV retains all 29,320 original score IDs exactly once. Raw files and golfer identifiers remain local.

- Exclude 757 deleted records; no penalty records were present. Keep UnderReview under existing score rules.
- Use the November 3 membership export's `primary_club_id`; map that club to its AGA. Do not arbitrarily select another membership.
- Eligible records: 28,563. Of those, 28,380 match 57 AGAs, 24 international associations, 25 the trial association, and 134 remain unresolved.
- Unresolved: 123 scores lack a golfer in the older snapshot, five lack a primary club, six have ambiguous club metadata.
- The main AGA view includes 28,380 scores from 21,369 unique golfers. No test-mapped scores were found. Counts include Regular, Junior and unclassified records. Attributes describe November 3 affiliation, not necessarily affiliation at posting.

## Anonymous presentation data

`data/processed/offseason_scores.json` is embedded as `OFFSEASON_SCORES_DATA`. It contains only association metadata, daily score counts, precomputed distinct-poster counts, source hashes and aggregate reconciliation details. No score IDs or golfer IDs are embedded.

`rows` holds one record per date/AGA for the loaded 22-day window, including explicit zeros. Dates outside the loaded range remain unavailable. Year/AGA selections aggregate the same daily records. Weeks start Monday. Distinct golfers are calculated from private IDs separately for each day/week/month and the selected year/AGA; daily unique counts must never be summed into a period's unique total. The sortable AGA table includes scores, distinct posters and scores per golfer.

There is no share-of-all-scores metric or denominator in this view, per Evan's instruction. Matching exceptions and source details are in the shared collapsed footer.

## Validation and refresh

`python3 scripts/validate_offseason_dashboard.py` independently reconciles the private matched rows to the public counts and unique-poster rollups. `node scripts/check_offseason_scores.cjs` runs that check, then verifies all 60 association selections (All plus 59 AGAs) in day/week/month views. Source matching audit: `reports/offseason_membership_matching_2026-11-16.json`.

For the next intake, preserve the explicit offseason flag and established score exclusions, obtain a current membership snapshot if possible, reconcile unmatched records, and update the anonymous daily and distinct-poster rollups together. Do not broaden source definitions or publish automatically.


## Course locations — November 16, 2026

Imported `offseason_course_locations_2026-11-16.csv.csv`; SHA-256 `fb4464b9d03bd84c797fa3f3a3a21f7415f3a38a0b7c7a74ea4ed56acb56327d`. The 4,217 returned rows contain 3,877 distinct course IDs; alternate-number join duplicates agree on the direct-ID fields. All 3,762 nonblank eligible course IDs match `crs_courses.id`, and all normalized course names match. Do not use the alternate course-number interpretation.

The local location table groups actual course state/province, with expandable course detail and current golfer-AGA filtering. Exact state-level and course-level unique golfers are computed from private record sets, not summed from lower-level aggregates. All 28,380 scores reconcile. Unknown location retains 41 scores / 36 golfers. Two scores lack a course ID and are displayed under “Course ID not supplied”; they are excluded from distinct-course counts. Canadian and Australian regions retain their country labels. Validation: `python3 scripts/validate_offseason_locations.py`. No publication performed.
