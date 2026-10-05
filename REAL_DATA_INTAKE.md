# Handicapping and GHIN Dashboard — Real Data Intake

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
