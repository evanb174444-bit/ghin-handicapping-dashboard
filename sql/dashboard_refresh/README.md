# Dashboard exports: start here

Use these **eight queries**, one CSV per query. This package replaces the 16-file November 2 handoff for future runs. Existing exports and dashboard files are unchanged.

Read [the export process and rulebook](../../docs/DASHBOARD_EXPORT_RULEBOOK.md) before running them.

| Run | SQL file | Save results as |
|---|---|---|
| 1 | [Memberships](01_memberships.sql) | memberships_2026-11-02.csv |
| 2 | [Acquisition history](02_acquisition_history.sql) | acquisition_history_2026-11-02.csv |
| 3 | [Scores: totals and posting mix](03_scores_posting_mix.sql) | scores_posting_mix_2026-11-02.csv |
| 4 | [Scores: demographics](04_scores_demographics.sql) | scores_demographics_2026-11-02.csv |
| 5 | [Score participation](05_score_participation.sql) | score_participation_2026-11-02.csv |
| 6 | [Trials](06_trials.sql) | trials_2026-11-02.csv |
| 7 | [Enhanced GPS](07_gps.sql) | gps_2026-11-02.csv |
| 8 | [Challenges](08_challenges.sql) | challenges_2026-11-02.csv |

Run each entire file as one statement. Export every row with headers. Files 6–8 contain labeled sections inside one CSV; do not manually edit their JSON column. They can be split locally with `scripts/unpack_dashboard_bundles.py`.

**Run the heavy exports one at a time.** Monthly posting mix and demographics stay separate to avoid the large combined grouping. Both still scan substantial score history; their first-run runtime is unverified.

Status: prepared from the existing project SQL and reviewed locally; not executed or validated against Production BigData. Existing importers need their dated paths/cutoffs and new input contracts updated before these exports can be installed. Nothing has been published.
