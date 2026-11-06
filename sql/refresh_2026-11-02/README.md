> Superseded for future runs by the [eight-export package](../dashboard_refresh/README.md) and [export rulebook](../../docs/DASHBOARD_EXPORT_RULEBOOK.md). Retained here for traceability.

# November 2, 2026 refresh

Run each numbered SQL file separately on the confirmed Production BigData reporting connection. Each produces one CSV; do not join these different data grains into one result.

01 is the large full membership export: all statuses, all creation dates. It supplies membership totals, composition, associations/clubs, NH, exact Index statistics, membership/score Explorer attributes, and detailed acquisition/GC cohorts. Do not add an Active-only or October-only filter.
02 supplies historical acquisition aggregates, January 2020–October 2026, including matching prior-year periods. It is used by the historical acquisition importer.
03 supplies Scores totals and Posting Mix, January 2025–October 2026.
04 supplies score demographic history, January 2025–October 2026. Older validated demographic files remain unchanged.
05–06 supply current active non-trial/trial golfers' YTD score counts, including zero scores. They run through execution time, preserving the existing Explorer definition, rather than stopping October 31.
07–10 supply Trials history, cohorts, current pools, and January–October conversion destinations.
11–14 supply current GPS reconciliation, monthly activity, tenure, and explicit renewal-status labels.
15–16 supply Challenges and challenge/course names.

Current-state figures are as extracted, not certified October 31 snapshots. Unbounded monthly histories can include November rows: processing must exclude partial November from completed-month charts. Trial cohort outcomes are observed through extraction. GPS activity is not verified paid transactions; explicit status labels do not establish actual auto-renew enrollment.

DBeaver: Export Data > CSV > Query the database; export every row, UTF-8, comma, headers, double quotes, empty NULL, number formatting off. Use the export filename in each file's first line. Record connection, timezone, extraction window, and exported row count. Separate executions are live reads, not one frozen snapshot. Raw identifiers stay local.

The SQL is adapted from existing project queries and has not been executed against the database. Before dashboard installation, reconcile results and update the builders' old source filenames, cutoffs, and dated assertions. Do not rerun the old October builders unchanged.

Additional sources remain necessary for GHIN app usage, historical active membership snapshots, retention/recovery events, and billing/GC month-end history. These queries do not supply those sources.
