CREATE MATERIALIZED VIEW mv_daily_summary TO daily_summary
AS SELECT
toStartOfDay(timestamp) AS day,
transaction_type,
currency,
sumState(amount) AS total,
countState() AS count
FROM transactions_raw
GROUP BY day, transaction_type, currency;