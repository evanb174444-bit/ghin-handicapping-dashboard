> Latest dated preparation: [November3 full-refresh package](../sql/refresh_2026-11-03/README.md). This advances the shared contract’s pending Trials assembly; no new database execution or dashboard installation is implied.

> For either dashboard’s next refresh, start with the [canonical shared GHIN + GC contract](/Users/EvanBelfi/Documents/Projects/USGA-GC-Dashboard/SHARED_DASHBOARD_REFRESH.md) and [GHIN inventory](GHIN_SHARED_REFRESH_HANDOFF.md). The provisional shared pack adds GC snapshot group 09 to the eight GHIN groups; Trials group 06 still needs consolidation.

## November 2, 2026: consolidated export process

Use the [export process and rulebook](DASHBOARD_EXPORT_RULEBOOK.md) and [eight-query package](../sql/dashboard_refresh/README.md) for the next refresh. This replaces the earlier 16-export handoff. Memberships and historical acquisition remain separate; monthly score posting mix and demographics remain separate to avoid the combined grouping workload, and participation shares one aggregation across trial/non-trial pools. Evan explicitly agreed to split the monthly score export on November 2. The unrun combined monthly score query was removed from the runnable package. Trials, GPS and Challenges each bundle their existing component results into one labeled CSV. Bundling reduces export steps but does not remove all source scans.

Completed monthly reporting ends October 31; current state and current-YTD participation retain execution-time definitions. SQL has been reviewed locally but not executed against Production BigData. The bundle unpack helper passed synthetic CSV/JSON round-trip checks. Existing importers still need dated paths, cutoffs and combined-input contracts adapted once the exports arrive. No dashboard data was installed or published. Older definitions and manual acquisition corrections remain in force.

## GC joiner comparison chart — October 15, 2026

Added below GC Membership Totals. Distinct GC joiners are assigned by earliest GC membership creation date within each year. Existing GHIN = earlier golfer creation calendar date; New to GHIN = same-day. User chooses New to GC (stacked total) or New to GHIN (only new segment). Jan–Sep2026:162,101 total,130,703 same-day,31,397 earlier dates,1 unresolved later golfer date. This is intentionally different from the national-chart131,175 GHIN-creation cohort and the GC dashboard’s161,556 monthly snapshot total. Monthly arrays reconcile to all independent annual and Jan–Sep migration cohorts. DefaultYTD, all fiveyears, annual2026partial; percentage comparisons use matched periods. Source October13 detail export and57approvedGC club IDs. Unknown never classified as new. Rebuild with scripts/build_gc_joiner_history.py then scripts/install_gc_joiner_chart.py.

## April 2023 GC migration check — October 14, 2026

Evan suggested April for possible TheGrint influx. Current-extract earliest-2023-GC-join reconstruction: April29,973 joiners,12,496 migrators (41.7%),17,477 same-day new. Migrators spread across all30 days and57GC clubs; peak April20=796. January larger:14,702 migrators of19,400 (75.8%). Current club front_end_provider=GHIN for all April migrators; this is not historical golfer referral attribution and does not identify/exclude TheGrint origin. No single-day bulk batch established. Report reports/gc_2023_migration_months.json; script scripts/analyze_gc_2023_migration_months.py.

## GC migrator date comparison — October 14, 2026

Evan defines migrator as Golfer Creation Date strictly before GC Membership Creation Date (calendar date). Scanned all qualifying GC memberships in October 13 detail export; no status filter. Deduplicated golfer within membership-creation year/period using earliest qualifying GC membership date in that period. Jan–Sep cohorts: 2022 total92,235 / migrators11,797 (12.8%); 2023 total182,820 /67,226 (36.8%); 2024 total154,178 /30,408 (19.7%); 2025 total165,159 /31,979 (19.4%); 2026 total162,101 /31,397 (19.4%). Full years: 2022 13,949/103,848 (13.4%); 2023 70,053/197,336 (35.5%); 2024 33,201/170,810 (19.4%); 2025 35,269/184,481 (19.1%). 2026 includes460 with earlier creation day in same year, beyond prior-year31k measure; same-day130,703; one golfer has creation date after membership. Same-day is a classification by date, not historical channel validation. Existing-GHIN additions do not themselves prove cancellation of another membership or causal diversion. These are current-extract reconstructed cohorts, not historical snapshots. Report reports/gc_migrators_by_year.json; script scripts/analyze_gc_migrators.py. No dashboard changes in this investigation.

## 2020 subgroup display correction — October 14, 2026

The prior manual correction affected All Members only, leaving the administrative spike visible in Regular Members. Fixed by omitting 2020 from AGA/All Associations subgroup charts and returning no 2020 subgroup prior-year comparison. No verified allocation of Steve’s corrected total among Regular, Junior, Unclassified exists; subtracting196,332 from Regular January would produce a negative count. Corrected All Members totals remain. Raw subgroup data preserved.

## GC acquisition definition reconciliation — October 14, 2026

Confirmed GC dashboard runbook uses membership creation date, while national acquisition stack used golfer_creation_date. October 13 detailed export with same qualifying GC clubs: 131,175 unique GHINs created Jan–Sep2026; 162,101 unique GHINs with GC membership created in period; 162,154 membership rows. Intersection 131,164. Membership-only group: 30,937 existing GHINs created before2026. Golfer-date-only group: 11. Difference between membership-row count and GC dashboard 161,556 is598, not fully reconciled; dashboard uses monthly snapshot history. Main 30K gap is a demonstrated definition difference, not evidence of omitted Central Comp/TheGrint records. Earlier speculation about Steve’s GC scope remains unconfirmed. Stack is new-to-GHIN golfers with GC affiliation, not all new GC memberships. Do not substitute new GC memberships into a stack of newly created GHINs without reconciling populations. Evidence: reports/gc_acquisition_date_reconciliation.json; script scripts/reconcile_gc_acquisition_dates.py. No chart or source data changes made during investigation.

## January 2020 manual adjustment — October 13, 2026

Evan explicitly requested removal of the flagged discrepancy from the default YTD chart. The 196,332 difference between raw AGA annual 678,301 and approved 481,969 is now subtracted from January 2020 in All Members, for AGA and All Associations. AGA January becomes 29,265; Jan–Sep 431,618; annual 481,969. Raw history preserved; display adjustment stored in data/processed/acquisition_adjustments.json. Monthly, YTD, annual, tables and prior-year comparisons use the correction. No individual membership records or population subgroups reclassified. Supersedes the earlier annual-only override limitation.

## Approved 2020 annual override — October 13, 2026

Evan selected Steve’s 481,969 for 2020 instead of the database-derived 678,301. Applied to AGA / All Members / Annual Totals only; 2021 annual YoY compares against 481,969. Database monthly and YTD counts retained because Steve’s monthly allocation is unavailable. Regular, Junior, International, and All Associations remain source-derived; no invented disaggregation. Source override persisted in data/processed/acquisition_annual_overrides.json and preserved by importer. Chart explicitly labels the override.

## GC pre-launch acquisition correction — October 13, 2026

Evan confirmed GC did not exist in 2020 or 2021. Acquisition GC segments must be zero for both years, regardless of current GC affiliation. Total acquisition counts are unchanged. Builder and processed GC data enforce this. From 2022, the current GC affiliation caveat still applies; this is not verified original acquisition-channel attribution.

## Trial conversion Creation Date check — October 13, 2026

Source: data/raw/ghin/trial_conversion_creation_dates_2026-10-13.csv.csv; query sql/ghin/24_trial_conversion_creation_dates.sql. 21 grouped rows, 2024 through September 2026. In 2025, 54,686 converted golfers with qualifying AGA membership have current golfer_creation_date equal to conversion date and a different trial created date. Another 24,123 have trial creation and conversion on the same day (ambiguous). These total 78,809 of 79,438 qualifying category counts (99.2%). Only 375 category counts have a creation year earlier than conversion year. 2,302 have no qualifying AGA membership on linked golfer_id. Aggregate categories are not independently deduplicated across categories. Results establish alignment of current Creation Date to conversion for most linked qualifying golfers, not historical mutation of date or GHIN ID. Do not assert trial conversions generally retain trial-start Creation Date. Dashboard unchanged.

## January 2020 acquisition investigation — October 13, 2026

AGA detail export: 225,598 January golfers versus later aggregate 225,597 (one-person unreconciled difference). January 2: 60,672; January 3: 125,752. Combined 186,424, or 82.6% of January. January 2 concentrations include Chicago District 42,425 and GAP 18,266. January 3 includes Maryland 45,546, Wisconsin 31,482, Indiana 24,878, Montana 23,899. Association groups overlap. This strongly supports bulk association loading/migration, but underlying administrative event not independently confirmed. No adjustment made. Hypothetically subtracting both days from aggregate 2020 total 678,301 gives 491,877 versus Steve 481,969; not a validated correction. Full diagnostics: reports/acquisition_jan_2020_diagnostics.json; script: scripts/analyze_january_2020.py.

## April–May 2025 acquisition investigation — October 13, 2026

AGA aggregate: April–May all golfers 128,649 (2024), 197,646 (2025), 146,071 (2026). Junior: 29,004, 101,444, 50,707. Regular: 99,100, 97,305, 95,708. Junior increase of 72,440 concentrates the 2025 spike; regular declined 1,795. Population groups overlap. Detail export points to Youth on Course/junior clubs across associations; top club increases vs 2024: SCGA Junior Club +6,075, GAP Youth on Course +5,248, YOC - Florida +5,032. Largest 2025 day in April/May: April 14, 9,105 distinct eligible golfers. Evidence does not establish whether records represent administrative imports or organic acquisition, or explain Steve’s filter. Detail export is one golfer higher in each of April and May than later aggregate. Dashboard left unchanged. Full group results and methodology: reports/acquisition_apr_may_diagnostics.json; reproducible scan: scripts/analyze_acquisition_spike.py.

# GHIN Dashboard Knowledge Base

Updated October 13, 2026. This is the entry point for agreed reporting definitions, source limitations, and the acquisition refresh handoff. Read these rules before preparing queries or quoting dashboard figures. Preserve the approved dashboard design and existing source data.

## Definitions and counting rules

Latest acquisition update, October 13: the database aggregate export `new_golfers_historical_2026-10-13.csv.csv` now supplies monthly counts for January 2020–September 2026. The local Acquisition view includes historical monthly and cumulative comparisons. It supersedes the earlier 2026 acquisition extract: AGA YTD is **423,809**, International **13,951**, and All Associations **437,725**. The only difference is one fewer May 2026 Regular golfer in AGA (and therefore in the combined scope); the export does not identify the reason. Active membership counts remain from the original October 13 membership export. See `reports/acquisition_history_validation.json`.

Evan clarified: no membership record means no membership. Do not characterize those golfers as missing from this membership-based reporting population or add a coverage caveat for them. Historical acquisition can be calculated directly in the database from Creation Date; the earlier restriction to 2026 was requested scope, not a data limitation. January 2020 has a large recorded cohort; no migration or other explanation has been verified.

Historical import: run `scripts/import_acquisition_history.py` after any full membership refresh installation, which otherwise installs the earlier 2026-only acquisition view. The historical view source is `scripts/membership_acquisition_history_view.js`. The prior dashboard/data were retained in `backups/acquisition-before-history-2026-10-13/`.

| Measure | Definition |
|---|---|
| New golfer | A unique GHIN number whose golfer Creation Date falls within the specified period. Evan explicitly confirmed this on October 13. |
| Active golfer or person described as an Active Member | A unique GHIN number with at least one qualifying membership marked Active at the reporting snapshot. Evan accepted this definition on October 13. |
| Total active memberships | All qualifying Active membership records. Multiple club memberships for one golfer count separately. This remains the main membership measure established September 21. |
| Unique golfers | Distinct golfer IDs after applying the selected population filters. |
| Multi-membership golfers | People with more than one qualifying membership, counted once each. |
| Additional memberships | Total memberships minus unique golfers in the selected population. |
| Handicap Index holders | Golfers who have established an Index. Do not substitute active golfer or membership totals, which include NH. |

Example: one golfer with three qualifying Active memberships contributes three memberships, one active golfer, one multi-membership golfer, and two additional memberships.

Creation Date determines acquisition timing. A new club membership, reactivation, trial conversion, or first established Index does not substitute for the golfer's Creation Date. Count the same GHIN number once within each selected reporting population. Do not sum distinct counts across overlapping associations or Regular/Junior groups to obtain a national total.

**Confirmed by Evan during the October 13 refresh: use `public.v_golfer_clubs.golfer_creation_date` for acquisition.** The earlier query used `public.v_golfers.created_at`, exported as `golfer_record_created_at`. These fields are not equivalent: 5,863,425 membership rows in the new export have different creation months. Evan explicitly selected `golfer_creation_date` after reviewing that discrepancy. Do not substitute golfer-record `created_at`, `membership_creation_date`, `association_membership_creation_date`, or `status_date`.

## Qualifying populations

These rules were established in earlier membership work and were brought back into the acquisition discussion on October 13. The simple unfiltered golfer query does not implement them.

- Include only clubs explicitly marked `c.is_test = 'No'`. Test clubs and unknown/missing test flags do not qualify.
- Association reporting uses associations explicitly marked `a.is_test = 'No'`. Unknown or unmatched associations must be identified separately rather than assigned to a known scope.
- AGA Only uses membership `association_id` matched to parent federation `United States Golf Association`. This includes Golf PR and excludes Guam. It is association affiliation, not golfer residence. Do not add an `is_aga` or association-status restriction.
- International Only uses a known, nonblank parent federation other than `United States Golf Association`. Blank/unknown federation is not international.
- All Associations combines qualifying AGA and international populations, deduplicating golfer IDs across them for unique counts. Preserve unresolved scope separately.
- All Members includes Regular, Junior, and Unclassified. Source `Standard` is displayed as Regular. Do not force NULL or unexpected membership types into Regular or Junior.
- Trial association **237** is separate from the main non-trial All Members population. Exclude the trial membership row, not a golfer's qualifying non-trial memberships. Trial classification takes precedence over membership type.
- NH memberships remain included in totals and composition. Display NH as No Index and exclude it from average Handicap Index. Unknown or missing details are not automatically NH; neither is zero.
- Retain all club statuses under the existing export rules. Membership status and club status are separate fields.

For acquisition, applying these population rules must not silently add a current-Active-only condition. Creation Date is the agreed event definition. Existing Active-only exports cannot establish complete historical acquisitions. Current membership affiliation also does not establish association or member type at the original creation date; any use of current affiliation must be disclosed.

## October acquisition query and result

Evan requested this year only. The supplied SQL covered **January 1 through September 30, 2026**, with an exclusive upper bound of October 1, the latest completed month at the time. It grouped `v_golfers.created_at` by month and counted distinct `golfer_id`, without joining membership, club, or association filters.

Evan ran the query in DBeaver and supplied the result screenshot on October 13:

| Month in 2026 | Unfiltered new golfer count |
|---|---:|
| January | 27,519 |
| February | 27,895 |
| March | 53,964 |
| April | 88,126 |
| May | 84,490 |
| June | 78,029 |
| July | 63,520 |
| August | 52,861 |
| September | 32,221 |
| Total | **508,625** |

**508,625 is an unfiltered diagnostic result, not the agreed reporting count.** The query did not exclude tests or trial association 237 and did not separate AGA/international or member types. It allowed trial-club golfers whose Creation Date fell within the period and applied no Active-status filter. No separate test count was measured, so the result alone does not establish how many test golfers it contains.

The assistant initially presented the result too broadly and omitted previously agreed population filters. Do not reuse that interpretation or publish the number as validated acquisition data.

`sql/national_membership/12_new_golfers_monthly.sql` is also unfiltered and spans completed months since 2020. It is a diagnostic draft, not an approved acquisition export. `11_acquisition_source_discovery.sql` is metadata discovery only. Neither replaces a scoped acquisition query.

## Dashboard source status

The Acquisition screen originally shown October 13 used mock data: **198,450 August 2026**, **1,566,570 YTD**, and related percentages were not operational results. The local refresh replaced that series with January–September 2026 cohorts using the confirmed `golfer_creation_date` field. Scope and population filters now use actual distinct counts, not scaled sample counts. See [refresh report](../reports/membership_refresh_2026-10-13.md).

The dashboard still mixes real extracts and other mock sections. The header Mixed source data does not establish whether a particular tile is real. Check each module's source and extraction date. Membership composition, current counts, association/club rollups, Explorer, and acquisition now use the October 13 export. Retention and recovery display “Historical data needed” because the supplied file cannot support those histories.

Current membership data comes from the October 13 export, queried in 1,026 batches between 2:33:37 and 2:48:26 p.m. Eastern. It is not a certified single-time snapshot. Current Active flags cannot reconstruct past month-end activity. Do not infer historical Active counts from the latest status or latest status-change date alone. Preserve the separately supplied historical billing series and GC month-end reports.

## Andrew Dzurita email handoff

Evan requested a reply answering Andrew's statistical questions, not an acknowledgement promising future work. No email was sent. The following values were checked in local files for the draft; they are dated evidence, not a fresh October 13 refresh:

| Topic | Local evidence and interpretation |
|---|---|
| Active unique golfers | U.S. associations: 3,544,477 from September 21–22 extracts. All associations: 3,637,459 from September 21–25 extracts. Includes golfers without an Index; not a replacement for Index-holder totals. |
| GC population | 545,018 active golfers for September 2026 month-end, versus 537,730 in August. The roughly 537K GC population is not first-time Index holders or new golfers. |
| GHIN app usage | 2,817,445 monthly active users in June 2026, approximately 2.7% above June 2025. App users are a different measure from unique GHIN golfer records. |
| Trial conversions by event date | 76,263 recorded January–September 2026. These are not necessarily conversions of trials created in those same months. |
| Trial creation cohorts | January–September 2026: 54,344 of 145,815 trials converted by October 2, 37.3%. Full 2025 creation cohort: 85,910 of 189,690 converted by October 2, 2026, 45.3%. Later observation and cohort maturity affect comparisons with an earlier published rate. |
| Scores January–August 2026 | All Associations: 65,020,934, up 2.98% over the comparable 2025 period. AGA: 63,278,443, up 2.74%. |
| Scores full 2025 | All Associations: 86,100,451. AGA: 83,884,129. Current counting rules differ from the email's 82.25 million; reconcile scope and eligibility before substituting. |

The draft did not validate the email's 537K first-time Index holders, 510K new golfers, 430K new GHIN users, 94.4% recreational scores, or more than 75% playing purely for fun. The later unfiltered 508,625 result does not resolve those definitions or establish a comparable update. Do not infer golfer motivation from posting totals or treat scores as distinct rounds without an established definition.

Source files: `data/processed/ghin_app.json`, `data/processed/ghin_live.json`, `data/processed/score_counts.json`, `gc-dashboard-summary/data/membership_monthly.json`, `reports/membership_composition_review_2026-09-22.md`, and the embedded membership geography aggregates in the main dashboard. Score scope and eligibility are documented in [score posting notes](SCORE_POSTING_NOTES.md).

## Database and export workflow

- Evan uses the Mac **Windows App** to access **tableau-desktop.usga.org**, where DBeaver runs. Do not assume DBeaver is installed locally on the Mac.
- The remote session showed an existing connection named **ghin2020pilot 2**. Its mapping to Production BigData was not confirmed in this conversation. The saved workflow calls for Production BigData, not Production Secondary; the database name alone does not certify that mapping.
- The assistant inspected the connection but did not run a query, change connection settings, or export data. Evan said stop and took over. He then ran the supplied 2026 query and provided the screenshot above.
- Existing CSV workflow: DBeaver result grid → Export Data → CSV → Query the database. Export all rows, UTF-8, comma delimiter, headers, double-quote quoting, empty NULL, number formatting off. Do not use a grid row limit as the full export.
- Existing remote destination is `C:\Users\V-EBelfi`; finished files are copied through Windows Explorer to Mac Downloads. Keep raw identifiers local and out of the published dashboard.
- Record source connection, extraction time, timezone, row count, population rules, and period bounds. Separate live exports are not automatically one consistent snapshot.

## October 13 refresh results and remaining limits

Evan executed `sql/national_membership/13_membership_refresh.sql` and supplied the compressed export. Archive Utility failed to expand its Deflate64 ZIP. The verified CSV is saved at `data/raw/membership_refresh_2026-10-13/membership_refresh_2026-10-13.csv.csv`: 4,172,285,048 bytes, CRC32 `043738ae`, matching the ZIP entry. The failed Downloads copy is not the authoritative source.

The file contains **10,251,896 unique membership IDs**, all membership statuses, and no duplicate membership IDs. Club and association eligibility fields and scope classifications were checked. Current Active totals include qualifying AGA/international rows only. Trial and unresolved rows remain separate.

| Scope | Active memberships | Active unique golfers | New golfers Jan–Sep 2026 |
|---|---:|---:|---:|
| AGA | 3,859,441 | 3,560,991 | 423,810 |
| International | 96,703 | 94,708 | 13,951 |
| All Associations, deduplicated people | 3,956,144 | 3,654,391 | 437,726 |

Acquisition uses `golfer_creation_date`, confirmed by Evan after the field discrepancy was identified. Each counted golfer's creation month was checked against all their memberships, including records outside the selected period. No conflicting months or missing Creation Dates were found. All membership statuses are included. Current membership affiliations do not prove affiliation at creation; golfers absent from the membership export remain outside coverage.

The 528,243 represented January–September golfers reconcile to 437,726 main-population golfers plus 90,517 trial-only golfers. Another 13 main-population golfers also have trial memberships and remain in the main count. AGA/international acquisition overlap is 35 people. The earlier 508,625 diagnostic used a different date field as well as different eligibility and extraction timing; its difference is **not** a measured exclusion count.

The corrected reusable query is `sql/national_membership/14_new_golfers_2026_scoped.sql`. It has not been executed against the database in this turn; the local counts come from the verified export.

The refresh pipeline is `scripts/audit_membership_refresh.py`, `scripts/build_membership_refresh.py`, `scripts/build_refresh_acquisition.py`, and `scripts/install_membership_refresh.py`. `finish_membership_refresh.py` supports completing aggregation from checkpoints with smaller disk sorts. Legacy September builders still reference older exports; do not rerun them as an October refresh. Private SQLite staging is regenerable and was removed after aggregate validation. Only anonymous aggregate cells and golfer-pattern counts enter the HTML.

Remaining limits: historical retention/recovery events, historical active snapshots, prior-year acquisition comparisons, and complete golfer-table coverage were not supplied. The connection's Production BigData mapping remains unconfirmed. No site was published and no email was sent.

## Collaboration preferences

Keep explanations short and simple. When Evan asks for a query, provide the query directly. Consult this knowledge base and the saved reporting rules before asking him to repeat definitions. Respect stop and I'll handle this instructions; do not continue computer control without a new request. Keep metric definitions and dated results distinct.

## Detailed references

- [Real data intake and approved classification rules](../REAL_DATA_INTAKE.md)
- [National membership export contract](../sql/national_membership/README.md)
- [U.S. scope](../sql/national_membership/us_only/README.md)
- [International export rules](../sql/national_membership/international/01_active_all_types.sql)
- [Data architecture](DATA_ARCHITECTURE.md)
- [Component inventory](DASHBOARD_COMPONENT_INVENTORY.md)
- [Score posting decisions](SCORE_POSTING_NOTES.md)

The detailed intake document remains authoritative for access-type mappings, Affiliate/WORE, Type 1/2/3, GC identification by the authoritative club list, NH handling, and composition drilldowns. This handoff does not change those rules.

## Membership Explorer counting toggle — October 21, 2026

Added Memberships / Unique Golfers toggle to the grouped results table. Unique counts derive from existing golferPatterns, deduplicated within each matching group after filters and population selection. Table ranking/share/NH counts/NH rates follow the toggle; first three summary cards retain memberships, unique golfers, and additional memberships. NH unique counts require at least one matching No Index membership. Unique shares use the overall distinct matching golfer denominator; overlapping groups can sum above 100%. No new export required. Source script and embedded dashboard both updated; not pushed.


### October 26: exact Handicap Index statistics in Membership Explorer
Average and median Index cards and grouped table columns use unique golfers with a valid numeric Index from the October 13 membership export, independent of the Memberships/Unique Golfers count toggle. NH and unknown values are excluded. Plus handicaps use negative arithmetic and display with a plus sign. Each row also shows the contributing unique golfer count.
All 3,859,441 existing AGA membership rows reconcile at the anonymous cell level. There are 3,119,595 golfers with valid Index values and no conflicting values across their memberships. GC Clubs: 521,674 valid unique golfers, mean 14.7981233491 (display 14.8), median 14.0. This replaces the earlier band-based estimate with exact source-value statistics. Private staging stays under data/raw/membership_index_stats; only anonymous cell patterns and Index values are embedded.
The audit also identified 45 numeric-index membership rows above 54.0, excluded from valid-index statistics. Existing membership totals and NH rates remain unchanged.

### October 26: local segment comparison
Membership Explorer now has Compare segments. It copies the current filters and population into independent A/B panels, with copy, swap, and return controls. Each panel has its own member population; the comparison uses those panel selections. Summary and grouped comparisons use unique golfers, exact average/median Index, valid Index count, and NH unique-golfer rate. Differences are B minus A, with percentage-point rate differences. Overlap is calculated from golferPatterns, counting people matching both segments even through different memberships. Existing Explorer selection is preserved when returning. Local browser checks passed for independent filters, inherited selection, grouping, differences, copy/swap, mobile overflow, and restored Explorer. Not published.

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

## Pending Tom request — November 12, 2026

Tom Padula requests offseason score reporting after November ends: overall counts, daily/weekly/monthly breakdowns, and AGA breakdowns, potentially in Scores Explorer. Full request and open definition questions are recorded in docs/SCORE_POSTING_NOTES.md under “Tom request — offseason score reporting (November 12, 2026)”. Recorded only; implementation pending.

## Pending Tom request — historical monthly score comparisons

Evan clarified November 12: Tom explicitly wants GHIN scores-posted trends compared with NGF rounds-played trends, including monthly history and aligned YoY comparisons. NGF is a required part of the request. Evan further clarified that Tom says the monthly NGF rounds data is public. Use the public NGF reports for a month-by-month comparison with GHIN score postings; do not treat subscription access as a prerequisite. Full details are in docs/SCORE_POSTING_NOTES.md under “Tom request — historical monthly score comparisons”. Offseason reporting remains a separate request; leave prior-year Scores Explorer reconstruction alone. Recorded only.


## November 12, 2026 — public NGF comparison

Scores → Scores vs Rounds is implemented locally. Compares existing AGA-affiliated GHIN score-entry YoY with published U.S. national NGF rounds-played YoY; Monthly/YTD modes and 2023–2026 lookback. NGF currently through September 2026, GHIN through October. Source archive: https://www.ngf.org/monthly-rounds-played-reports/. Intake and methodology: docs/SCORE_POSTING_NOTES.md; data/processed/ngf_rounds_played.json; scripts/import_ngf_rounds_2026_11_12.py. Validation: reports/scores_ngf_comparison_2026-11-12.json. Local review only; nothing published.


## November 12, 2026 — Membership acquisition vs rounds

Added Membership → Acquisition vs Rounds locally at Evan’s request. Reuses Scores comparison CSS and visual layout, with independent 2026/2025/2024 year and Monthly/YTD controls, two white YTD summaries, open horizontal data table, percentage-point difference row and collapsed Data notes. Fixed AGA Only / All Member Types acquisition history preserves established eligibility and manual adjustments; other Membership filters do not carry over. Reuses verified public NGF reports. Source histories unchanged. Acquisition’s vertical scale expands in uniform 5/10-point steps to avoid clipping larger changes. Local review only; no publication authorized for this new change.


November 12, 2026: At Evan’s request, both Scores vs Rounds and Membership Acquisition vs Rounds now use the established AGA / Regular population rather than All Member Types. Historical/current totals, YoY, callouts, point labels, data tables and percentage-point differences all use Regular data; NGF national all-golfer reports unchanged. Regular membership classification is not an age filter. Other dashboard views and all source payloads unchanged. Local only; prior GitHub publishing authorization does not apply to these new changes.


November 12, 2026: Membership Acquisition vs Rounds now has All Regular / GC only selection. Uses existing ACQUISITION_DATA.gc.history.aga.regular for both current/prior years, preserving the same AGA/Regular scope, with no new export. Chart, YTD summaries, table and differences update together. GC denotes a retained GC membership, including other club affiliations, not original acquisition channel. NGF national benchmark unchanged. All Regular remains the default. Local only.
