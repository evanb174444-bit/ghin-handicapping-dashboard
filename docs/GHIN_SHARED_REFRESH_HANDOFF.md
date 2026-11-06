# GHIN-side handoff for one GHIN + GC refresh process

> **November3 full-refresh package now prepared:** [dated instructions and nine-group index](../sql/refresh_2026-11-03/README.md). Group06 SQL now includes full historical event months before November1, Jan–Oct club-level candidate destinations, five legacy timing buckets, cumulative association/exception/reconciliation sections, creation cohorts and current pools. This closes SQL preparation only, not execution/importer validation. Prior statements that06 still needs assembly describe the older package. Current snapshots use actual extraction time; completed activity ends October31.

> Canonical shared operating contract: [SHARED_DASHBOARD_REFRESH.md](/Users/EvanBelfi/Documents/Projects/USGA-GC-Dashboard/SHARED_DASHBOARD_REFRESH.md). Shared status ledger: [SHARED_EXPORT_LEDGER.csv](/Users/EvanBelfi/Documents/Projects/USGA-GC-Dashboard/SHARED_EXPORT_LEDGER.csv). This document supplies the detailed GHIN-side evidence.

Prepared November 2, 2026. Evidence-backed inventory for reconciliation with “Update GC dashboard,” not a new deployed pipeline or a change to metric definitions. Evan authorized direct coordination between the two chats, one common query/export grouping, and DBeaver-based sourcing. Do not edit either site's presentation or publish during this reconciliation.

## Ownership and paths

GHIN workspace: `/Users/EvanBelfi/Documents/GHIN Handicapping Dashboard`.
Main GHIN artifact: `Handicapping and GHIN Dashboard.html` (large standalone HTML with embedded aggregate payloads).
`gc-dashboard-summary/` in this workspace is an older copy; **it is not the current GC website source**. Its `ghin_trials.json` still contains older draft totals. Do not update it as a proxy for the GC site shown in Evan's screenshot.
Current GC workspace: `/Users/EvanBelfi/Documents/Projects/USGA-GC-Dashboard`; GC chat owns that workspace during reconciliation.

Core GHIN references: `docs/KNOWLEDGE_BASE.md`, `REAL_DATA_INTAKE.md`, `docs/SCORE_POSTING_NOTES.md`, `docs/DASHBOARD_EXPORT_RULEBOOK.md`. `config/data_sources.json` is partly stale (e.g., awaiting-source modules already have operational extracts); do not treat that registry as a reliable completeness inventory.

## Existing SQL inventory

All paths below are relative to the GHIN workspace. The eight-file package is prepared, but the complete package has not been database-executed or integrated. Successful older exports establish many source contracts; preparation of a new SQL file does not certify its runtime or resulting data.

| Query | Purpose / key source | Window and grain |
|---|---|---|
| `sql/dashboard_refresh/01_memberships.sql` | All qualifying membership detail; `v_golfer_clubs`, `v_clubs`, `v_golfers`, `v_associations` | All creation dates/statuses, one membership ID per row; as extracted |
| `02_acquisition_history.sql` | Scoped historical new-to-GHIN aggregates from membership `golfer_creation_date` | Jan 2020–Oct 2026, month/scope/population distinct golfers |
| `03_scores_posting_mix.sql` | `scores` plus deduplicated `t_extract_current_year_scores` / `t_extract_previous_year_scores` labels; current primary-club attribution | Jan 2025–Oct 2026, aggregate dimensions |
| `04_scores_demographics.sql` | Separate score aggregation with current golfer age/gender and primary-club fields | Jan 2025–Oct 2026, aggregate dimensions |
| `05_score_participation.sql` | `golfer_clubs`, `clubs`, `golf_associations`, and YTD `scores` | Current Active non-trial/trial pools; Jan 1 through execution, one population/golfer |
| `06_trials.sql` | Four-section legacy Trials bundle | Full retained events/cohorts, current pools, Jan–Oct candidate destinations |
| `07_gps.sql` | `gps_subscriptions`, `gps_activities` | Full activity/current subscriber/tenure/explicit-status sections |
| `08_challenges.sql` | `challenges`, `crs_courses` | Full retained current counters and separate course-name matches |

**Keep score mix and demographics separate. Evan explicitly rejected the huge combined monthly score query.** Run heavy exports sequentially. Month/year subdivision is a fallback, with documented disjoint bounds and unchanged filters. Last national membership export was 10,251,896 rows / 4,172,285,048 bytes (about 3.9 GiB); posting mix 70 MiB, 2026 demographics 205 MiB, prior non-trial participation 42 MiB. Smaller output does not imply a cheap source query.

## Latest shared Trials SQL — supersedes partial trial handoffs

Use `sql/ghin/27_extended_trials_legacy_timing_october_2026.sql`.
Export filename: `trials_extended_legacy_timing_october_2026.csv`.
The prior `26_extended_trials_through_october_2026.sql` was successfully executed per GC chat's validation: cumulative raw conversions 200,667; October created 12,665; October signup 5,076; unique same-day GC matches 4,199. Query 27 changes only timing bucket definitions plus descriptive/export comments; it has not yet been executed. The original October CTEs remain unchanged in both.

Five timing buckets: First day 0 / Next day 1 / First week 2–7 / First month 8–30 / Beyond 1 month 31+ calendar days. Arithmetic is `sign_up_date::date - trial_start_date::date`, not record creation. Missing/negative/nonfinite exceptions and valid-timing share denominator remain.

Envelope: `dataset, record_type, extracted_at, source_database, reporting_timezone, row_data`. Seven datasets, each with a manifest:

- `trial_monthly_history`: October 1–31 creation/start/signup event rows.
- `ytd_trial_destinations`: legacy name, **October only**; same-day matching unchanged.
- `trial_conversion_timing`: all retained pre-November recorded conversion rows, five legacy buckets.
- `trial_conversion_timing_exceptions`: exclusive timing exceptions among those conversion rows.
- `trial_conversion_source_exceptions`: missing-signup and post-cutoff source rows outside conversion population.
- `cumulative_trial_destination_associations`: all retained pre-November distinct golfer/signup-day candidate events, grouped by destination club's **current** association.
- `trial_conversion_reconciliation`: raw/event-grain bridge and controls.

Timing counts source rows; destinations deduplicate golfer/date and exclude missing golfer IDs. Raw rows = missing-ID rows + collapsed duplicate golfer/day rows + destination events. Destination events = single + unmatched + multiple. Timing buckets + timing exceptions = raw rows. “All” is not GC-only. GC is an approved club-ID classification of uniquely matched candidates, not proof of destination or payment. Original October uses membership association ID; cumulative association display resolves current club association after matching and reports differences. Neither proves historical affiliation at conversion.

This extended file **does not supply all legacy 06 sections**: current trial pools and creation-cohort outcomes are absent, and event monthly history outside October is absent. For a truly unified Trials export, include those needed legacy sections in the new bundle under their existing contracts, without rerunning duplicate destination/timing logic or mislabeling October-only as YTD. GC must confirm which sections it displays.

## Confirmed schema/joins and conflicts to resolve

GHIN view memberships: `m.golfer_club_id` ID; `m.golfer_id`, `club_id`, **membership** `association_id`; dates `membership_creation_date`, `golfer_creation_date`, `association_membership_creation_date`, `status_date`, `inactive_date`, `updated_at`; `status`, `usga_membership_type`. Joins: club_id→`v_clubs.club_id`, golfer_id→`v_golfers.golfer_id`, membership association_id→`v_associations.association_id`. Preserve club association_id separately. Validate membership-ID uniqueness; do not assume views are unique.

View golfer fields: `created_at` (different from agreed acquisition Creation Date), status, gender, age, numeric/display Index, primary_club_id. Club fields: category/type/provider/status/is_test. Association fields: name, parent_federation, is_test. View test flags are strings No/Yes. Base-table test flags are booleans.

Scores: `scores.id`, golfer_id, created_at, deleted, penalty, status, is_trial, number_of_holes/number_of_played_holes. Extracts contain repeated membership rows; labels must be deduplicated by score_id before joining. One current-primary association mapping per golfer prevents score multiplication; preserve ambiguous/unknown buckets.

Trials: `trial_golfers.created_at`, `trial_start_date`, `sign_up_date`, golfer_id; signup event is not an invented paid-conversion flag. Candidate membership creation lies within the signup calendar date; nontrial membership association and explicitly non-test club required.

GC snapshot available in GHIN workspace: `sql/gc_snapshot/gc_current_snapshot.sql`, backed by supplied schema files in that directory. Its confirmed base-table joins use membership `club_rate_id`→`club_rates.id`→`golf_association_rates.id`, whose `rate_type` reproduces membership-type lineage. Club association is `clubs.golf_association_id`. Membership creation reproduces view `COALESCE(m.create_db2_ts,m.created_at)::date`. GC-specific snapshot excludes Archived memberships AND Archived golfer profiles, selects 57 listed club IDs, includes names/full DOB/local numbers/auto-renew fields/membership_versions, and preserves source timestamps as timezone-unconfirmed. It does **not** include all GHIN required fields (e.g., verified golfer_creation_date, all-club metadata, federation, age, primary club) or the national population.

Therefore the GC snapshot cannot simply replace national query 01, and query 01 cannot replace all GC-specific inputs. A future common detail extract should preserve a broad superset, with per-dashboard predicates after staging; base-field equivalence for view `golfer_creation_date`, gender, age and federation must be verified before using it. Do not apply GC archived exclusions nationally without reconciling acquisition history. Avoid adding names/DOB nationally just to achieve fewer exports; prefer necessary raw fields/GC-only detail separation.

## Approved GHIN definitions

- Main membership headline counts membership records; Active golfers counts distinct golfer IDs with qualifying Active memberships. Recompute uniqueness after selected filters; do not sum overlapping association/population distinct counts.
- All Members = nontrial Regular (Standard), Junior, Unclassified. Association 237 trial ROWS are separate; keep valid nontrial memberships of those same people.
- Clubs explicitly non-test; known test associations excluded; unresolved association eligibility separately audited. AGA = non-test membership association parent federation United States Golf Association (includes Golf PR, excludes Guam). International = known nonblank other federation. No is_aga/status/residence filters.
- Exact Index stats use unique golfers with valid numeric Index. NH remains in total counts but not mean/median; unknown is not NH or zero. Plus values have negative arithmetic; >54 excluded from valid stats, conflicts investigated. GC WD handling has additional fields unavailable in national view extract: reconcile explicitly, do not silently substitute.
- Approved GC ID list is authoritative. Public/access/Type 1/2/3/Affiliate-WORE precedence remains in intake and `review_membership_exports.classify`.
- New-to-GHIN acquisition uses **membership view golfer_creation_date**, not golfer created_at or membership creation. Include all membership statuses. GC joiners use membership_creation_date and are a distinct metric.
- 2020 approved acquisition correction is preserved separately; subgroup 2020 is omitted where unallocatable; GC acquisition is zero in 2020/2021. Never erase those corrections by rebuilding.
- Scores exclude deleted/penalty, include trial/Temporary/UnderReview/competition/unknown statuses. Posting date is created_at under existing provisional definition. Score All Associations excludes test but includes trial/unresolved; this differs from membership All Associations.
- Participation base-table association is via club; membership Explorer scopes via membership association. Their populations need reconciliation, not assumed equivalence. Zero scores included; trial pool counts all qualifying scores, not trial-flagged-only scores. Trial/nontrial pools may overlap.

## Periods, source status, and historical limits

Session timezone on returned trial CSV: America/New_York. Most view exports preserve database session timezone; GC base snapshot records UTC captured_at but explicitly labels source timestamp timezone unconfirmed. Do not infer UTC or harmonize timezone without a verified source timestamp rule. Current counts are as extracted; monthly activity through Oct 31 uses exclusive `< 2026-11-01`. Participation remains Jan 1 through execution. Cohort outcomes are observed through execution, not reconstructed as of cutoff.

National current membership/composition/Explorer data remains October 13 until refreshed. Scores totals/mix history commonly ends August; 2022–2026 demographic source files are under `data/raw/scores`. Historical national acquisition source is `data/raw/acquisition_history_2026-10-13/new_golfers_historical_2026-10-13.csv.csv` (Jan 2020–Sep 2026). GC joiners are reconstructed from the Oct 13 all-status membership detail and are not certified monthly snapshots. Preserve existing billing and GC month-end series. Current status/latest status date alone cannot recover historical active status, retention or reactivation events. membership_versions is raw potential evidence, not established complete event history.

GHIN App file `data/processed/ghin_app.json`: GA4 property 190687937, GHIN Mobile App, quarterly comparison Q2 2026/Q2 2025 plus other existing series. Membership rows are not analytics active users/sessions/impressions. Evan wants database-driven refresh; determine whether confirmed analytics/session/event tables exist before promising DBeaver replaces GA4. No such table is confirmed in current GHIN query suite. Similar discovery is needed for marketing/influencer/affiliate/getahandicap web metrics; no schema invention or forced proxy metrics.

## Import/build contract and QA

Most existing scripts are **hard-coded to prior dates and sources**. They are not an unattended eight-file refresh orchestrator.

- Membership: `audit_membership_refresh.py` (stream into SQLite, ID/scope checks), `build_membership_refresh.py` / `finish_membership_refresh.py`, `build_refresh_acquisition.py`, `install_membership_refresh.py` (dated Oct13 paths). Refresh Index stats through `build_membership_index_stats.py` and installer. Membership/association/club/intersection/Index outputs in `data/processed`; source identifiers stay private.
- Historical acquisition: `import_acquisition_history.py` runs after membership installation (which otherwise installs 2026-only view); update old bounds/month counts/paths. Detailed GC/new-GHIN comparison: `build_acquisition_gc.py`, `build_gc_joiner_history.py`, `install_gc_joiner_chart.py`.
- Scores: `build_score_counts.py`, `import_score_methods.py`, `import_score_history.py`; adapters still expect older files/months. `build_score_explorer.py` (--trial for trial), `install_score_explorer.py`; currently joins Oct21 scores to Oct13 membership, preserving unmatched counts. Adapt dates and split unified participation population explicitly. Do not let mismatched extracts silently produce zeros.
- Products: `build_ghin_live.py`, `build_challenges_data.py` embed old filenames/dates/asserted totals. Update these before using new sources. `unpack_dashboard_bundles.py` recognizes current extended Trials datasets but only splits structure, not certifying metrics.
- Tests: `check_membership_refresh.cjs`, `check_membership_explorer.cjs`, `check_acquisition_history.cjs`, `check_gc_joiner_chart.cjs`, `check_score_counts.cjs`, and dedicated NH/age/club/geography checks. Existing checks often assert dated totals/date strings: update certified expected inputs, not to hide differences. Browser scripts use local file URLs, Playwright from `/Users/EvanBelfi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright`, Chrome executable. Existing reports under `reports/` and `data/validation/` provide baselines. New combined query runtime and new-date outputs are not yet validated.
- Check raw IDs/keys, joins, known categories, scope partitions, distinct counts, breakdown reconciliation, source windows, matching/timing controls, unmatched preservation, old/new drift, current/prior aligned windows, and local desktop/mobile/filter functionality. Preserve raw checksums/timestamps. Current work has not rebuilt the national dashboard.

## Recommended single numbered export plan — pending GC reconciliation

Retain the eight functional GHIN groups, upgrade group 06 to one shared complete Trials bundle (query27 five buckets + needed cohort/current-pool/history sections). Prefer reuse of national membership extract for overlapping GC totals/composition/acquisition once population and field equivalence is demonstrated. Until then include the existing GC-rich snapshot as an explicit supplementary group 09, not a disguised replacement. It supplies genuinely additional fields and statuses; its output stays private. A tested expanded national superset could later remove 09, but no such query exists yet.

Keep acquisition group 02 while historical acquisition importer requires it. It could later be derived locally from the full national detail; implementation and reconciliation must precede removal. Keep score groups 03/04 separate by Evan's decision. Do not claim eight exports refresh analytics/marketing/history for which no database source has been confirmed. Additional schema-discovery SELECTs are a separate diagnostic phase, not a recurring required export or fake zero metric.

Use one shared status ledger with rows: dataset, SQL path/version, predicates, window/timezone, file/checksum, execution/validation state, GHIN consumer, GC consumer, remaining gap. Both chats should read the same operational contract; designate one human-facing coordinator after inventories agree. A new chat/site migration is unnecessary for this documentation phase.

## Publication and privacy

No raw names, IDs, birthdates, member detail or membership_versions in published assets/Git. Member-level staging stays local. This reconciliation does not authorize altering either site's methods, pushing GitHub or publishing. GC chat confirms Azure develop deploys live; main unchanged is no safety gate. Current live GC commit 8dda899 remains; do not roll back. Local or user-selected GitHub review precedes an explicitly authorized USGA push. GHIN publishing route is not established here; do not assume GC host deployment also publishes GHIN.

## November 2 GC Challenges reconciliation follow-up

GC owning chat reports its new local importer `scripts/import_challenges_snapshot.py` excludes deleted challenges and test associations 98/231 identified by the verified September22 association lookup. Returned-file processing yielded 995 eligible challenges (72 active, 917 completed, 6 upcoming), 36 associations, 50,449 summed participations, 17,885 ranked participations and 155,365 score-counter records. These are GC-local importer results reported by that chat, not a newly executed national rebuild. The prior 1,014 nondeleted headline included 19 test-association challenges. Keep test exclusions and deleted exclusions explicit in shared intake; do not change national federation/AGA eligibility implicitly.

Unique golfers remains 37,777 dated August25; no November unique trend point or current scores-per-unique figure is supported. Both saved 109-column/6-table challenge schema discoveries expose counters and rejected-challenge relationships, with no confirmed accepted roster. Rejected golfers cannot establish participation. Metadata-only discovery SQL is `sql/ghin/28_challenge_participant_schema_discovery.sql`, copied identically by the GC chat into its `scripts/sql/challenge_participant_schema_discovery.sql`; execution/export remains pending. No live publication was performed for this reconciliation.

## November 3 challenge participant discovery result

Query28 has now executed. Reviewed GC `reports/2026-11/challenges/participant-schema-review.json`: 126 metadata rows (109 columns, 3 foreign keys, 14 indexes), extracted November3 12:51:36.739 -0500 from ghin2020pilot. Raw CSV is GC `data/raw/2026-11/challenges/challenge_participant_schema.csv.csv`, SHA256 `438449eb4858d60037da8b43e150fca7426cf4c906658c5a238d950d5b84c312`.

The same six objects returned; no accepted-participant roster, dependent view or incoming challenge foreign key was identified. This does not rule out external storage or an unexpectedly named/unlinked relation. No additional confirmed backend/API lineage exists in the GHIN inventory. Do not count rejected golfers or infer uniqueness from counters. Do not issue another speculative data query as if a roster were confirmed.

Next precise source-owner question: What source computes the admin unique-golfer header/participant export, which challenge_id/golfer_id keys and accepted/opt-out/deletion rules does it use, and is that source replicated to the reporting database? Existing dated unique total remains dated; no new unique figure or live publication is supported by metadata.

## November 3 GC decision: use participations, drop unique-golfer metric

Evan explicitly authorized the GC chat to replace GC Challenges unique-golfer metrics with participations. GC reports local headline50,449 entries, scores/participation155,365 /50,449 =3.1, and trend comparison August25 confirmed detail42,452 to November2 50,449 (+18.8%). Earlier May/July unique counts are not participation baselines. Historical raw unique records remain private; the displayed stale-unique/pending metric is removed. Participant lineage discovery no longer blocks this GC update. This is a GC metric decision, not authorization to alter GHIN presentation or publish. Current GHIN main view already labels participation counts. No new live publishing authorization was provided.

## November 3 RAD coverage: explicit legacy-name overrides

Evan explicitly assigned two legacy GC master names: **Illinois State Golf Association → Central** and **New Mexico Golf Association → West**. GC records these with user-source provenance in its `data/processed/aga_regions.json`. Preserve these name-level overrides in future shared mapping adapters; no numeric association IDs were confirmed or invented. They do not change **Chicago District Golf Association (106) → Midwest** or **Sun Country Amateur Golf Association (35) → Central** in the ID-based September Regional Affairs map (`config/association_regions.json`). RAD coverage is separate from federation scope and residence. This handoff records the decision; no GHIN dashboard/config mapping or publication was changed.
