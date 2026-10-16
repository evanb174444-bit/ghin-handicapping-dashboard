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
