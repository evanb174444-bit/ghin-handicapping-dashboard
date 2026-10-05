-- Find the verified geography fields before applying the U.S.-only scope.
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'v_associations'
ORDER BY ordinal_position;
