# Active snapshot trend

The overview now includes a trend within the active snapshot panel. It shares the panel association/member-type filters and offers Unique Golfers, Association Memberships and Club Memberships. Captures are dated October 13 and November 3, 2026; comparisons are since the preceding actual capture, not certified month ends. No interpolation is used. Billing history is independent.

Data: `data/processed/active_snapshot_history.json`. After preserving a new validated dated membership refresh folder with `international_totals.json`, `membership_associations.json` and `validation.json`, run `python3 scripts/update_active_snapshot_history.py`. It rebuilds the aggregate history and replaces the embedded constant. Each new date extends the chart and table automatically. The builder verifies association sums, unique association rows and unique-golfer ≤ association-membership ≤ club-membership totals for every supported scope/member-type combination. Do not use a current status export to fabricate earlier snapshots.

All Associations, All Member Types: Oct13 unique 3,654,391 / association memberships 3,781,260 / club memberships 3,956,144. Nov3 unique 3,664,334 / association memberships 3,792,188 / club memberships 3,968,982. Changes: +9,943 / +10,928 / +12,838. Local only; no publishing authorized.

The Overview now renders three smaller trend graphs directly beneath the three headline metrics. All three are visible together and share the snapshot filters. The separate trend card/measure selector is no longer displayed. Each metric shows the absolute/percentage change since the prior capture, actual capture dates, and point tooltips. The same history builder extends them with future captures.
