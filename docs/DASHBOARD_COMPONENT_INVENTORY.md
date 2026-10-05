# Dashboard Component Inventory

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
| Acquisition KPI row | Current and YTD new-golfer measures | Monthly/YTD | acquisition.json | mock |
| New Golfers — Monthly YoY | Same-month acquisition across years | Same-month history | acquisition.json | mock |
| New Golfers Cumulative YoY | Cumulative acquisitions through selected month | YTD history | acquisition.json | mock |
| New Golfers by Month | Monthly acquisition trend | Monthly | acquisition.json | mock |
| New Golfers YTD Pacing YoY | Cumulative pacing by month | Monthly YTD | acquisition.json | mock |

## Membership — Retention

| Component | Business meaning | Period type | Proposed JSON owner | Status |
|---|---|---|---|---|
| On-Time Renewal Rate | Renewal completion by due period | Monthly | retention.json | mock |
| On-Time Renewal KPIs | Eligible, renewed, and not renewed | Monthly | retention.json | mock |
| 12-Month Rolling Retention | Rolling retained share | Rolling 12-month | retention.json | mock |
| Rolling Retention KPIs | Base, retained, and not retained | Rolling 12-month | retention.json | mock |

## Membership — Recovery

| Component | Business meaning | Period type | Proposed JSON owner | Status |
|---|---|---|---|---|
| Recovery KPI row | Current and YTD reactivation measures | Monthly/YTD | recovery.json | mock |
| Monthly Reactivations | Monthly recovered golfers | Monthly | recovery.json | mock |
| Reactivations YTD Cumulative | Cumulative recovered golfers | Monthly YTD | recovery.json | mock |

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

