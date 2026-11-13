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

## Participation tile and query — October 21, 2026

Tom requested counts and percentages of golfers posting 0, 1–7, and 8+ scores, with age/gender exploration. Evan confirmed YTD only. Added sql/scores/13_posting_participation_ytd.sql, returning aggregate golfer counts and score sums by scope, population, gender, age band and posting bucket. Period January–August 2026 matches existing score coverage. Current active non-test memberships define eligibility, with Trial Association excluded. All Members includes unclassified types; Regular/Junior independent, each golfer deduplicated within scope/population. Demographics are current at export. No personal identifiers returned. Query prepared, not executed against the database.

Added Score Posting Participation above annual/YTD charts in Scores > Totals. Existing selected score total is shown as context, explicitly not a golfer count. All three participation counts and percentages remain Pending until the new export arrives. Age/gender controls are disabled in an expandable explorer. Trial selection states the separate cohort requirement. Do not infer these bands from aggregated monthly score totals or use a different membership-snapshot denominator. Saved source and embedded HTML updated together; no data rebuild or publication performed.

## Participation counts imported — October 21, 2026

Imported Downloads/score_posting_counts_2026.csv.csv, archived as data/raw/scores/score_posting_counts_2026.csv. Exactly three buckets: 0 scores879814 (24.05%),1–7 scores682804 (18.66%),8+ scores2095705 (57.29%). Sum3658323 distinct active golfers; percentages independently recalculated and match to two decimals. CSV has no period/scope/extraction metadata; Jan–Aug2026 and current-active non-test all-association eligibility follow the supplied counts-only SQL. No demographic or Regular/Junior breakdowns. Data stored data/processed/score_participation.json, rendered from embedded copy in scores_scope_view.js function liveScoresParticipation. Scope/month/population mismatches explicitly unavailable. Removed pending age/gender controls per user's counts-only direction. Source and standalone HTML updated without rebuilding unrelated data. No git push.

## Corrected current YTD participation — October 21, 2026

Supersedes the August-cutoff participation tile above. User supplied score_posting_counts_2026_current.csv.csv with extraction/score-end timestamp 2026-10-21 17:51:14.105 -0400 and period start2026-01-01. Counts: zero823995 (22.52%),1–7 616875 (16.86%),8+2217477 (60.61%),total3658347. Recomputed percentages match export; rounded percentages sum99.99%. Zero score rate remains22.52% after extending scores through extraction instead of August. Do not attribute the earlier full zero-score count to cutoff mismatch or claim the remaining result independently audited beyond SQL/export checks. Current-active eligibility and score cutoff now use the same statement snapshot per supplied query. Payload and tile refreshed; raw old export preserved. Tile always explicitly shows its fixed Oct21 period, independent of report-month selector for other score totals, and remains unavailable for narrower scope/population selections. No age/gender data. Not pushed.

Participation moved to dedicated Scores > Explorer tab at user request. Removed from Totals; Explorer shows October21 participation subtitle and omits the unrelated August score-total footer. Global scope/population selections still apply with unavailable messaging for unsupported cuts. Import script preserves the separate route. Removed the explanatory report-month line and participation-rate sentence per user request. Not published.

## Regular/Junior participation — October 21, 2026

Imported score_posting_counts_by_type_2026.csv.csv;12 rows, one extraction and period-end timestamp2026-10-21 18:18:26.947 -0400. All3658374: zero823985,1–7 616857,8+2217532. Regular3253608:517035 (15.89%),579291 (17.80%),2157282 (66.30%). Junior395655:304846 (77.05%),36262 (9.17%),54547 (13.79%). Unclassified16712:2912,2315,11485. All group totals and rounded percentages validated. Groups overlap; do not subtract Junior from All to infer Regular. Classification uses m.club_rate_id -> v_club_membership_types.club_membership_type_id plus club_id; view joins club_rates.golf_association_rate_id to golf_association_rates.rate_type. No age-based classification or unverified rate fallback. Unmapped memberships retained in All and unclassified audit group. Existing Regular/Junior toggles now supported in Scores > Explorer for All Associations. AGA/International and Trial remain unavailable. All figures updated from this same export, preserving older sources. Dashboard script, import template and embedded HTML updated; not pushed.

## Scores Explorer ID join — October 21, 2026

Imported private two-column active_golfer_ytd_scores_2026-10-21.csv.csv (42MB). Unique IDs3658438; buckets823946/616792/2217700, total scores76785726. Joined to the validated archived October13 membership CSV, retaining active AGA/International memberships using the established classification helper. Downloads membership CSV had malformed quoting; used the previously validated archive already used for the membership dashboard. Matched3649865 golfers;8573 lacked an October13 active membership match (buckets4360/2447/1766). Unmatched retained in overall counts via explicit unknown cell; never inferred zero scores. Snapshot differences disclosed in tile and expanded definitions. No exact score extraction timestamp in CSV.

Build scripts/build_score_explorer.py creates private SQLite staging under data/raw/score_explorer_2026-10-21 and anonymous cells/patterns in data/processed/score_explorer.json. No golfer IDs in public payload. Grouped pattern counts preserve per-golfer deduplication across memberships for filters and group rows. UI scripts/score_explorer_view.js, installer install_score_explorer.py. Nine dimensions: membership type, association, public/private access, club group/type, gender, age, Handicap Index, club. OR within dimension, AND across dimensions on same membership record. Existing global scopes/populations now use Oct13 matched attributes, not prior Oct21 type aggregate. Trial stays unavailable. Table shows largest100 groups with explicit label; filters still cover all groups. Counts/percentages use unique golfers. Membership source metadata current at Oct13, not score cutoff. Individual IDs stay private. HTML now87.8MB.

Validation: input unique IDs/nonnegative counts; bucket reconciliation including unmatched; browser totals, combined Female+Private+35–44 filter (2264/2218/3389,7871 total), group/scopes/populations/mobile; independent SQLite COUNT(DISTINCT golfer) matches that filter exactly. Reports score_explorer_validation.json and score_explorer_filter_validation.json. No publication.


## October 21: current active trial score participation
Imported active_golfer_ytd_TRIAL_scores_2026-10-21.csv.csv: 156,349 unique IDs, no duplicates or negative counts. YTD bands: 128,662 zero (82.29%), 26,703 with 1–7 (17.08%), 984 with 8+ (0.63%); qualifying scores total 62,450. This is current active Association 237 golfers' YTD posting, not all trials created YTD and not restricted to scores posted during trial dates.
Matched 153,536 golfers to active October 13 Trial memberships; 2,813 unmatched remain in overall totals with actual bands [1629,1082,102]. Public score_trial_explorer.json contains anonymous grouped patterns only. IDs and staging remain under data/raw. Trial selection uses the existing Explorer filters/sorting; switching between trial and member datasets clears filters to prevent label-index mismatch. AGA/International exclude Trial Association 237. Existing non-trial totals unchanged. Local update; not yet published.


## October 23: creation-year filters and grouping
Scores Explorer now includes Golfer Creation Year and Membership Creation Year in both filter and group selectors for non-trial and trial populations. Source fields are golfer_creation_date and membership_creation_date from the October 13 membership export. Years 1900 through the snapshot date are accepted; missing or invalid dates are explicit unknowns. Unmatched memberships remain separately labeled. Creation fields describe source records, not proof of first-ever participation or renewal.
A golfer counts once per selection and once per qualifying group; membership-year rows can overlap. Score bands still cover January 1–October 21, not just time since membership creation. Adding years preserves all prior grouped patterns exactly when the new dimensions are removed, validated against the preceding datasets for both populations. Totals remain 3,658,438 non-trial golfers and 156,349 trial golfers. The enlarged anonymous dataset is gzip-compressed within the standalone page and decoded locally by the browser; private identifiers are not embedded.

## September–October posting mix import — November 6, 2026

Imported `scores_posting_mix_sep_oct_2026.csv.csv` from Downloads. Archived unchanged under `data/raw/scores/2026-11-06/`; SHA-256, four source timestamps (12:14:09.134–12:39:47.629 -0500), row count34,806 and checks are in `reports/scores_incremental_2026-11-06.json`. No single frozen snapshot is claimed. Query source: `sql/scores_refresh_2026-11-06/01_scores_sep_oct_2026.sql`.

No duplicate aggregate keys. Exactly September/October; counts, flags and methods validated. Deleted/penalty eligibility follows supplied SELECT; 770 test scores excluded locally. September7,986,079; October6,950,022. YTD January–October79,957,035 (+2.4062% vs same2025 months); October+4.6127%. All scope/population methods, breakdowns and association totals reconcile. Installed January2025–August2026 and earlier history preserved exactly. No GC breakdown inferred.

Updated totals, posting mix/application/API/holes/member-type composition, associations, reporting labels and the home score tile's shared data. Demographics remain through August2026, including matched Jan–August YTD comparisons. Scores Explorer remains October21 with October13 memberships. Neither section was relabeled as refreshed. Counts retain current primary-club attribution. Backups: `backups/scores-before-2026-11-06/`. Reproducible importer: `scripts/import_scores_sep_oct_2026.py`; UI source `scripts/scores_scope_view.js` mirrors embedded code. Local browser verified totals, AGA Regular filtering, posting versus demographic periods, association periods and Explorer's unchanged date; no console errors. No publication or push.

## September–October demographic import — November 6, 2026

Imported `scores_demographics_sep_oct_2026.csv.csv`; unchanged archive in `data/raw/scores/2026-11-06/`. 282,942 unique aggregate rows; 29 source timestamps17:31:49.886–17:41:01.787 -0500. Exactly September/October, nonnegative counts and valid flags; no duplicate dimension groups. SHA-256, every capture timestamp, source reconciliation and YTD demographic totals: `reports/scores_demographics_incremental_2026-11-06.json`. Preserve batches rather than claiming a single frozen snapshot.

Non-test totals September7,986,075 and October6,949,981, respectively4 and41 below the earlier posting-mix export. Independent scope/population classification differences are retained (maximum absolute selected-month difference54). All six demographic dimensions and association sums reconcile to their own source totals. 770 test scores excluded. Existing demographic months were preserved exactly; all headline/posting totals, posting association history and pre-2025 history unchanged. Full demographic YTD79,957,107 differs from headline79,957,035 by72 because earlier separately sourced demographic history already differed by117, followed by the new -45 difference. No adjustment/rescaling or fabricated balancing rows.

Age, gender, public/private and club-group charts now cover Jan–October2026, with matched Jan–October comparisons. Posting-index notes reference the current November3 membership baseline. Scores Explorer remains October21 with October13 memberships and was not refreshed. Importer: `scripts/import_scores_demographics_sep_oct_2026.py`; backup `backups/scores-before-demographics-2026-11-06/`. Local browser checked four demographic totals, October labels, YTD comparison cutoff, International/Regular filters and no console errors. Local update only; no new GitHub or USGA Azure publication.

## November 6, 2026 — Scores Explorer refresh (local)

Imported score_participation_2026-11-06.csv.csv: 3,825,075 rows, unique by population/golfer, zero duplicate keys or unexpected populations. Non-trial: 3,665,462 golfers (820,525 zero; 605,228 with 1–7; 2,239,709 with 8+). Trial: 159,613 golfers (131,424 zero; 27,375 with 1–7; 814 with 8+). The pools overlap by 38 golfers and are not additive.

Score created_at window starts January 1 and ends at each recorded execution time: November 6, 18:17:51.397–18:27:22.369 America/New_York, 383 timestamps. This includes partial November and is not one frozen read; monthly totals/composition/associations remain completed October. Membership attributes use the November 3 archive. Unmatched current-eligibility golfers remain in overall totals with actual score bands: 3,259 non-trial and 1,893 trial; matched-attribute selections exclude these unknown affiliations. Trial counts include all qualifying YTD scores for currently eligible golfers, not trial-flagged-only scores. Club Group GC Clubs selects matched GC membership rows.

Private raw source archived at data/raw/score_participation_2026-11-06/. SHA-256: 4befb7f852caa3e4023c96d775e646a2610ac05fd90a708d872fb5d06febed3d. Builders: scripts/build_score_explorer_2026_11_06.py (--trial); scripts/install_score_explorer_2026_11_06.py. Source audit: reports/score_participation_intake_2026-11-06.json; per-population validation reports retain all capture timestamps. Only anonymous grouped patterns embedded. Local refresh only; no GitHub or USGA publication.

## November 7, 2026 — four Scores Explorer posting bands

Split the prior 8+ score bucket into 8–24 and 25+, using exact ytd_score_count values in the existing November 6 export. No database query, new export, source-period change, or population change. Both trial and non-trial Explorer data, grouped tables, percentage sorting, stacked bars and responsive bucket cards now use 0 / 1–7 / 8–24 / 25+. Existing membership joins were reused read-only with identical cells and labels.

Non-trial bands: 820,525 / 605,228 / 1,043,019 / 1,196,690. Trial: 131,424 / 27,375 / 766 / 48. Total golfer counts, source score counts and unmatched populations are unchanged. Each new upper pair reconciles exactly to the previous 8+ bucket. Validation: reports/score_explorer_four_bands_2026-11-07.json. Builder: scripts/build_score_explorer_2026_11_06.py (--reuse-matches; --trial for trial). Local review only; nothing published.

## November 7, 2026 — 50+ Scores Explorer band

At Evan's request, split 25+ into mutually exclusive 25–49 and 50+ score bands. The five bands are 0 / 1–7 / 8–24 / 25–49 / 50+. Source remains the November 6 participation export, with November 3 membership attributes and unchanged score eligibility. No new query or export. Non-trial counts: 820,525 / 605,228 / 1,043,019 / 715,788 / 480,902. Trial counts: 131,424 / 27,375 / 766 / 41 / 7. The upper two bands sum exactly to the former 25+ bucket; source score totals, golfer totals, membership cells and unmatched populations are unchanged. Cards, stacked bars, grouped tables and percentage sorting use all five bands. Validation: reports/score_explorer_five_bands_2026-11-07.json. Local only; no publication.

## November 7, 2026 — collapsible Scores Explorer comparison chart

Added Show chart beside Group results by. Starts collapsed on load with the established table visible. Expanding replaces the table with horizontal 100% stacked bars using all five posting bands; collapsing restores the same table selection and sorting. Grouping, scope, member population and per-record Explorer filters feed the existing result calculation unchanged. Group counts are unique within each group; affiliations can overlap. Exact segment counts and percentages are available through hover titles and accessible labels. Chart sorting uses the shared sort state and has its own direction control while table headers are hidden. Up to 100 groups, with a bounded scroll area and responsive labels. Existing embedded trial/member payloads verified unchanged. Local preview checks matched AGA Regular values in Evan's screenshot, Age grouping, GC intersection and empty results. Validation: reports/score_explorer_group_chart_2026-11-07.json. No publication.

## November 7, 2026 — line comparison replaces stacked group bars

Evan rejected stacked group bars as difficult to compare. Replaced that chart with categorical line distributions: posting bands on x, share within each group on y. Straight segments connect measured band percentages; no smoothing or inferred intermediate values. Four representative affiliations selected initially, with a collapsed Choose groups checklist for adding/removing curves. Other groupings start with up to four groups. Membership/association filters still feed the same result calculation; member/trial dataset switches reset line selections safely. Exact percentage/count/source group total is in each point's hover title and accessible label. Colors remain stable across filters. No table-sort caption is shown in line mode. Chart remains collapsed by default and replaces the table while expanded. Original stack-chart notes above are superseded. Source payloads unchanged; local only. Validation: reports/score_explorer_line_chart_2026-11-07.json.

## November 7, 2026 — line chart controls and legend refinement

Moved Choose groups and its checkboxes below the graph. Removed the introductory sentence. Moved the categorical-band/denominator/multiple-affiliation note into the existing collapsed Show data and definitions area. Legend labels increased to 15px; legend and checkbox swatches increased to 34x6px; chooser labels 14px; plotted line width 3.5px. Verified seven age groups selected with unknown/unmatched off, matching Evan's screenshots. Source payloads unchanged; no publication.

Exploratory profile question: existing anonymous membership-cell patterns retain joint intersections across demographic, affiliation, Index and creation-year dimensions, so combined zero-posting profiles can be analyzed without another export. No profile feature implemented. Non-trial usable-age coverage is 2,096,732 / 3,665,462; 1,568,730 lack usable age. Combinations must retain within-selection unique-golfer counting, report cohort sizes/unknowns and comparison baselines, and account for creation-cohort exposure. Creation year alone is coarse tenure; records are current membership attributes, not historical attributes at posting. An observed association is not a causal explanation. Validation: reports/score_explorer_controls_2026-11-07.json.

## November 7, 2026 — stable Data / Graph switch

Replaced Show/Hide chart with a fixed-width, right-aligned Data | Graph segmented control. Each button exposes aria-pressed and targets its result region; selected state updates independently of button labels. Grouping and view controls use a stable two-column grid. The data caption reserves its height while hidden in Graph view, preventing layout movement. Browser measurements were identical in both modes: x783.2, document y855, width164, height42.4 at the tested viewport. Mobile control width140px. Score payloads unchanged. Local only. Validation: reports/score_explorer_view_toggle_2026-11-07.json. Three earlier chart HTML backups were losslessly gzip-compressed with verified SHA-256 matches after a disk-space failure; the failed partial new backup was removed and recreated completely.

## November 7, 2026 — always-open group selection

Removed the group chooser accordion. Controls remain visible beneath the line chart in Graph view. All groups default checked except Unknown / invalid and unmatched active-membership groups. Defaults cover the complete grouping label set, so filters do not silently leave newly visible groups unchecked; manual choices persist during the session. Verified Age starts with seven valid groups checked and both requested exceptions unchecked, and manual checkbox changes remain functional. Source payloads unchanged; local only. Validation: reports/score_explorer_open_groups_2026-11-07.json.

## November 7, 2026 — styled score line-point rollovers

Replaced native browser point titles with white callout cards: series-colored accent and marker, group label, large percentage, posting band, and separate golfer count/denominator. A connector links card to point. Cards render in an SVG overlay after all series, with positions clamped to chart bounds and placed above or below the point. Point hit areas enlarged; the same callout appears on keyboard focus. Pointer hover takes priority when another point retains keyboard focus; leaving/blur dismisses. Exact accessible labels remain. Verified 45–54 / 8–24: 34.5%, 86,701 of 251,277; right-edge and upper-left cards stay inside the plot; dismissal leaves zero cards visible. Source payloads unchanged. Local only. Validation: reports/score_explorer_callouts_2026-11-07.json.

## November 7, 2026 — remove unmatched graph category; Unknown off by default

Removed the unmatched active-membership group from graph rendering and its checkbox options for every dimension. Retained those golfers in source/overall totals and the existing data table; their source posting-band counts are documented within collapsed Show data and definitions. All category names beginning Unknown now default unchecked, including Unknown Access, Unknown / invalid, Unknown Index/gender/year labels and Unknown public/private access. Users may explicitly enable Unknown if needed. Other categories remain default on; manual choices persist within the session. Verified Age, Club Group, Public/Private and Handicap Index in the local browser. Source payloads unchanged; no publication. Validation: reports/score_explorer_unknown_cleanup_2026-11-07.json.

November 7, 2026: Removed the Scores Explorer group-count/sort-direction status caption at Evan's request. Grouping, Data/Graph toggle and table-header sorting remain functional. Local only.

## November 7, 2026 — one filter area on Scores Explorer

Removed the association-scope and member-population dropdowns above Explorer only. The existing Select filters builder now includes Association Scope (All Associations / AGA Only / International Only) and Golfer Population (Members / Trial Golfers); Regular, Junior and Unclassified remain under Membership Type. Nondefault scope/population selections appear as removable filter chips beside existing cell filters, and Clear all resets every Explorer selection. Trial remains the separate established participation dataset; switching member/trial populations retains the prior behavior of clearing dataset-dependent cell filters. Explorer now owns scope and population state independently of Totals/Composition/Associations, preventing hidden inherited filters. Other Scores pages retain their top controls. Intro displays reporting period, with active choices shown by chips.

Local browser checks: default members 3,665,462; AGA + Regular 3,157,019 with unchanged band counts; Trial 159,613; International 94,897. Totals controls retained; switching from AGA Regular Totals to Explorer did not restrict Explorer secretly. Source payloads unchanged; no publication. Validation: reports/score_explorer_filter_consolidation_2026-11-07.json.

## November 7, 2026 — reuse Membership Explorer naming

Removed the newly introduced Association Scope and Golfer Population filter categories. Scores now reuses Membership Explorer's core filter label map and order directly: Membership Type, Association, Public / Private, Club Group, Club Type, Gender, Age, Handicap Index, Club. Existing Scores creation-year filters remain available. All/AGA/International choices and individual associations are under Association; All Member Types, Regular/Junior/Unclassified and Trial Golfers are under Membership Type. Chips use the same established labels. Selecting a member type while viewing Trial correctly returns to member data before applying the type filter. Verified Trial159,613 and AGA+Regular3,157,019; payloads unchanged. Local only. Validation: reports/score_explorer_matching_names_2026-11-07.json.

## Tom request — offseason score reporting (November 12, 2026)

Requester: Tom Padula. Recorded by Evan's instruction from Screenshot 2026-11-12 at 1.45.00 PM.png. Status: pending; revisit after November 2026 ends.

Add offseason score details to the GHIN Scores section:
- Overall offseason score counts.
- Breakdowns by day, week, and month.
- Breakdowns by AGA.
- Consider Scores Explorer as the location for the detailed breakdowns; Tom suggested it as a possibility.

Before implementation, agree on the offseason definition and whether classification follows date played or date posted, including how differing AGA season calendars should apply. These are unresolved implementation details, not additional requirements from Tom. No UI, query, data, or publication changes are authorized by this note.

## Tom request — historical monthly score comparisons (November 5, 2026; recorded November 12)

Requester: Tom Padula. Source: Screenshot 2026-11-12 at 1.45.48 PM.png. Evan clarified on November 12 that this request IS about comparing GHIN scores posted with NGF rounds played. NGF comparison is an explicit requirement; the earlier interpretation that it was only contextual is superseded.

Requested comparison:
- Monthly GHIN score-posting trends alongside NGF rounds-played trends.
- Historical lookback and aligned prior-year/monthly YoY comparisons for both measures.
- Period/YTD comparisons where supported by the respective sources; the reference shows January–October totals and YoY.

Tom linked https://www.ngf.org/monthly-rounds-played-reports/ and said he uses that website. He thinks USGA has a subscription but does not personally have one. Evan clarified that Tom says the NGF monthly rounds data is publicly available. Use the public monthly reports as the intended source; no subscription or access investigation is requested. The task is to compare rounds played by month with GHIN scores posted by month, aligning reporting periods and geographic coverage. GHIN postings and rounds played are different measures; compare trends rather than assuming their counts should match. Tom's GHIN reference numbers remain subject to the earlier export reconciliation.

Status: implemented locally November 12, 2026 following Evan’s explicit “DO IT” instruction. Public NGF reports are the agreed source for the rounds side of the monthly comparison. The separate offseason request remains pending after November ends. Leave the prior-year Scores Explorer reconstruction request alone per Evan's instruction. No query, data acquisition, UI or publication work is authorized by this clarification alone.


## November 12, 2026 — Scores vs Rounds comparison

Built a Scores vs Rounds subtab with year selection (2023–2026), Monthly/YTD line comparisons, common-cutoff YTD summaries, a collapsible source-linked data table, and collapsed Data notes. Uses existing AGA Only / All Member Types GHIN creation-month score history, preserving all established eligibility and attribution rules. No new score query or modification of existing data. This fixed comparison has no inherited Scores scope/member filters.

Public NGF intake: 45 monthly reports, January 2023–September 2026. PDFs, extracted text, original archive and SHA-256 hashes retained under data/raw/ngf/2026-11-12; processed values and exact report links in data/processed/ngf_rounds_played.json. Both monthly and published cumulative YTD U.S. national YoY percentages independently cross-checked with pypdf and pdfplumber (rotated watermark characters removed for the independent text extraction). NGF absolute round counts are not provided in these reports and are not inferred. Published YTD changes are used directly, never averaged from monthly changes. Missing months remain null, not zero. GHIN October remains visible while NGF currently ends in September.

Latest common period January–September 2026: GHIN 71,081,643 vs 69,695,438 (+1.99%); NGF +0.1%. These are different populations and measures; the view compares trends, not equivalent counts. Validation: scripts/check_scores_rounds.cjs and reports/scores_ngf_comparison_2026-11-12.json. 90 monthly/YTD row checks passed; all pre-existing embedded JSON payloads are byte-identical to the backup. Local browser review verified all year controls, Monthly/YTD switching, unchanged Totals filters and missing October NGF. No GitHub or Azure publication. Offseason and historical Explorer reconstruction requests remain unchanged.


November 12, 2026: Reformatted Scores vs Rounds Show data to match Tom's horizontal monthly layout: prior year/current year/YoY rows, followed by NGF YoY. Positive changes green, negative red. Final YTD column explicitly uses the common reporting cutoff for both sources, avoiding presenting September NGF YTD as Jan–Oct. Source links retained on NGF percentages, unavailable values remain dashes. Monthly/YTD controls and source data unchanged. Local review only.

November 12, 2026: Restored the GHIN-minus-NGF percentage-point difference in the horizontal comparison table, as a Difference (pp) row for each month and common-cutoff YTD. Requested by Evan; source data and formulas unchanged. Local only.

November 12, 2026: Moved comparison report-availability note into collapsed Data notes. Scores vs Rounds axis now fixed at −10% to +20%, with seven ticks every five percentage points, for all years and Monthly/YTD modes. Local only.

November 12, 2026: Added faint vertical month gridlines and short horizontal-axis month ticks to Scores vs Rounds. Local only.

November 12, 2026: Replaced comparison year dropdown with a 2026 / 2025 segmented year toggle, as requested to introduce just the previous year first. Updates graph, data table and YTD summaries; Monthly/YTD mode retained. Older source history preserved. Local only.

November 12, 2026: Added 2024 to the Scores vs Rounds year toggle, using the already verified twelve 2024 NGF reports and existing GHIN history. 2024 compares with 2023. Local only.

November 12, 2026: Moved AGA-affiliated GHIN scores / U.S. NGF rounds context into Show data and added a light grey background to both top YTD callouts. Local only.

November 12, 2026: Restored white backgrounds on Scores vs Rounds top callouts at Evan’s request. Local only.

November 12, 2026: Scores vs Rounds Show data now defaults open; removed the redundant monthly comparison table caption at Evan’s request. Local only.
