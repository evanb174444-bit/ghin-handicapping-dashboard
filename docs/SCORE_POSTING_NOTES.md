# Score posting decisions

## Scope and source

Focus first on monthly score-posting counts. Defer provider and posting-mix breakdowns.
Source: data/raw/scores/score_monthly_totals_2025_2026.csv, exported September 28, 2026 from the existing ghin2020pilot connection. Production environment and geographic coverage remain unverified.

## User decision — September 28, 2026

Include trial golfers’ scores in the headline Scores Posted total.
Add a separate trial-score view or tile later. Show trial score counts and share of posted scores; preserve unknown trial status as a separate category, not as non-trial.

## Current extract and open definitions

Monthly history covers January 2025–August 2026, grouped by created_at month, status, and is_trial. Query retained deleted = false, penalty IS NOT TRUE, score_type IN ('H', 'A', 'T'), and status IN ('Validated', 'UnderReview'). Those eligibility rules and use of created_at as posting date remain provisional. No association scope filter was applied.
Trial inclusion is confirmed. UnderReview inclusion is confirmed by the user. Unknown trial status does not by itself exclude a score from an all-trial-status total.
April 2026 contains 161,591 Validated records with unknown trial status.
No dashboard score charts have been replaced yet.

## Updated counting decisions — September 28, 2026

Include trials, UnderReview, and Temporary records. Temporary inclusion is provisional; its meaning remains unverified. User identifies score type C as competition; do not infer Temporary semantics from that code. Exclude deleted records and penalty entries. Remove the prior H/A/T-only filter so competition records are not omitted. The original monthly export excludes Temporary and C and is therefore superseded for headline totals once the revised extract arrives.
Revised query: sql/scores/01_monthly_counts.sql. Retain status and trial-status groups for audit and the planned trial-score tile.

## Revised export received

Source: data/raw/scores/score_monthly_totals_including_temporary.csv. 137 grouped rows covering all 20 months, January 2025–August 2026. Includes all trial flags and statuses; excludes deleted = true and penalty = true per query. One record has blank status.
January–August 2025: 63,144,687. January–August 2026: 65,023,798 (+2.975881%). August 2026: 10,490,204 versus August 2025: 10,635,535 (-1.366466%).
2026 YTD trial breakdown: non-trial 64,383,146; trial 282,836; unknown 357,816.
Differences from the prior extract are not solely Temporary additions: score-type and status filters were removed, and a few trial counts decreased between runs, consistent with a changing database. Retain both exports. Source environment, geography, and created_at posting-date interpretation remain unverified. No dashboard changes yet.

## Association scope — September 28, 2026

The August 1 scope result confirms both AGA and international golfers, plus Trial Association 237, unmatched records, and a test association. Global association selector requested for Scores (Totals, Posting Mix, Associations), matching Membership: AGA Only, International Only, All Associations.

Selector added in the existing filter pill, disabled until scoped counts arrive. Existing score mockups preserved and explicitly labeled sample data. No scope filtering is claimed for these mockups.

Replacement export: sql/scores/02_monthly_counts_by_association.sql. January 2025–August 2026, same dates and deletion/penalty filters as the latest baseline. Includes trial, UnderReview, Temporary, and unknown status. One mapping per golfer prevents join multiplication; ambiguous current primary mappings retained separately. Retains test, trial_association, unknown, and ambiguous buckets for reconciliation rather than dropping rows. All Associations reporting should exclude test records, retain trials and unresolved non-test buckets, and disclose unresolved attribution. AGA and International filters select their confirmed scope buckets; trial-status flags are independent of association scope. Current primary-club attribution is not historical association-at-posting attribution. Membership-type classification, provider, and posting mix are outside this counts-only export. Existing Regular/Junior score views remain mockups until supported source data is available.

After export: verify every month is present; reconcile the sum of all buckets to the unscoped baseline allowing for documented live-data changes; separately report test exclusions and unresolved counts; enable selector using the reconciled scope aggregates.

Scores selector enabled on user request: all three options selectable across Scores tabs. AGA and International currently show a pending-export state; All Associations retains the explicitly labeled mockup. No fabricated scoped counts.

## Export amended for Regular and Junior selectors

The replacement export now includes independent is_regular and is_junior flags from v_golfer_clubs matched to the CURRENT primary club. No membership Active filter is applied, avoiding removal of historical scores from now-inactive golfers. Each golfer maps to one row before joining scores. Missing/ambiguous primary mappings yield unknown member flags. Unclassified member records are explicitly flagged. If both Regular and Junior are present for the same primary club, scores qualify for both selected views but appear once in All Members; do not add population totals together. These classifications describe current records, not membership type at posting. Historic regular/junior transitions cannot be recovered from this export. Association scope and member-population selectors can combine using these fields. Supersedes the earlier note that member classification was outside this export.

## Live counts loaded — September 28, 2026

Imported 11,248 rows from score_monthly_counts_by_association_2025_2026.csv. Every month's raw total reconciles exactly to the preceding 20-month unscoped export. All reported scopes exclude test records. All Associations retains trial-association and unmatched records; AGA and International use verified scope buckets. The 2026 YTD test exclusion is 2,933 scores, producing an All Associations total of 65,020,865. AGA YTD is 63,278,191; International YTD is 1,417,006; the remaining 325,668 comprise Trial Association (299,324) and unresolved scope (26,344).

Connected all nine scope/member combinations to real monthly counts and current-primary association rankings. Updated homepage Scores Posted chart to real All Associations data, through August only. Added a trial-status tile; provider/product/holes/posted-method visualizations remain unavailable instead of showing mocked scoped values. Replaced unsupported score KPIs with current/prior YTD counts, August count, and Trial Scores using the existing card styling. No new active-golfer or female-share figures inferred.

Files: data/processed/score_counts.json; data/validation/score_counts.validation.json; scripts/build_score_counts.py; scripts/scores_scope_view.js; scripts/scores_counts.css. Browser verification: all nine filter combinations, ranking sums/sorting, trial views, 2026 August endpoints with no future zeros, homepage and unchanged Membership counts; no browser errors. Current-primary attribution limitation is shown visibly on each Scores page.

Trial Golfers population added to all Scores views. It selects is_trial = true independently of current Regular/Junior membership flags. All Members still includes trial and unknown-trial records. Verified all twelve scope/population combinations, including zero international trial postings; mobile controls wrap into two columns. 2026 YTD trial scores: All Associations 282,819; AGA 428; International 0. Remaining trial postings are in Trial Association/unresolved buckets, so these are not inferred to belong to an AGA.

Posting Mix original five-chart design restored on user request. Each restored chart is explicitly labeled sample data and does not claim to reflect association/member filters; simulated member scaling is held at All for previews. The separate Trial Status tile remains live and responds to filters. Next database discovery: sql/scores/03_posting_method_metadata.sql identifies the statistics field's type/category definitions without scanning scores. Provider/account mapping discoveries from August 1 remain applicable, but final chart extracts still require definitions and scoped aggregation.


Posting method discovery: statistics is hstore with calculated values, not a method enum. public.holes contains score_id, raw_score, putts, fairway_hit, gir_flag and accuracy fields. Current/previous-year extract tables contain score_id, s_created_at, date_posted, score_posting_method, posting_application and posting_application_api, along with repeated membership rows. Aug 1, 2026 same-created-day coverage (deleted=false, penalty IS NOT TRUE): Hole-by-Hole 147844; Total Adjusted Score 125487; Total Adjusted Score - Front 9 / Back 9 106347; Hole-by-Hole Stats 28632; Missing from extract 2237; total 410547. Repeated extract rows affect 66424/58647/49902/13584 scores respectively. No nonnull method conflicts appeared in this one-day check. These are not yet test-filtered dashboard counts. Missing-from-same-day-extract does not prove absent across all extract dates. Query 04 deduplicates both extract sources by score ID and labels, retains unknown/conflicting categories, and preserves the existing counts source/eligibility/geography/member mapping. Full export remains pending; the three-way UI method chart will combine the two Total Adjusted Score labels but show unknown separately.

September 29 posting-method import complete: 36,212 grouped rows, 20 months, no duplicate aggregate keys. Archived source data/raw/scores/score_monthly_posting_methods_2025_2026.csv. Four extraction timestamps present: not a single snapshot. Monthly raw totals differ from Sept 28 baseline by -28 through +34 scores; full differences recorded in data/validation/score_methods.validation.json. No claim of exact reconciliation to the older export or proven cause for drift. All Scores totals, associations, trial status and homepage score tile now consistently use rolled-up NEW export; prior raw data preserved. All Associations Jan-Aug2026 excluding tests = 65,020,927 (+62); Total Score 37,237,309, Hole-by-Hole 23,358,747, Hole-by-Hole Stats 4,071,472, Unknown 353,399. Trial total 282,641. Method chart snapshot and 20-month trend are live across all 12 scope/population combinations. Unknown is explicitly included in denominator. Four other original mix charts remain labeled sample. Provider and trial tiles remain equal-width adjacent. Browser checks passed all 12 counts, method category sums and all 80 trend points per selection, zero-count international trials, association sums, sorting, mobile overflow, homepage, membership unchanged, and no runtime errors.


Consolidated export query 05 prepared (not executed). Sample application labels: Mobile App (iOS/Android GHIN), GHIN.com, Admin Portal, Kiosk, API and Migration. API account labels include Golf Genius API, multiple New Start Mobile association accounts, Blue Golf API, Fore Tees Api, Arccos Golf Api, AdminEscape, and personal names with unknown provider ownership. Preserve raw labels; do not infer providers from personal names or invent Other membership. Query 05 adds method, application, API account, source, number_of_holes and number_of_played_holes to the established monthly/scope/member/status counts. Conflicts and missing extract classifications retained; counts always from public.scores. It exports score counts by holes, not a separately established unique round metric. Current/prior extract coverage must be checked when updating reporting years.

September 29 consolidated export imported: 331,839 aggregate rows in data/raw/scores/score_monthly_dashboard_2025_2026.csv. All 20 months present, unique dimensional keys checked; duplicate extract membership rows were already eliminated in SQL. YTD excluding test scope 65,020,934, +7 vs method-only export. All six Posting Mix tiles now use this consolidated source with real-data labels, all 12 selector combinations, and actual 20-month trends. Score Totals, Associations, trial and homepage refreshed from same source. Provider mapping uses only explicit company identifiers in API labels; personal/ambiguous account names are Unknown, not assigned to TheGrint or another vendor without evidence. GHIN comprises Mobile App/GHIN.com/Admin Portal/Kiosk; Migration remains separate unresolved provenance. Other identified providers lists its contents in expandable detail. All2026 provider Unknown 3,374,750 plus Migration 887,326. Product tile renamed Scores Posted by Application to include third-party API and Migration honestly. Holes tile renamed Scores Posted by Holes Played, based on number_of_played_holes, with 9=12,762,157;18=51,752,401;10–17=506,376, not deduplicated rounds. Membership categories are disjoint Regular-only, Junior-only, Both if present, and Unclassified; current primary membership caveat remains. All2026 Regular63,050,616;Junior1,302,859;Unclassified667,459. No individual API account names embedded in the dashboard. Raw source kept for audits.

Provider tile replaced by API account tile on user request. Application API row is plain text again; lightbox code removed. API tile uses raw account labels, top seven plus Other API accounts, with full searchable/sortable account table behind Show data. Snapshot shares and total are API-only (All/All 2026 YTD14,854,958); annual and monthly views also API-only. All 12 scope/population combinations and all three views reconcile to Application API subtotal. Current account names intentionally remain raw, avoiding unverified company attribution. Trial tile stays adjacent. No more derived provider tile in live view.
