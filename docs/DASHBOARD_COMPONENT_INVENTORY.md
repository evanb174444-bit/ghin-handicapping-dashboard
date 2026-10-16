## GC Membership submenu — October 15, 2026

Renamed the GC secondary-nav label Membership Totals to Membership (internal route retained). Added Totals and Acquisition submenu. Totals shows the existing GC summary iframe; Acquisition shows only the new joiner-comparison chart. Defaults to Totals. Acquisition controls retain their in-session state when switching tabs. Source scripts/gc_membership_view.js, installed by install_gc_joiner_chart.py. Supersedes the earlier below-Totals placement.

## GC Membership Totals joiner chart — October 15, 2026

Appended GC New Members by Year beneath the GC membership summary iframe in the main dashboard. Same restrained blue stacked-bar style as national acquisition, YTD (default), Annual Totals, Monthly lines, all years 2022–2026, month cutoff, line-year toggles, counts/YoY, Show data and collapsed Data notes. New to GC stacks Existing GHIN and New to GHIN plus one unresolved date record in 2026. New to GHIN switches to same-day creations only and recalculates both periods and axes. This chart is based on GC membership creation cohorts, not national GHIN creation cohorts. Toggles redraw only the new chart, preserving the summary iframe. Current-extract distinct counts can differ from original monthly snapshots. Scripts: build_gc_joiner_history.py, gc_joiner_view.js, install_gc_joiner_chart.py, check_gc_joiner_chart.cjs. Data: data/processed/gc_joiner_history.json. Browser and numeric checks passed; local only.

## Acquisition Show GC toggle — October 13, 2026

Added checked-by-default Show GC control. When off, bar totals, axis scale, data table, monthly lines, and prior-year percentage comparisons exclude GC for both compared periods. Title explicitly says excluding GC. Toggle state persists across modes and scope/population changes during the page session. Default chart remains stacked with GC on top and labels in both segments. Browser validation checks both states for all three modes and nine scope/population combinations, including the partial 2026 annual comparison against Jan–Sep 2025.

## Acquisition GC stacks — October 13, 2026

YTD and Annual Totals bars now stack GC above Other, preserving the original total. Uses distinct golfers by golfer_creation_date and the established 57 GC club IDs, all membership statuses, existing scope/population filters. GC means a matching GC membership in the October 13 detail export, not proven acquisition through GC. Golfers with both GC and other memberships are assigned to GC within the selected scope/population; Other is total minus GC. Total and GC originate in separate October 13 exports (known small source timing differences are not silently corrected). Data: data/processed/acquisition_gc.json; builder: scripts/build_acquisition_gc.py, followed by scripts/import_acquisition_history.py to install. Show data includes total, GC, Other. All non-null GC monthly counts validated between zero and total; browser checks cover all modes across nine filter combinations and stack arithmetic. Local only.

## Acquisition cleanup — October 13, 2026

Per Evan’s latest request, acquisition now has one full-width New Golfers Created by Year chart with YTD, Annual Totals, and Monthly modes. Removed the four redundant chart cards. Retained muted blues, all years in bars, line-year toggles, per-year change labels, Show data, and scope/population filters. This supersedes the restoration note below. Source counts unchanged.

## Acquisition chart restoration — October 13, 2026

Kept the new summary chart and restored Monthly YoY, Cumulative YoY, New Golfers by Month, and YTD Pacing below it. Summary defaults to YTD and all seven years. Bars always show all years; only line charts offer year toggles. Muted blue palette, full-width summary plot, and same-period percent change above each annual bar (2020 has no prior-year comparison). Summary cutoff is independent of the restored charts.

## Acquisition chart simplification — October 13, 2026

Replaced four acquisition charts with one New Golfers Created by Year card matching the GHIN trials chart. Modes: YTD (same months), Annual Totals (2026 explicitly partial), and Monthly (lines). Defaults to 2024–2026 with 2020–2026 year toggles, a YTD cutoff selector, exact counts, a same-period prior-year change on the latest visible bar, and Show data. Existing geography and population filters apply. Source counts and definitions are unchanged. Validated all modes across nine scope/population combinations and checked rendering. Local only.

# Dashboard Component Inventory

Later October 13 acquisition update: monthly database aggregates for January 2020–September 2026 are connected locally. Monthly YoY, cumulative YoY, monthly trends, and YTD pacing are available with AGA/International/All Associations and All/Regular/Junior selections. These supersede the earlier 2026-only acquisition status below. Source: `data/processed/acquisition.json` and `reports/acquisition_history_validation.json`.

October 13, 2026: the [membership refresh report](../reports/membership_refresh_2026-10-13.md) supersedes the original planning inventory for membership-related views. Current totals, composition, Explorer, association/club rollups, and home membership figures are connected to the October 13 export. Acquisition uses confirmed Creation Date cohorts for January–September 2026. Retention/recovery show unavailable history. Billing history and other modules retain their separate sources.

Status values:

- `mock`: current approved visual uses embedded placeholder data
- `awaiting source`: no authoritative source has been assigned
- `connected`: generated JSON is the source

## Summary

| Component | Business meaning | Period type | Proposed JSON owner | Status |
|---|---|---|---|---|
| Active Handicap Index Golfers hero | Certified active golfer population | Snapshot | membership.json | mock |
| Active Golfers trend card | Monthly active population and comparisons | Monthly snapshots | membership.json | mock |
| Scores Posted trend card | Monthly score-posting volume | Monthly activity | scores.json | mock |
| Enhanced GPS Subscribers trend card | Subscriber population | Monthly snapshots | advanced_gps.json | mock |
| GHIN Trials card | Trials created and converted | Monthly activity | ghin_trials.json | mock |

## Membership — Composition

September 22, 2026 update: current composition snapshots, population controls, the Public breakdown, and four membership/golfer counts are connected locally through `data/processed/membership_composition.json`, embedded in the standalone HTML. Historical composition trends show an unavailable state. Age coverage and source dates are displayed. Other modules retain their existing sources. The original planning statuses below are superseded for these current composition snapshots.

| Component | Business meaning | Period type | Proposed JSON owner | Status |
|---|---|---|---|---|
| All / Regular / Junior selector | Population selection applied to the module | Snapshot selector | membership.json | mock |
| Access Type | Public/private member composition | Snapshot and annual history | membership.json | mock |
| Membership Type | Regular/junior composition | Snapshot and annual history | membership.json | mock |
| Club Type | Member composition by club type | Snapshot and annual history | membership.json | mock |
| Gender | Member composition by gender | Snapshot and annual history | membership.json | mock |
| Age Profile | Average age and age-band distribution | Snapshot | membership.json | mock |
| Handicap Index Profile | Average index and index-band distribution | Snapshot | membership.json | mock |

## Membership — Totals

| Component | Business meaning | Period type | Proposed JSON owner | Status |
|---|---|---|---|---|
| Total Membership Trend | Same-date annual active totals | Annual snapshots/YTD | membership.json | mock |
| Year-over-Year Trend | Selected-month active totals across years | Same-month history | membership.json | mock |
| Year-End Projection | Actual membership plus approved scenario projection | Actual and projected | membership.json | mock |

## Membership — Acquisition

| Component | Business meaning | Period type | Proposed JSON owner | Status |
|---|---|---|---|---|
| Acquisition KPI row | New golfers monthly/YTD and separately labeled current Active counts | Monthly/YTD and current extract | acquisition.json and international_totals.json | connected |
| Prior-year comparisons | Prior-year creation cohorts not supplied | Same-month/YTD history | acquisition.json | awaiting source; sample comparisons removed |
| New Golfers by Month | Distinct GHIN numbers by golfer_creation_date | January–September 2026 | acquisition.json | connected; represented membership population |
| New Golfers YTD | Cumulative 2026 acquisitions | Monthly YTD | acquisition.json | connected; represented membership population |

## Membership — Retention

| Component | Business meaning | Period type | Proposed JSON owner | Status |
|---|---|---|---|---|
| Retention | Renewal cohorts and historical Active snapshots not supplied | Monthly/rolling 12-month | retention.json | awaiting source; sample figures removed from view |

## Membership — Recovery

| Component | Business meaning | Period type | Proposed JSON owner | Status |
|---|---|---|---|---|
| Recovery | Reactivation event history not supplied | Monthly/YTD | recovery.json | awaiting source; sample figures removed from view |

## Associations

| Component | Business meaning | Period type | Proposed JSON owner | Status |
|---|---|---|---|---|
| Association Size filter | Filters associations by active HCP population | Snapshot filter | associations.json | mock |
| Allied Golf Association Landscape | Association membership and club measures | Snapshot/comparison | associations.json | mock |
| Five-year membership lightbox | Association active golfer history | Annual snapshots | associations.json | mock |
| Ranking tiles | Highest and lowest association measures | Snapshot/comparison | associations.json | mock |
| Growth vs. Scale | Active population versus five-year growth | Snapshot/comparison | associations.json | mock |

## Scores

| Component | Business meaning | Period type | Proposed JSON owner | Status |
|---|---|---|---|---|
| Population selector | All/Regular/Junior score population | Segment selector | scores.json | mock |
| Score Posting Performance KPIs | YTD volume, GHIN volume/share, and posting depth | YTD | scores.json | mock |
| Scores Posted trend | Monthly score volume | Monthly | scores.json | mock |
| Scores by Type | Posting-type distribution and annual trend | YTD/annual | scores.json | mock |
| Scores by Membership Type | Regular/junior distribution | YTD | scores.json | mock |
| Scores by Provider | Provider distribution and annual trend | YTD/annual | scores.json | mock |
| Scores by Product | Product distribution and annual trend | YTD/annual | scores.json | mock |
| Scores by Association | Association posting performance | YTD/comparison | scores.json | mock |

## GHIN — Totals

| Component | Business meaning | Period type | Proposed JSON owner | Status |
|---|---|---|---|---|
| Enhanced GPS summary | Subscriber total and trend | Snapshot/monthly | advanced_gps.json | mock |
| GHIN Trials summary | Trial conversions and trend | Monthly | ghin_trials.json | mock |
| Total Challenges | Challenge program volume | Program-to-date | ghin_challenges.json | mock |
| Total Challenge Golfers | Challenge participation | Program-to-date | ghin_challenges.json | mock |

## GHIN — Trials

| Component | Business meaning | Period type | Proposed JSON owner | Status |
|---|---|---|---|---|
| Trial KPI row | Created, converted, rate, active, and inactive | YTD/snapshot | ghin_trials.json | mock |
| Created vs Converted | Monthly trial funnel | Monthly | ghin_trials.json | mock |
| Conversion Rate Trend | Monthly conversion performance | Monthly | ghin_trials.json | mock |
| Conversions by Days in Trial | Conversion timing distribution | YTD | ghin_trials.json | mock |
| AGA Trial Conversions | Association conversion ranking | YTD | ghin_trials.json | mock |

## GHIN — Advanced GPS

| Component | Business meaning | Period type | Proposed JSON owner | Status |
|---|---|---|---|---|
| Enhanced GPS Subscribers | Subscriber total and trend | Snapshot/monthly | advanced_gps.json | mock |
| Subscriber Retention & Lapse | Monthly/YTD retention and lapse opportunity | Monthly/YTD | advanced_gps.json | mock |
| Retention Rate trend | Monthly retained share | Monthly | advanced_gps.json | mock |
| Upgrades vs Renewals | New upgrades and renewals | Monthly | advanced_gps.json | mock |

## GHIN — Challenges

| Component | Business meaning | Period type | Proposed JSON owner | Status |
|---|---|---|---|---|
| Challenge KPI cards | Program scale and participation measures | Program-to-date | ghin_challenges.json | mock |
| Program Trend | Association, challenge, and golfer growth | Selected checkpoints | ghin_challenges.json | mock |
| GHIN Challenges by AGA | Association challenge performance | Program-to-date | ghin_challenges.json | mock |
| GHIN Challenge Site Performance | Individual challenge performance | Program-to-date | ghin_challenges.json | mock |

