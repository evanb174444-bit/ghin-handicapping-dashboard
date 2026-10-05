-- Monthly posted entries, including trials and Temporary/UnderReview records.
-- Retain all statuses for inspection; exclude deleted and flagged penalty entries.
SELECT
    DATE_TRUNC('month', created_at)::date AS posting_month,
    status,
    is_trial,
    COUNT(*) AS score_count
FROM public.scores
WHERE created_at >= TIMESTAMP '2025-01-01'
  AND created_at <  TIMESTAMP '2026-09-01'
  AND deleted = false
  AND penalty IS NOT TRUE
GROUP BY 1, 2, 3
ORDER BY 1, 2, 3;
