# GHIN Challenges golfer-count provenance

Inspected November 3, 2026 in `/Users/EvanBelfi/Documents/GHIN Handicapping Dashboard`. Read-only dashboard inspection; no content or data changed.

## Current primary GHIN page: no unique-golfer total

`Handicapping and GHIN Dashboard.html` embeds `GHIN_CHALLENGES_DATA` at line185976 and the active `ghinChallenges()` function at line186027 (line numbers as inspected). Embedded data matches `data/processed/ghin_challenges_live.json`: asOf October3, 2026, 968 eligible challenge rows, **48,361 summed golfer participations**, 16,829 ranked participations, 146,570 scores. The active view labels the measure “Total Golfer Participations” and explicitly warns a golfer may appear in multiple challenges. It does not calculate or display a deduplicated overall participant count.

Exact lineage:

1. `sql/ghin/16_challenges_export.sql:12` reads `public.challenges.no_of_golfers` (one row per challenge; no participant join).
2. Supplied raw CSV `data/raw/ghin/ghin_challenges_2026-10-03.csv`, `no_of_golfers` column.
3. `scripts/build_challenges_data.py:6` selects Active, explicitly non-test AGAs from the lookup; lines18–25 remove deleted/notVerifiedAga/explicit test IDs129 and933, and convert each source `no_of_golfers` to challenge `golfers`.
4. Builder lines28–30 write processed data and validation report. The report explicitly calls counts participations, not unique people.
5. `scripts/build_ghin_live.py` embeds processed Challenges JSON and `scripts/ghin_challenges_view.js` in the standalone HTML.
6. View line10 defines `challengeSum`; line51 sums `golfers` over all eligible challenges; line52 labels “Golfer Participations”; line53 prepends “Total” and includes overlap disclosure. No `COUNT(DISTINCT golfer_id)` or participant-ID input exists in this path.

Raw nondeleted pre-scope sum is 48,403 (989 challenges), as separately recorded in `data/validation/ghin_challenges.validation.json`. Applying verified-AGA/explicit-test filters yields 48,361 (968 challenges) in `data/validation/ghin_challenges_live.validation.json`. Neither is unique people. Distinct association IDs/courses/challenge IDs in the view are not distinct golfers.

## Older GHIN page: hard-coded 30,559, no demonstrated unique calculation

`Handicapping and GHIN Dashboard.current.html:183957` contains `function ghinChallenges()` with literal “TOTAL GOLFERS” = **30,559**, alongside769 challenges,329 active,434 completed,8,976 ranked and75,662 scores. In the main refreshed HTML the same function survives as inactive `legacy_ghinChallenges()` at line185698. It is not the active live view.

The separate older project copy `/Users/EvanBelfi/Documents/Projects/GHIN Handicapping Dashboard/Handicapping and GHIN Dashboard.html` also contains this hard-coded30,559 and no `GHIN_CHALLENGES_DATA` payload. Its existence matters if Evan has that older file open.

`gc-dashboard-summary/data/processed/ghin_challenges_growth.json` has a July1,2026 point with the same30,559 and companion counts. This corroborates the historical snapshot association, but **does not prove copy direction, original source screenshot, who supplied it, or that it was calculated as distinct golfers**. The GHIN function itself has no source reference or unique-golfer calculation. Do not describe this value as a newly verified participant-derived unique total, or confidently call it invented mock data solely because it is hard-coded.

## Historical GC copy: 37,777 attributed to admin header

`gc-dashboard-summary/data/processed/ghin_challenges.json` (an older bundled GC copy, not the current GC workspace) records:

- metadata generatedAt August28,2026 20:53:15.025254+00:00.
- metadata.sources[0]: “GHIN admin combined-status header (2026-08-25)”, role “authoritative unique-golfer and headline totals”.
- metadata.sources[1]: combined-status admin pages1–35, August25.
- metadata.sources[2]: `ghin_challenges_2026-08-25_compiled.csv`.
- metadata.definitions.totalGolfers: “Unique golfers from the combined admin header”.
- summary.totalGolfers = **37,777** (line45 as inspected); metadata.detailTotals.totalGolfers = **42,452 participations**, over863 challenge rows.
- `gc-dashboard-summary/data/processed/ghin_challenges_growth.json` also has this August25 point.

This is **stored attribution to a header**, not independent verification of the header's underlying query. No original August25 screenshot or compiled CSV was located in the inspected local GHIN workspace/Downloads filenames. The August24 CSVs in Downloads contain only aggregate challenge/status/association counts, not participant identifiers. No evidence here establishes whether Evan, Fran, another person, or automation transcribed the August25 header. No GHIN builder calculates37,777 from accepted participant IDs. The current main GHIN active Challenges view does not consume this GC summary field.

## Answer and remaining limit

The current GHIN dashboard did not solve unique Challenges golfers in the database: it uses explicitly labeled participation counts. Older literal “Total Golfers” snapshots need their own historical provenance; the37,777 GC copy is explicitly attributed to an admin header. None of the inspected national build paths establishes the accepted-participant roster or the admin header's backend lineage. The next source question remains which accepted/opt-out/deletion definition and actual source computes that header, and whether it is in the reporting database.
