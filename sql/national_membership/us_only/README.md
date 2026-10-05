# U.S. membership exports

Each SQL file produces its own export. Run against Production BigData using DBeaver's Query the database CSV export.

Working scope: membership association_id belongs to an association with parent_federation = United States Golf Association and is_test = No. Includes Golf PR; excludes Guam. This is association affiliation, not golfer residence. No association status or is_aga restriction is imposed. Existing active/inactive, membership type, trial, and non-test club rules are preserved.

These are filtered alternatives to the original worldwide SQL scripts in the parent folder. Original raw exports and worldwide aggregates are retained for reversal. Trial association 237 is outside this U.S. working scope, so there is no U.S. trial export here.
