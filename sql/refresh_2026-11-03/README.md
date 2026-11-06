# November 3: one GHIN + GC export handoff

**Snapshot date: actual query execution on November 3, 2026. Completed monthly activity: through October31,2026 (`< 2026-11-01`).** October13 is the date of the old national membership source, not today's cutoff. This package leaves the old source files and dashboards untouched.

Start with the [shared contract](/Users/EvanBelfi/Documents/Projects/USGA-GC-Dashboard/SHARED_DASHBOARD_REFRESH.md) for approved differences between the two dashboards. This dated package advances that plan: Trials group06 is now consolidated in SQL. It still needs database execution, validation and importer adaptation; no unattended shared refresh runner is claimed.

## Run order and filenames

| Run | SQL | Output CSV | Coverage |
|---|---|---|---|
| 01 | [Membership detail](01_memberships.sql) | memberships_2026-11-03.csv | All dates/statuses; current memberships, people, Index, demographics, associations, clubs, NH and Explorer attributes |
| 02 | [Acquisition history](02_acquisition_history.sql) | acquisition_history_2026-11-03.csv | Jan2020–Oct2026 new-to-GHIN aggregates |
| 03 | [Scores: totals and posting mix](03_scores_posting_mix.sql) | scores_posting_mix_2026-11-03.csv | Jan2025–Oct2026 score totals/associations/method/application/API/holes |
| 04 | [Scores: demographics](04_scores_demographics.sql) | scores_demographics_2026-11-03.csv | Jan2025–Oct2026 gender/age/current-club breakdowns; keep separate from03 |
| 05 | [Score participation](05_score_participation.sql) | score_participation_2026-11-03.csv | Current Active trial/nontrial golfers; scores Jan1 through execution, includes zero scores |
| 06 | [Full Trials bundle](06_trials.sql) | trials_full_refresh_2026-11-03.csv | Nine datasets; historical monthly events, Jan–Oct candidate destinations, cumulative timing/associations, exceptions/reconciliation, creation cohorts and current pools |
| 07 | [GPS bundle](07_gps.sql) | gps_2026-11-03.csv | Subscriber/date reconciliation, retained monthly activity, tenure, explicit renewal-status labels |
| 08 | [Challenges bundle](08_challenges.sql) | challenges_2026-11-03.csv | Current challenge counters and challenge/course names; participation counts, not unique people |
| 09* | [GC rich snapshot](09_gc_snapshot.sql) | gc_current_snapshot_2026-11-03.csv | GC-specific identity/renewal/history detail and approved Archived exclusions |

**Eight core exports for today's national GHIN update; group09 is supplementary when a new GC snapshot is required.** The November2 GC snapshot is already archived and validated; keep it if retaining its November2 as-of date. Do not call that a November3 snapshot. National01 cannot silently replace GC09, or vice versa: the fields, status exclusions and association attribution differ. No need to rerun the already delivered trial query27 or raw challenge-counter query in addition to groups06/08 unless validation requires it.

All files are read-only SELECTs. SQL source checksums are recorded in [sql_sha256.json](sql_sha256.json). Use the actual extraction date in future output filenames; filenames do not certify snapshot timing.

## DBeaver instructions

1. Confirm **Production BigData**, not Production Secondary. `ghin2020pilot` alone does not prove the environment. Preserve the session timezone, recording it in [export_log.csv](export_log.csv). Previous Trials exports used America/New_York; GC snapshot capture is UTC while its source timestamp semantics remain unconfirmed.
2. Open a SQL file. **Select the entire statement (Ctrl+A) and execute it (Ctrl+Enter).** Running just its trailing SELECT causes the earlier `data_0 does not exist` error. Do not execute only a highlighted fragment.
3. Export results using **Export Data → CSV → Query the database**, all rows. This reruns the SELECT: record export timing, not just preview timing. Run one heavy export at a time; do not launch both score queries together.
4. UTF-8, comma, column headers, double quotes, empty NULL string, number formatting off, no long-text/JSON truncation. Keep the output filename above. Do not use Excel to resave, add LIMIT, truncate the grid, or add Active/October-only filters.
5. Fill connection, timezone, start/end and row count in the log. Copy complete CSVs and log to Mac Downloads. Preserve separate query/batch timestamps; separate live reads are not a frozen transaction.
6. If a monthly score export fails on resources, split its date bounds into documented, nonoverlapping months/years; change no eligibility or grouping fields. Supply all pieces and their log entries. More than eight resulting files is acceptable for a safe complete export.

## Trials group06: exactly what changed

Based on the already executed Trials query family, retaining the five GC timing groups **0 /1 /2–7 /8–30 /31+ days**, source `trial_start_date`, `sign_up_date` calendar-day subtraction, exception handling and original candidate matching.

- `trial_monthly_history` now supplies **all retained event history before November1**, not October only. This updates national and GC historical event charts from one source. Never add its historical rows to old rows; replace by event/month key after validation.
- `ytd_trial_destinations` now supplies **January1–October31**, retaining club-level candidate matches for GC ID classification. Do not read its total as October-only. Validate October by `conversion_month = 2026-10-01`.
- `trial_conversion_timing`, `trial_conversion_timing_exceptions`, `trial_conversion_source_exceptions`, `cumulative_trial_destination_associations`, `trial_conversion_reconciliation` retain query27 methodology and full pre-November cumulative population.
- `trial_cohorts` supplies source creation months before November1 with conversion outcomes observed through execution; the old diagnostic timing fields remain distinct from the cumulative five-group chart.
- `current_trial_pools` is a current-state snapshot of association237 Active/Inactive golfers, with Active precedence; no October-only creation restriction.

Every section has a manifest. Preserve raw `row_data` definitions as well as extracted/source/timezone columns. Timing source rows and deduplicated golfer/signup-day matching events have different counting units; preserve the explicit bridge. Original October references are creation12,665/signup5,076, single-candidate GC4,199, unmatched206/multiple22; explain live rerun differences, never force totals.

## Page-by-page readiness

| Section | Export / processing | Coverage limits |
|---|---|---|
| Home summary | Reuse validated membership/acquisition/score/product aggregates from01–08 | Each tile must show the source window actually available |
| Membership current totals/composition, associations/clubs, NH, linked Index/age, Membership Explorer | 01; approved GC-ID and RAD lookups | Current snapshot only; exact Index uses valid unique golfers; preserve unknowns/plus arithmetic |
| Acquisition history and GC/new-to-GHIN comparisons | 02 plus01 detail | Creation Date versus GC membership-join date stay distinct; preserve 2020 adjustments and GC prelaunch-zero rules |
| Membership trend/billing, retention, recovery | Existing certified history; GC09 and GC historical archive only within GC-approved definitions | No confirmed national historical events/snapshots query; today's status is not historical status |
| Scores totals/associations/posting mix | 03 | Current primary association attribution; unresolved/test buckets reconcile |
| Score demographic history | 04 plus preserved pre2025 history | Current age/gender/affiliation, not historical demographics |
| Score Explorer | 05 joined to01 | Split trial/nontrial, retain unmatched actual bands, don't assume missing match means zero |
| Trials | 06 | All/GC split, source-row/event units, observed outcomes and candidate attribution retained |
| Enhanced GPS | 07 | Activity rows are not proven paid renewals; tenure isn't verified continuous enrollment; explicit status labels aren't actual auto-renew enrollment |
| Challenges | 08 | GHIN verified-AGA filter and explicit test IDs129/933 stay as established; GC importer has its own nondeleted/test-association rules. Current counters cannot reconstruct historical snapshots. GC now uses participations, so unique-golfer discovery no longer blocks its refresh |
| GHIN App usage | No confirmed reporting-DB analytics source | Existing GA4 property190687937; users/sessions/impressions require verified analytics lineage. Do not replace them with membership totals |
| GC web/paid-media/affiliate/marketing sections | No confirmed source in this package | Database schema/source discovery needed if these are in requested scope; preserve dates rather than invent data or default to old portal exports |

**The package refreshes confirmed operational sections; it cannot truthfully certify every website section as fresh without the outstanding analytics/history sources.** DBeaver access does not prove those sources are replicated. No speculative table names are included.

## What already exists, and what the importer must do

Known reusable GC deliveries, subject to each consumer's own validation:

- GC09 November2 snapshot: 827,529 membership rows, archived in GC `data/raw/2026-11/gc_current_snapshot_2026-11-02.csv.csv`;83 capture timestamps. It has neither national coverage nor national acquisition/federation/age fields.
- Extended Trials query26/27 files: cumulative query26 raw conversion count200,667 and validated October counts. Use the actual GC validation record for query27's import state; group06 contains additional national sections absent from those files.
- Challenge November2 counters: GC local995 eligible challenges/50,449 participations/17,885 ranked/155,365scores. National scope differs; use08 or the original counter file plus name/course lookup and recompute national exclusions. No new unique total needed.
- RAD map is shared ID-based September source; preserve user name overrides Illinois State→Central and New Mexico→West, without changing CDGA/Sun Country or inventing IDs.

Before installation:

1. Archive/checksum raw files and SQL versions; record dates/connection/row counts; preserve manifest JSON. No identifiers in Git or public HTML.
2. National membership streaming validation via adapted `scripts/audit_membership_refresh.py`; block duplicate/missing membership IDs, quantify missing joins/unresolved scope. Adapt dated paths and use disk-backed staging for ~4GB input.
3. Adapt `build_membership_refresh.py` / `finish_membership_refresh.py`, `build_refresh_acquisition.py`, `install_membership_refresh.py`, exact Index/intersection builders and installers. Their old Oct13 constants are not today's reporting bounds.
4. Run adapted `import_acquisition_history.py` **after** membership install, preserving `acquisition_adjustments.json`, annual override and historical GC segmentation definitions. Use both detail and aggregates for reconciliation, not doubled totals.
5. Adapt score total/method/history importers to03/04 and new completed months; preserve older history and compare overlap drift. Adapt `build_score_explorer.py` to05 split populations plus new01, not the old Oct13 match file.
6. Unpack06–08 with `scripts/unpack_dashboard_bundles.py`; it recognizes all Trials section names, but retain raw manifests explicitly. Adapt product builders (`build_ghin_live.py`, `build_challenges_data.py`) instead of running old filenames/fixed-total assertions unchanged.
7. Validate population/aggregate partitions, cohort conversions, timing+exceptions, raw-to-event bridge, candidate destinations, GPS date/status partitions, challenge unique IDs/test exclusions, scores and Index stats. Existing values are comparison evidence, not forced targets.
8. Run relevant adapted local checks: `check_membership_refresh.cjs`, `check_membership_explorer.cjs`, `check_acquisition_history.cjs`, `check_gc_joiner_chart.cjs`, `check_score_counts.cjs` and affected NH/age/club/geography checks. Check new source labels, dates, filters, empty selections, desktop/mobile and JS errors.
9. Report validated results and unresolved sections, then review locally. Publishing is a separate explicit user action; GC Azure develop deploys live.

**Preparation status:** local structural/source checks only, no new database query executed, no November3 dashboard data installed, no publish. Receiving CSVs begins validation and dated-importer adaptation; the existing scripts are not yet a one-command shared refresh.
