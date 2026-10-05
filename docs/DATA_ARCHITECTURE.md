# Dashboard Data Architecture

## Separation of responsibilities

### Raw source data

Operational Excel, CSV, or system exports supplied by the metric owner.

Location:

`data/raw/<module>/`

Raw files are never loaded by the dashboard and are never edited by a generator.

### Processing logic

Module-specific generators:

`scripts/generators/<module>.js`

Each generator will:

1. locate its registered source;
2. validate sheets, columns, dates, types, IDs, and categories;
3. standardize source values;
4. apply approved business rules;
5. reconcile totals and components;
6. write dashboard-ready JSON;
7. write a validation report.

### Processed JSON

Published dashboard contracts:

`data/processed/<module>.json`

The dashboard reads processed JSON only. Percentages are stored as decimals. Each
file carries its source, report date, generation timestamp, and warnings.

### Presentation

The approved standalone dashboard remains the visual baseline. It may format,
filter, sort, select periods, and render charts. It must not reproduce source
cleaning or business calculations.

### QA and reconciliation

Validation output:

`data/validation/<module>.validation.json`

Errors block publication. Warnings require review.

## Module flow

```text
raw source
    ↓
module generator
    ↓
validation and reconciliation
    ↓
processed module JSON
    ↓
detailed dashboard module
    ↓
summary page using the same module JSON
```

## Initial module outputs

- `membership.json`
- `acquisition.json`
- `retention.json`
- `recovery.json`
- `scores.json`
- `associations.json`
- `ghin_trials.json`
- `advanced_gps.json`
- `ghin_challenges.json`

## Reporting-period convention

- Snapshot metrics use the certified report date.
- Activity metrics use the last fully completed period.
- For an August 1 report, snapshot values are as of August 1 and monthly activity
  is through July 31.
- Comparison values must use matching dates or matching completed periods.

## Incremental connection order

1. Membership Totals
2. Summary Active Golfers, consuming `membership.json`
3. Membership Composition
4. Acquisition
5. Retention
6. Recovery
7. Scores
8. Associations
9. GHIN Trials
10. Advanced GPS
11. GHIN Challenges
12. Remaining Summary widgets, consuming the same module JSON files

