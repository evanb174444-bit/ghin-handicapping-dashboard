# Handicapping and GHIN Dashboard — Real Data Intake

For the next refresh, use the [export process and rulebook](docs/DASHBOARD_EXPORT_RULEBOOK.md) and [eight-query package](sql/dashboard_refresh/README.md).

Start with the [project knowledge base](docs/KNOWLEDGE_BASE.md) for the October 13 definitions, acquisition-query correction, source status, and database handoff. The unfiltered 508,625 result is diagnostic only, not a validated acquisition headline.

## Reporting rules

### Approved membership counting rules

Confirmed by Evan on September 21, 2026. These supersede earlier guidance making unique golfers the main membership number.

- **Total memberships:** all qualifying membership records, including multiple memberships per golfer. Always the big membership number and the basis for Membership Composition chart counts and percentages.
- **Unique golfers:** distinct golfer IDs in the selected population.
- **Multi-membership golfers:** golfers with more than one qualifying membership in that population, counted once each.
- **Additional memberships:** memberships beyond each golfer's first; total memberships minus unique golfers.

Example: one golfer with three qualifying memberships contributes 3 total memberships, 1 unique golfer, 1 multi-membership golfer, and 2 additional memberships.

Apply the selected population filters before calculating all four measures. Recalculate unique golfers and multi-membership measures across the selected records; do not sum these measures across overlapping golfer populations. Validate membership IDs and golfer IDs before calculation so duplicate join rows or missing IDs cannot inflate the results. Current composition work uses Active memberships.

Confirmed by Evan on September 22, 2026: active memberships with **NH (no Handicap Index)** remain included in membership totals and composition denominators. Show them as **No Index** in the Handicap Index breakdown and exclude them from the average Handicap Index. Never convert NH to zero. Missing golfer details or an unavailable index remain Unknown rather than being assumed to mean NH, and do not contribute to the average.

Confirmed by Evan on September 22, 2026: **All Members** includes Regular (source Standard), Junior, and Unclassified memberships. Exclude association-237 trial memberships from this population and report them separately. Exclude the trial membership row, not the golfer's qualifying non-trial memberships. Keep Unclassified visible rather than assigning it to Regular or Junior.

### Approved access-type mapping

Confirmed by Evan on September 22, 2026:

- Public, Semi-Private, Resort, Municipal, and Military roll up to **Public** in the main Access Type tile.
- Private remains **Private** for Type 1 (green-grass) clubs. Type 2 and Type 3 follow the Public rule below; preserve and flag conflicting source categories.
- Preserve the original `club_category` values. Add a separate Public breakdown tile showing Public, Semi-Private, Resort, Municipal, and Military individually, using qualifying membership counts. Its percentages use the Public rollup as the denominator.
- Show **Total Public Memberships** prominently above the breakdown. The generic source Public category must be split by recorded club type: Type 1 → **Public Green Grass Clubs**, Type 2 → Affiliate/WORE, Type 3 → Virtual clubs/eClubs. Authoritative GC matches take precedence. Keep the main Access Type rollup labeled Public. This makes the breakdown labels descriptive without assuming all source-Public records have real estate.
- Add a half-width **Affiliate / WORE by Association** tile alongside the Public breakdown. Use the same mapped Affiliate/WORE pool and membership association ID, rank descending, show membership counts and shares, and respond to All/Regular/Junior. Its rows must sum to the Affiliate/WORE total. Preserve missing IDs as Unknown. Association names require a verified numeric-ID lookup; the existing mock association labels do not establish that lookup.
- Affiliate rolls up to **Public** access. Preserve Affiliate in the Public breakdown tile and retain the recorded Type 1/2/3 for the Club Type tile. Evan clarified that Affiliate category must not override a recorded Type 1 or Type 3.
- WORE is equivalent to Affiliate for access reporting: **Public**. Combine WORE with Affiliate in the Public breakdown tile, while preserving the original `club_category` and recorded club type. This supersedes the earlier Affiliate/WORE → Type 2 override; authoritative GC matches still appear separately as GC Clubs.
- **Type 2** means affiliates and is **Public**; **Type 3** means virtual clubs/eClubs and is **Public**, including when `club_category` is Not Specified. Preserve the original category. For the Public breakdown, classify otherwise unspecified Type 2 memberships as Affiliate and otherwise unspecified Type 3 memberships as Virtual clubs/eClubs.
- **Type 1** means a club with real estate (green grass), which may be Public or Private. Use the known club category to determine access. If its category is Not Specified or missing, show **Unknown — green-grass access not specified**, retaining these memberships in the overall denominator.
- In the September 21 Active Standard export, the 130,819 Not Specified memberships comprise 4,789 Type 2 and 34,128 Type 3 memberships (38,917 classified Public), plus 91,902 Type 1 memberships whose access remains unknown. These are observed counts, not adjustment constants.

### Approved GC club classification

Confirmed by Evan on September 22, 2026:

- Evan's GC dashboard club list is authoritative for GC identification. Match by club ID using that list; do not infer GC membership from club names alone.
- All GC clubs have **Public** access.
- In the Club Type composition tile, authoritative GC matches appear in **GC Clubs** instead of Type 1/2/3. Each membership contributes to exactly one displayed club-type category. GC classification takes precedence over the underlying source club type; retain the source type for traceability.
- The approved access and GC mappings are implemented in the local Membership Composition view. The September 21–22 extracts populate All Members, Regular, and Junior; historical trends remain unavailable.

### Snapshot and activity dates

- Report date: the certified snapshot date shown in the dashboard.
- Snapshot metrics (for example, active golfers and GPS subscribers): use the value **as of the report date**.
- Monthly activity metrics (for example, scores posted, trials, and conversions): use the **last completed month**.
- For an August 1 report, snapshot metrics are as of August 1 and monthly activity is through July 31.
- Historical comparisons must use the same date or completed period in each comparison year.

Place incoming operational extracts in:

`data/raw/<module>/`

The dashboard will never read these files directly.

## Source files needed

### 1. Association master

One row per association.

Required fields:

- association_id
- association_name
- active_flag

### 2. Membership snapshots

One row per snapshot date, association, and member segment.

Membership processing must retain membership and golfer IDs in private source staging and produce `total_memberships`, `unique_golfers`, `multi_membership_golfers`, and `additional_memberships` for each supported selection. Segment-level distinct counts alone cannot establish national unique counts. The legacy golfer fields below do not substitute for the approved membership measures.

Required fields:

- snapshot_date
- association_id
- membership_type
- access_type
- club_type
- gender
- age_band
- handicap_index_band
- active_golfers
- inactive_golfers
- archived_golfers

### 3. Acquisition, retention, and recovery

One row per reporting month, association, and member segment.

Required fields:

- reporting_month
- association_id
- membership_type
- new_golfers
- up_for_renewal
- renewed_on_time
- retained_12_month
- prior_year_active_base
- reactivated_golfers

### 4. Scores

One row per reporting month, association, membership segment, provider, product, and posting type.

Required fields:

- reporting_month
- association_id
- membership_type
- gender
- provider
- product
- posting_type
- scores_posted
- active_hcp_golfers

### 5. GHIN Trials

One row per reporting month and association.

Required fields:

- reporting_month
- association_id
- trials_created
- trial_conversions
- active_trial_golfers
- inactive_trial_golfers
- conversion_timing_bucket

### 6. Enhanced GPS

One row per reporting month and member segment.

Required fields:

- snapshot_date
- reporting_month
- membership_type
- gps_subscribers
- upgrades
- renewals
- eligible_for_renewal
- retained_subscribers
- lapsed_subscribers

### 7. GHIN Challenges

Challenge-level data with association ownership.

Required fields:

- challenge_id
- challenge_name
- association_id
- status
- start_date
- end_date
- golfers
- ranked_golfers
- scores_posted

## Validation gates

Before any source replaces mock data:

1. Association IDs reconcile to the approved association master.
2. Totals reconcile to the source workbook or certified system extract.
3. Segment totals reconcile to the corresponding overall total.
4. Dates follow the snapshot-versus-completed-month rules above.
5. Percentages are recalculated from counts, not imported as independent values.
6. Missing values remain missing; they are never silently converted to zero.
7. Every displayed figure can be traced to a source file, row grain, and calculation.

## Recommended rollout

1. Membership Totals and Summary Active Golfers
2. Membership Composition
3. Acquisition, Retention, and Recovery
4. Scores
5. GHIN Trials and Enhanced GPS
6. GHIN Challenges
7. Associations tables and insights

The first requested source should be the association master plus monthly membership snapshots for 2021–2026.


## Working U.S. scope — September 22, 2026
Membership composition uses membership association_id matched to non-test associations whose parent_federation is United States Golf Association. This provisional federation-based definition includes Golf PR and excludes Guam; it is not a golfer-residence filter. No association status or is_aga filter is added. Missing/blank federation is excluded and counted in the scope audit.

Configuration: config/membership_scope.json. Verified lookup: config/association_scope_lookup.json. Every membership composition total, unique count, chart and average is recomputed after applying scope. Other dashboard sections remain their existing mixed/mock sources and are not validated U.S. actuals.

Worldwide aggregate snapshots are preserved in data/snapshots/worldwide-2026-09-22. To revert, set mode to worldwide, label to Worldwide Associations, and definition accordingly in membership_scope.json; rerun review_membership_exports.py then build_membership_composition.py and render_membership_review.py. Raw exports are unchanged. Future separate SQL exports with the same U.S. filter are in sql/national_membership/us_only.


## Club membership explorer
The full-width Club Membership Breakdown now covers all memberships: the eight disjoint Public subgroups, Private Clubs, and Unknown Access. Groups sort by membership count; shares use Total Memberships. Each group selects its own association breakdown, whose shares use that group’s total. The established access and GC precedence rules are unchanged. All/Regular/Junior selections apply to both sides.


## High-index insight
The Handicap Index key insight is unique-golfer weighted: female golfers with numeric Index >20 (and separately >30) divided by all golfers above the same threshold within the selected membership population. NH and missing golfer details are excluded. Unknown gender stays in the denominator. Membership IDs use the later export on overlap before golfers are deduplicated. The build fails if a qualifying golfer has conflicting gender values. Rebuild with scripts/build_high_index_insight.py after scope/source changes, then scripts/build_membership_composition.py. This differs intentionally from membership-weighted bars.


## Club explorer gender toggle
All/Men/Women filters only the Club Membership Breakdown tile, intersecting the current All/Regular/Junior population. All retains unknown gender; Men uses Male and Women uses Female. Both the club-group shares and association shares recalculate within the selected gender. Membership counts remain membership-weighted. The selected club group persists when gender or member population changes; empty combinations show an empty state.


## Club explorer comparison mode (supersedes separate gender filters)
All/Male-Female is now a display-mode toggle. All is the default and includes unknown gender. Male/Female shows two club-group bars using the total for each gender as denominator, and association columns containing each gender’s count and share within the selected club group. Association rows sort by combined Male+Female membership count in comparison mode. The headline remains Total Memberships, including unknown gender; gender subtotals exclude unknown. Both modes respect All/Regular/Junior populations.


## Linked age and Handicap Index explorer
One full-width tile now links age selection on the left to membership-weighted Handicap Index counts, gender shares and averages on the right. All ages is first/default and includes unknown/invalid ages; Unknown/invalid is also independently selectable. A shared All/Male-Female view defaults to All. Age selection persists across population changes and empty groups render explicitly. NH stays in distributions but is excluded from averages. The existing unique-golfer Handicap Index insights apply to All ages only and are hidden for selected age brackets; the female age insight describes the overall selected member population.


## No Handicap Explorer
NH means trimmed, case-insensitive handicap_index_display = NH; numeric missing/Unknown is not treated as NH. All/Regular/Junior scope applies. Breakdowns cover association, access, mapped club group, recorded club type (GC retained under source Type), gender, age including invalid/missing, and membership type. Every row shows NH membership count, share of all NH memberships, and NH count divided by all memberships in that segment. Selecting a row drills into club counts within that same segment. Unique golfers with at least one NH membership are counted separately, after the same membership-ID overlap resolution and U.S. scope. Only aggregate club names and counts are embedded, never golfer IDs.


## NH intersecting filters
Left overview remains unfiltered by the right-pane selections (but respects the top member population). Clicking rows replaces/adds one filter per dimension on the right. Add/remove/clear controls support intersections across membership type, association, access, group, gender and age. NH rate denominator includes all matching memberships, not just NH. Unique golfers are computed by union of matching anonymous aggregate cell-patterns, never summed across overlapping groups. No GHIN numbers or golfer IDs are embedded. Rebuild scripts/build_nh_intersections.py before build_membership_composition.py after scope/source changes. Validated Junior + NCGA + Female + Affiliate/WORE independently against CSV: 7,853 NH memberships, 7,730 unique golfers, 8,728 total matching memberships.


## Unified NH Explorer
The single full-width explorer supersedes the left-overview/right-filter layout. Filters remain cumulative; results can be grouped by Membership Type (default), Association, Public/Private, Club Group, Gender, Age, or Club. Rows show matching NH counts, share of matching NH, within-row NH rate, and all matching memberships. Zero-NH rows are omitted. Unique golfers remain an intersection-wide metric, not a sum across groups.


### Membership Explorer preview — September 23, 2026
Added a separate full-width Membership Explorer below the existing explorers. Combined filters and result groupings include membership type, association, access, club group, recorded club type, gender, age, Handicap Index band, and club. It follows the current U.S. scope and population selection. Total membership counts use deduplicated membership IDs; anonymized golfer cell patterns calculate unique golfers across each filter intersection. No golfer IDs are embedded.

Rebuild intersection data with `python3 scripts/build_membership_intersections.py`, then rebuild the local HTML with `python3 scripts/build_membership_composition.py`. Verify with `scripts/check_membership_explorer.cjs`. Checked baseline 3,840,678 memberships / 3,544,477 unique golfers, all nine grouping sums, NH reconciliation (438,165 / 433,444 unique), stacked filters, population switching, empty selections, removal/reset and mobile overflow.


## November 13, 2026 — GHIN Trials refreshed locally

Source: data/raw/ghin/2026-11-13/trials_full_refresh_2026-11-13.csv, SHA-256 65dcee30feb6f3ce7902b79f15bef05d897a97bc3e4d23fce2cc5de7afb71917. 10,744 CSV rows: nine manifests and 10,735 aggregate data rows. Original CSV and SQL retained unmodified. Separate export reads at 15:15:45 and 15:30:57 America/New_York are preserved; not a frozen snapshot. Database label ghin2020pilot retained, without independently certifying the server mapping.

Completed monthly history spans June 2024–October 2026 (29 months, 87 event rows). October: 12,662 trials created / 5,076 signups / 14,246 trial starts. Jan–Oct 2026: 158,474 created / 81,338 recorded signups. Same-day candidate destinations reconcile month by month: GC 65,530; non-GC AGA 12,297; non-AGA 510; unresolved 3,001. Attribution rules unchanged; candidates are not certified paid destinations.

All-time source timing uses the dedicated five-group dataset and totals 200,667 conversions before November1. Cohorts created before November have 201,666 observed conversions as of November13; that includes later outcomes and must not be substituted for completed-month conversions. The top cohort summary retains its observed-outcome methodology and now labels that distinction explicitly. Current trial pools: 160,517 active / 103,991 inactive, Active precedence; two overlapping-status golfers reported separately by source.

Updated the local Trials page, October selector, monthly/YTD/annual chart labels and source notes, destination chart, timing groups, and linked home trial summaries. GPS and Challenges data unchanged. Saved source: scripts/import_trials_refresh_2026_11_13.py. Validation: reports/trials_refresh_2026-11-13.json and scripts/check_trials_refresh_2026_11_13.cjs. Source partitions, unique aggregate keys, month coverage, cohort partitions and raw-to-event bridges verified; nine chart-mode checks and local browser controls passed. No publication. Old build_ghin_live.py still targets October2 inputs; do not run it to install this delivery.

November 13, 2026: Evan explicitly directed cutting headline Trials Converted and Conversion Rate off at October31. Headline values now use completed monthly event history: 462,033 created, 200,667 signups, 43.4%. Both totals use the same cutoff. Post-cutoff observed cohort outcomes remain archived but are not used in these headlines; current trial-pool snapshots retain their truthful November13 date. Local only.


## November 13, 2026 — Advanced GPS refreshed locally

Source: data/raw/ghin/2026-11-13/gps_2026-11-13.csv, SHA-256 30269dd71186263d74b6b2d48a7dd7a218903452c38be005eb33c0287f71d42f. 512 CSV rows: four manifests / 508 aggregate rows (30 active reconciliation groups, 474 activity groups, three tenure cohorts, one explicit renewal-status aggregate). Envelope extraction time 2026-11-13 16:06:40.996 -0500, America/New_York; original source, query and manifest definitions retained. Database label is ghin2020pilot; server mapping not independently established.

November13 snapshot: 102,484 active-flagged unique golfers = 102,118 current-date coverage +158 outside dates +208 missing dates without a current range. Reconciliation, active tenure population and explicit renewal-status active totals agree. Active subscription rows102,502; golfers with multiple active rows15. Date-quality partitions and tenure bands reconcile for all three overlapping cohorts; on/off/unknown statuses reconcile to active golfers.

Completed monthly charts end October31,2026. Jan–Oct2026 new28,763 /renewed64,910. October new1,915 /renewed4,294 /canceled179 /expired178. Partial November retained only in the raw/full-history and established lifetime totals, labeled as throughNovember13. Current subscriber/tenure state is November13, not an October31 snapshot. All existing counting methods retained: activity statuses are record counts grouped by creation month, not verified payments or certified historical active subscribers. Tenure is time since retained initial date, not verified continuous enrollment.

Updated Advanced GPS cards, October highlights, Monthly/YTD/Annual controls and dates, tenure figures/notes, and home GPS cards. Trials data and October31 headline cutoff are unchanged; Challenges unchanged. Source importer scripts/import_gps_refresh_2026_11_13.py; validation reports/gps_refresh_2026-11-13.json and scripts/check_gps_refresh_2026_11_13.cjs. Twelve chart-mode checks and local browser review passed. No publication. Old build_ghin_live.py still targets the old inputs and must not be run to reinstall this refresh.


## November 13, 2026 — GHIN Challenges refreshed locally

Source: data/raw/ghin/2026-11-13/challenges_2026-11-13.csv, SHA-256 96b6aa00f9fc84cb822da75f557bc4676ecd90aa0d15cb05e57d151f5db7672f. 2,231 CSV rows: two manifests /1,159 challenge rows /1,070 name-lookup rows. Extraction2026-11-13 16:36:20.879 -0500, America/New_York. Original CSV, SQL and manifests retained. Database labelghin2020pilot does not independently certify the server mapping.

Preserved national scope: active non-test verified AGAs from association_scope_lookup; deleted challenges and explicit test IDs129/933 excluded. Partition:994 eligible,145 deleted,19 outside verified AGA scope,1 explicit test. This differs intentionally from the GC consumer's scope. 56 duplicate diagnostic course_num-join lookup rows were collapsed only after confirming identical primary course identity/name. All994 eligible names/course names resolve; actual join remains crs_courses.id.

November13 snapshot:994 challenges /50,648 participations /18,016 ranked participations /156,531 scores /36 participating AGAs /780 distinct courses. Statuses:920 completed /71 active /3 upcoming. January–October2026 starts789; October32. Current counters and detail tables include all eligible records, including future scheduled starts. Completed-month charts stop October31. Participations/scores grouped by challenge start month are current challenge counters, not monthly golfer or score-posting activity. Historical2025 coverage remains partial from March14; available-total changes remain marked as non-comparable full periods.

Duration analysis recomputed from721 completed2026 challenges, with all in exactly one day-range band. Highest average participation remains10–12weeks (159.7); highest ranked rate8–10weeks (48.2%,138 challenges). Winners are now calculated dynamically rather than fixed editorial labels. Date labels, charts, counters, AGA/site tables and source notes refreshed; Trials and GPS payloads unchanged. Validation: reports/challenges_refresh_2026-11-13.json and scripts/check_challenges_refresh_2026_11_13.cjs;80 monthly values,12 chart modes, aggregate partitions, regional filtering and local browser review passed. Importer: scripts/import_challenges_refresh_2026_11_13.py. Old build_challenges_data.py still targetsOctober3; do not rerun it for this delivery. Local only; no publication.


## November 13, 2026 — current GC data port to national GHIN dashboard

Local only. The GC Membership Totals layout is retained and now reads the owning GC project’s November 2 snapshot / completed October activity. Active memberships 550,660; October new memberships 8,332; YTD new memberships 169,888. Copied membership, segmentation, retention and recovery JSON unchanged, with source hashes in `reports/gc-port-2026-11-13.json`. Imported current association adapters and their reconciliation controls. Original monthly headline totals and observed association counts remain distinct; November 2025 reconstructed association base is 436,675 versus original historical headline 438,198. Estimates, unclassified recovery records and authorized June expiration substitution remain identified in notes.

Native GC Acquisition retains its distinct-golfer method and chart format. January–October 2026 rebuilt from existing verified November 3 national membership detail (10,279,905 scanned rows), not substituted with GC monthly membership counts. 170,410 distinct 2026 joiners (137,926 same-day new GHIN; 32,483 existing GHIN; one unknown); October 8,329. Pre-2026 history unchanged. Analytics/funnel sources retain their own source dates.

The 8766 local preview previously allowed only its top-level review files, causing embedded GC pages to return 404. `scripts/serve_local_review.py` now safely serves public GC summary HTML/JSON assets, rejects traversal/raw/private routes, and externalizes identical inline dashboard code for browser tooling. Start with Python; review at http://127.0.0.1:8766/review.html. Backups: `backups/gc-before-port-2026-11-13/`. Local browser review and syntax/aggregation checks passed. No push or deployment.

GC embedded pages now size to their content with ResizeObserver, including after data renders, so narrow screens do not clip the lower charts or notes.


## November 16 — Get a Handicap funnel through October

Funnel-only refresh at Evan’s clarified scope. Existing GA4 property331309674 / Get a Handicap - Overview_Eb / Get a Handicap segment / seven-step closed funnel retained. Original CSV exports archived under data/raw/ga4/2026-11-16 with source hashes in reports/getahandicap_funnel_refresh_2026-11-16.json. September completed-registration users7,007; October5,273. Jan–Oct cumulative108,943; Nov2025–Oct2026 cumulative116,536. Cumulative values are separate GA4 runs, never sums of monthly uniques. Q3 cumulative:103,247 completed /117,388 Payment /1,045,984 Landing. Monthly reports show100% available data; GA4 reports7.1% sampling for Jan–Oct and6.6% for Nov2025–Oct2026; Q3 also flagged sampled. Source consent-only exploration notice retained in Data notes. Earlier funnel history unchanged.

Updated funnel, health, transition trends, month selectors, headline funnel KPIs and cumulative quarter/year charts. Sessions/bounce data stay through August and were not imported or changed. September/October traffic KPIs show N/A instead of zero. Separate coverage labels remain truthful. Node validation and local browser review passed. No push/publication.
