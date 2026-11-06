# Scores refresh — November 6, 2026

First export: `01_scores_totals_posting_mix.sql` → `scores_posting_mix_2026-11-06.csv`.

Read-only SQL prepared from November 3 group03; not executed or database-validated. Monthly score coverage January2025–October2026. Existing eligibility, primary-association/member-type rules and deduplicated posting labels retained. New `has_active_gc_membership` is an independent current Active GC membership flag using the approved 57-club list. A golfer with both kinds of membership belongs to GC Only; Exclude GC is the complementary golfer group. Historical scores do not establish historical GC affiliation. No membership join multiplies score counts.

Run the entire statement in Production BigData. Export all rows as UTF-8 CSV with headers, comma delimiter, double quotes, empty NULL, and numeric formatting off. Record actual export times/connection; preserve session timezone. Run heavy exports sequentially. Demographics and participation are separate follow-up exports. Existing importers require adaptation and validation before installation. No dashboard data or publication changed.
