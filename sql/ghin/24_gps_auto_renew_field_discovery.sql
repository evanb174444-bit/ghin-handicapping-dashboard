-- Export as gps_auto_renew_field_discovery.csv. Schema metadata only; no customer data.
-- Find dedicated renewal flags and potential store receipt/notification payloads.
SELECT table_schema, table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
  AND (
      LOWER(column_name) ~ '(auto.*renew|renew.*auto|renewal|receipt|purchase_token|notification|signed_payload|signed_transaction|pending_renewal)'
      OR (LOWER(table_name) ~ '(gps|subscription|receipt|app_store|appstore|google_play|play_store|storekit)'
          AND (data_type IN ('json', 'jsonb')
               OR LOWER(column_name) ~ '(renew|status|payload|response|metadata|event|type)'))
  )
ORDER BY table_schema, table_name, ordinal_position;
