# GHIN and Handicapping Dashboard: export process and rulebook

Prepared November 2, 2026. This is the operating guide for the eight-query package in [sql/dashboard_refresh](../sql/dashboard_refresh/README.md). It preserves the approved definitions in [the knowledge base](KNOWLEDGE_BASE.md) and [data intake rules](../REAL_DATA_INTAKE.md). It replaces the earlier 16-export recommendation, not those metric definitions.

## The short version

Run eight SQL files in DBeaver. Export each result to one CSV. Give Codex the eight files plus the export log. Codex checks and processes them before updating the local dashboard.

For this refresh, monthly charts end on **October 31, 2026**. Current membership/subscriber counts show the state when the query runs. The Scores Explorer counts scores from January 1 through the time its query runs. Those are different reporting periods and must be labeled separately.

The SQL has been prepared and reviewed locally. It has not been run against the reporting database. The first run must pass the checks below before replacing dashboard data.

## What you run

| Order | Export | What it supplies | Time covered |
|---|---|---|---|
| 1 | Memberships | Membership totals, unique golfers, composition, associations/clubs, NH, exact Index statistics, Explorer filters, detailed GC acquisition analysis | All creation dates and membership statuses; current record values |
| 2 | Acquisition history | Monthly new-golfer comparisons, with AGA/international and Regular/Junior/Unclassified selections | January 2020–October 2026 |
| 3 | Scores: totals and posting mix | Score totals, associations, posting methods, applications/API and holes | January 2025–October 2026 |
| 4 | Scores: demographics | Score counts by gender, age and current primary-club details | January 2025–October 2026 |
| 5 | Score participation | Zero, 1–7 and 8+ score bands for current active non-trial and trial golfers | January 1, 2026 through query execution |
| 6 | Trials | Monthly events, creation cohorts, current trial pools and candidate conversion destinations | Retained history/current state; destination matching January–October 2026 |
| 7 | Enhanced GPS | Current subscribers and date checks, monthly activity, tenure and explicit renewal-status labels | Retained history/current state |
| 8 | Challenges | Challenge counters plus challenge/course names | Retained challenge records/current values |

The exact filenames and clickable SQL files are in [the package index](../sql/dashboard_refresh/README.md).

## Why eight instead of sixteen

- Monthly posting mix and demographics remain separate. Combining them creates a much larger grouping workload. Evan agreed to keep them separate; the combined query has been removed from the runnable package. Run each heavy export by itself. These established separate queries are still substantial database work, with runtime unverified for this refresh.
- Trial and non-trial participation now share one YTD score aggregation. A population column identifies each pool.
- The four Trials results travel in one file. The four GPS results travel in one file. The two Challenges results travel in one file. Their sections remain separate so counts cannot multiply through unrelated joins. Bundling reduces export steps; it does not eliminate all underlying source-table work.
- Acquisition remains its own small aggregate export. The membership file contains the underlying Creation Dates, but the existing historical acquisition importer expects this aggregate contract. Removing it would require a validated local historical aggregation step.

Thus eight is a practical working package, not a proven mathematical minimum. Combining every topic into one enormous file would save clicks but complicate retries, checks and processing. No runtime improvement is claimed until measured on the reporting database.

## Evan's DBeaver steps

1. Connect to **Production BigData**, not Production Secondary. Confirm the server/connection mapping; a database named `ghin2020pilot` alone does not prove which environment it is.
2. Create a Windows folder such as `C:\Users\V-EBelfi\GHIN_refresh_2026-11-02`.
3. Open `01_memberships.sql` in DBeaver. Run the **whole file as one statement**. Repeat separately for files 02–08.
4. From each result, choose **Export Data → CSV → Query the database**. This runs the SELECT again to export all matching rows. The export run, rather than the preview, is the source we use.
5. Set UTF-8, comma delimiter, column headers, double-quote quoting, empty NULL string, and **Format numbers unchecked**. Do not truncate long text/JSON values. Use the filename in the package index.
6. Export **all rows**. A preview grid with 200 rows is not the complete export. Do not add `LIMIT`, an Active-only condition, or an October-only condition to make a file smaller.
7. Log the connection, database timezone, export start/end times, row count and filename. Use [the export-log template](../sql/dashboard_refresh/export_log_template.csv). If DBeaver executes in batches, preserve all extraction timestamps; do not describe it as one frozen snapshot.
8. Copy the finished folder through Windows Explorer to Mac Downloads. Keep CSVs intact. Do not open and resave the large membership file in Excel.
9. Give Codex the files and log. Codex validates the exports, updates the processing inputs, builds the dashboard locally, and reports what changed.

Run exports one at a time, especially Memberships, both monthly score exports and Score Participation. If a monthly score export exceeds available resources, split its date bounds into documented, nonoverlapping months or years; keep all other eligibility and attribution rules unchanged. Log each part, check complete coverage, and combine only during local processing. Do not add LIMIT or drop dimensions to force it through. This fallback creates more than eight files.

If an export fails, rerun that export and record its new time. A partial file must not be used. Existing good dashboard data remains until the replacement passes checks.

## Dates: the rules that prevent misleading comparisons

| Kind of number | Rule for November 2 |
|---|---|
| Current memberships, golfers, trial pools, GPS subscribers | As extracted on the actual run date/time; not an October 31 certification |
| Monthly activity and acquisition charts | Include dates before November 1; exclude partial November |
| Score Explorer participation | January 1 through execution time; preserve its separate current-YTD definition |
| Trial creation-cohort conversion rates | Group by creation month; conversion outcome is observed through extraction, giving older cohorts more follow-up |
| Prior-year comparison | Match the same completed months or explicitly matched date window |

Queries use the database session timezone. Record it; do not silently change it to the Mac's timezone. Separate exports can reflect slightly different live states. Current statuses, affiliations, ages and Index values cannot reconstruct historical month-end snapshots.

Trials and GPS history sections deliberately retain their full available history, which may contain November activity. Processing must exclude those partial-month rows from completed-month displays while retaining them in raw staging.

For the next refresh, update the filenames/log and review the date bounds together: acquisition's exclusive upper bound, both monthly score queries' bounds (`params` for posting mix and the score filter for demographics), trial conversion destinations' start/end, and participation's year start. The November package fixes completed activity at `< 2026-11-01`; it does not automatically advance next month. GPS/trial tenure and current pools continue to use actual execution time.

At year rollover, verify that the current/previous-year score extract tables still cover both requested reporting years. Preserve validated older score history rather than overwriting it with a shorter export.

## Counting and classification rules

### Memberships and golfers

- The main membership number counts qualifying **membership records**. One person with three memberships counts as three memberships and one unique golfer.
- Additional memberships = memberships minus unique golfers. Multi-membership golfers counts people with more than one qualifying membership once each.
- Apply the selected filters first, then calculate distinct golfers. Do not sum overlapping association or member-type distinct counts into a national total.
- The export retains all statuses. Current membership displays select Active during processing. Acquisition uses all statuses so now-inactive golfers remain eligible.
- Membership IDs must be present and unique after joins. Duplicates block installation pending investigation. Missing golfer joins and unresolved associations must be reported.
- Regular means source Standard. Preserve Junior and Unclassified. All Members includes those three non-trial populations.
- Association 237 is a separate trial membership population. Exclude that membership row from main membership totals; keep the same person's qualifying non-trial memberships.

### Association, access and GC scope

- Qualifying clubs must explicitly have `is_test = 'No'`. Known test associations are excluded; unresolved association eligibility stays separate for audit.
- AGA means a non-test membership association whose parent federation is United States Golf Association. This includes Golf PR and excludes Guam. It is affiliation, not residence. Do not add `is_aga` or association-status filters.
- International requires a known, nonblank federation other than USGA. Unknown federation is not International. All Associations deduplicates golfers across qualifying AGA and international memberships.
- Match GC using the approved club-ID list. Names alone do not establish GC status. GC clubs use Public access and the separate GC Clubs category.
- Type 2 and Type 3 are Public. Preserve recorded club type and raw category. Affiliate/WORE is Public; it does not overwrite recorded Type 1/2/3. Unknown Type 1 access remains Unknown. Public/Semi-Private/Resort/Municipal/Military roll up to Public; preserve their detailed categories.
- Use the full detailed access/category precedence in the intake rules. Do not replace it with a new SQL name-matching shortcut.

### Handicap Index and acquisition

- NH means the source explicitly says NH. Include it in membership counts; show No Index; exclude it from numeric Index averages/medians. Missing details are Unknown, not NH or zero.
- Exact average/median statistics use unique golfers with valid numeric Index values, independently of the Explorer's Memberships/Unique Golfers toggle. Preserve plus-handicap arithmetic. Values above 54.0 remain excluded from valid Index statistics and reported for review; conflicting golfer Index values must be investigated.
- New golfer timing uses `v_golfer_clubs.golfer_creation_date`. Do not substitute golfer-record `created_at`, membership creation, status date, conversion date or first score.
- Current membership affiliation does not prove acquisition channel or affiliation at creation. Preserve the approved 2020 acquisition adjustment and zero GC acquisition in 2020–2021. Never silently remove those display rules during refresh.
- GC joiners and new-to-GHIN golfers have different definitions. Do not substitute one into the other's chart.

### Scores, trials and GPS

- Score totals exclude deleted and penalty records. Include trials, UnderReview, Temporary, competition and unknown statuses/types under existing rules. Do not restore the older H/A/T-only filter.
- Monthly scores count score records by `created_at`. Holes labels describe those records; they are not an independently verified count of rounds played.
- Monthly score attribution uses current primary-club/association and member-type records. It is not historical affiliation at posting. Retain unknown, ambiguous and test buckets for reconciliation; displayed All Associations excludes tests and retains non-test unresolved/trial buckets under the approved score rules.
- Regular and Junior score flags can overlap. Count All Members once; never add the two populations to get All.
- Participation uses the established base-table active eligibility query, which attributes association via club. Explorer attributes come from the membership export, using its membership-association rules. Reconcile rather than assume those source populations are identical.
- Participation includes zero scores. Trial and non-trial pools can overlap if a person has both kinds of active membership; do not sum their golfer counts into one deduplicated total. Trial participation counts all qualifying YTD scores for those golfers, not just scores flagged trial or scores during trial dates.
- Trial signup counts, creation-cohort conversion rates and current trial pools answer different questions. Same-day membership matching gives candidate destinations; it does not prove the actual destination. Explain unmatched/ambiguous candidates. Reconcile at the correct grain: trial event rows versus distinct golfer/date candidate records may differ.
- GPS activity rows are not verified paid purchases or historical active-subscriber counts. Tenure is time since the earliest retained initial subscription date, not proven continuous enrollment. Explicit renewal-status labels do not establish actual auto-renew enrollment.
- Challenge golfer/score counters belong to each challenge. They are not unique golfers or unique scores across all challenges. Preserve deleted-status exclusions and verified AGA/test rules in processing. Course name matches can be ambiguous; they must not multiply the challenge counters.

## What Codex does after receiving the files

1. Preserve original CSVs in a new dated private raw folder; record checksums, sizes, row counts, connection and extraction windows. Never overwrite a previous raw extract.
2. Split the labeled Trials/GPS/Challenges CSVs locally using [unpack_dashboard_bundles.py](../scripts/unpack_dashboard_bundles.py). The `dataset` column identifies a section; `row_data` contains its original fields. Manifest rows are metadata, not metrics. An empty section is explicitly listed in the unpack report; it must not silently become zero or disappear.
3. Split participation by its population column. Validate uniqueness by `(population, golfer_id)`, not golfer ID alone.
4. Keep posting mix and demographics as separate inputs, using their established column contracts. Both describe the same underlying scores; never add their totals together. Reconcile each by month/scope/population and document differences caused by separate live extraction times.
5. Update the existing builders' dated file paths, completed-month bounds, source metadata and old fixed-total assertions. The new files are **not drop-in inputs for the old October scripts**. Preserve acquisition corrections and validated older history.
6. Stage large membership data with bounded-memory/disk-backed processing. Keep golfer/membership IDs local. Publish only the existing anonymous aggregates/patterns required by the dashboard.
7. Run the acceptance checks below. Rebuild locally only after checks pass; inspect the affected views and date labels. Report source gaps and material differences. Publishing remains a separate action.

Example bundle unpacking command, run from the project folder after replacing input paths:

```sh
python3 scripts/unpack_dashboard_bundles.py --output /tmp/ghin-refresh-unpacked /path/to/trials_2026-11-02.csv /path/to/gps_2026-11-02.csv /path/to/challenges_2026-11-02.csv
```

The output directory must be new. A successful unpack produces a `SUCCESS` file and `unpack_manifest.json`. Unpacking checks file structure; it does not certify the dashboard calculations. If it fails, do not use its partial output.

## Acceptance checks before replacing dashboard data

- All eight exports completed. Filenames, sizes and row counts agree with the log; JSON cells are complete. Multiple extraction timestamps are recorded and reviewed.
- Membership IDs are nonempty and unique; missing golfer/association joins, test exclusions and unresolved scope are quantified. The approved scope/population totals reconcile to source records. Snapshot totals are not forced to match last month's values.
- Acquisition has the expected reporting months through October and distinct counts for each scope/population. Compare against membership-derived cohorts and document differences from timing or source state. Preserve manual corrections separately from raw counts.
- Monthly scores cover January 2025–October 2026. For each month and selected scope/population, sum of method/application/demographic breakdowns reconciles to the same score count. Tests, unknown labels and ambiguous mappings remain visible in validation. Compare old/new overlapping months and explain material drift; do not require changing live data to match an earlier extract exactly.
- Participation counts are nonnegative integers with no duplicate population/golfer pair. Zero + 1–7 + 8+ equals each pool's golfer count. Reconcile membership matches and retain unmatched golfers with their actual score bands; never assume unmatched means zero.
- Trial cohort partitions reconcile; monthly signup events and destination candidates reconcile only after accounting for their different grains and missing IDs. Current active/inactive pools apply active precedence.
- GPS active date groups sum to active-flagged unique golfers. Explicit renewal groups reconcile to their active pool. Validate tenure missing/invalid dates and overlapping canceled/active cohorts.
- Challenges have one counter row per challenge ID. Course lookup ambiguity cannot inflate counts. Verify AGA/test eligibility against the refreshed membership/association lookup.
- Recalculate shares from counts. Preserve missing values as missing. Confirm October endpoints, prior-year matched periods, current snapshot labels, selectors, Explorer totals and Index statistics in the rebuilt local dashboard.

## Other reports we still need

These are source gaps, not evidence that the data cannot be queried. The eight queries cover the dashboard's established operational database extracts. They do not establish a complete replacement for the following sources:

| Data | Needed source / next step |
|---|---|
| GHIN app usage | GA4 exports and certified operational app totals; database membership counts do not measure app use |
| Historical active memberships | Certified snapshots/billing history for each period; today's status cannot reconstruct past totals |
| Retention and recovery | Agreed renewal/reactivation definitions plus historical membership events or certified reports |
| Billing and GC month-end history | Existing certified billing series and GC month-end reports, or a separately validated database replacement |

Keep a missing section dated or marked unavailable. Do not relabel an old figure as November just because other sections were refreshed.
