# National membership exports

Start with `01_active_standard.sql` to supply the largest current Membership and Associations population. Run the remaining Active files next, then the Inactive files. Each query produces one separate CSV; no combined national file or later splitting is required.

These queries continue the September 17 database handoff. They have not been executed against the database by this agent.

## DBeaver steps

1. Use the confirmed **Production BigData** reporting connection. Do not use Production Secondary. The name `ghin2020pilot` alone does not confirm the connection.
2. Open one `.sql` file in the SQL editor and press **Control+Enter**.
3. Right-click the results → **Export Data → CSV → Query the database**. This reruns the SELECT and exports all matching records, including rows not loaded in the grid.
4. Use UTF-8, comma delimiter, headers at top, header labels unchanged, double-quote quoting, empty NULL string, and **Format numbers unchecked**.
5. Save to `C:\Users\V-EBelfi` using the SQL filename plus the actual extraction date, with `.csv` as the extension. Repeat separately for each SQL file.
6. Copy finished CSVs from Windows Explorer into Mac Downloads. Do not open these large files in Excel.

Record the connection label, export start/end times, exported row count, and filename for each file. `extracted_at` records each SELECT's start time; separate exports are live reads, not one frozen snapshot. If the export performs multiple query executions, retain their timestamps and flag the file for review. A date in a filename does not certify a month-end snapshot.

## Files and coverage

| SQL file | Membership status | Population |
|---|---|---|
| 01_active_standard.sql | Active | Non-trial Standard |
| 02_active_junior.sql | Active | Non-trial Junior |
| 03_active_unclassified.sql | Active | Non-trial NULL or unexpected type |
| 04_active_trials.sql | Active | Association 237, any type |
| 05_inactive_standard.sql | Inactive | Non-trial Standard |
| 06_inactive_junior.sql | Inactive | Non-trial Junior |
| 07_inactive_unclassified.sql | Inactive | Non-trial NULL or unexpected type |
| 08_inactive_trials.sql | Inactive | Association 237, any type |

At a single database state these filters are mutually exclusive and cover all Active/Inactive memberships attached to clubs marked `is_test = 'No'`. Unknown/missing club flags remain excluded, matching the completed research. All club statuses are retained. Trial classification takes precedence over membership type. Missing association IDs remain in the non-trial groups and must be flagged during intake. Unexpected types are preserved verbatim in the unclassified export; they are not rewritten to NULL.

The Standard files will still be large. No additional population counts are needed before exporting. If a file is too large for the VM, subdivide that query in SQL using documented, nonoverlapping ID ranges; do not add LIMIT or split by fetched grid rows.

## What this supplies to the existing dashboard

| Dashboard need | Export fields / remaining decision |
|---|---|
| Membership totals and composition | Membership ID, golfer ID, status, raw membership type, gender, age, numeric/display Handicap Index |
| Associations and club composition | Membership association ID, club association ID, club ID/name, raw category/type, provider |
| Trial current population | Association 237, with both statuses retained separately |
| Acquisition and recovery preparation | Membership/golfer/association creation dates and latest status dates; historical events and national definitions still required |

No names, contact information, local numbers, or full dates of birth are requested. Golfer and membership IDs remain sensitive source data: keep raw CSVs local and out of the published dashboard.

## Processing contract before replacing any figures

- Stream CSVs into a disk-backed staging database in bounded batches. Do not use the GC in-memory updater for national data. This processing pipeline is still to be implemented.
- Preserve membership rows. Check that `membership_id` is nonempty and unique across the extraction set; flag duplicate rows rather than silently deduplicating. Join uniqueness has not yet been proven, so duplicate membership IDs must block dashboard integration pending review.
- Track missing golfer joins using `matched_golfer_id`, missing associations, club/membership association disagreements, raw classification values, and extraction windows.
- Reconcile against the exported files and their recorded row counts. Earlier live counts are dated context, not fixed expected totals. Status/type changes between exports can cause overlap or omission; a certified source snapshot is needed for strict reconciliation.
- Keep Active unclassified visible. Never assign Wisconsin or other NULL memberships to Standard/Junior using fixed adjustments.
- Evan confirmed on September 21, 2026: the big membership number and composition charts count all qualifying memberships, inclusive of multiple memberships per golfer. Also retain unique golfers, multi-membership golfers (people with more than one qualifying membership), and additional memberships (total memberships minus unique golfers). One golfer with three memberships contributes 3, 1, 1, and 2 respectively. See `../../REAL_DATA_INTAKE.md` for the approved rules.
- Calculate all four measures within the selected population. National unique golfer and multi-membership measures cannot be calculated by summing them across clubs, associations, or membership-type groups; recalculate from membership records and golfer IDs. Do not deduplicate the membership total by golfer.
- All Members includes non-trial Regular (source Standard), Junior, and Unclassified memberships, as approved September 22. Association-237 trial memberships are excluded and reported separately; qualifying non-trial memberships held by the same golfer remain included. Active NH memberships are included in totals, shown as No Index in the handicap breakdown, and excluded from the average Handicap Index. Label the main measure as memberships. Preserve the numeric and display index fields; do not interpret NH as zero or assume missing golfer details mean NH.
- Standard → Regular, access category mappings, Type 2/3 Public classification, and GC classification using Evan's authoritative club list are approved in `../../REAL_DATA_INTAKE.md`. Apply those rules while preserving source values and unknown green-grass access. Association master reconciliation and locating/loading the authoritative GC club IDs remain integration work.
- Current membership state does not supply certified historical active populations, renewals, trial conversions, scores, GPS, or Challenges. Historical snapshots/events and separate product sources remain necessary.

## Project continuity

The approved HTML in this workspace and in `/Users/EvanBelfi/Documents/Projects/GHIN Handicapping Dashboard` was byte-identical when preparing this package. SQL files were added to the current writable dashboard workspace only. The existing presentation and real GHIN App data were not changed, and nothing was published.
