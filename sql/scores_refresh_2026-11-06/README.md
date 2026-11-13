# Scores refresh — November 6, 2026

First export: `01_scores_totals_posting_mix.sql` → `scores_posting_mix_2026-11-06.csv`.

Read-only SQL prepared from November 3 group03; not executed or database-validated. Monthly score coverage January2025–October2026. Existing eligibility, primary-association/member-type rules and deduplicated posting labels retained. New `has_active_gc_membership` is an independent current Active GC membership flag using the approved 57-club list. A golfer with both kinds of membership belongs to GC Only; Exclude GC is the complementary golfer group. Historical scores do not establish historical GC affiliation. No membership join multiplies score counts.

Run the entire statement in Production BigData. Export all rows as UTF-8 CSV with headers, comma delimiter, double quotes, empty NULL, and numeric formatting off. Record actual export times/connection; preserve session timezone. Run heavy exports sequentially. Demographics and participation are separate follow-up exports. Existing importers require adaptation and validation before installation. No dashboard data or publication changed.

## Incremental run order (current)

1. `01_scores_sep_oct_2026.sql` → `scores_posting_mix_sep_oct_2026.csv` — returned and installed locally November6.
2. `02_scores_demographics_sep_oct_2026.sql` → `scores_demographics_sep_oct_2026.csv` — returned, validated and installed locally November6. September1 inclusive through November1 exclusive, exactly two months. Current gender/age and primary-club data, preserving the established score predicates. No posting-label extract joins; runtime is unmeasured and is not guaranteed to be shorter than the first export.

Export all rows with headers and number formatting off. Run one heavy export at a time. Prior history is retained during local import. Full-history files earlier in this folder are not needed for this incremental refresh.

3. `03_score_participation_current_ytd.sql` → `score_participation_2026-11-06.csv` — prepared, pending execution. Current Active trial/nontrial golfers and Jan1 through execution score counts, including zeros. Distinct population/golfer rows can overlap between populations. Metadata accompanies each row for capture provenance. This file can be larger than the two monthly aggregate exports because it has millions of golfer rows. Raw IDs stay private; importer must separate populations and preserve unmatched membership records. Existing October13-dated builder/installer must be adapted before running against this file and the November3 membership archive. No demographic or GC-membership inference from score counts alone.
