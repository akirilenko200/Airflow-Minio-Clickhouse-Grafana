CREATE TABLE transactions_raw (
	transaction_id UUID,
	timestamp DateTime,
	bank_country LowCardinality(String),
	account_number String,
	transaction_type LowCardinality(String),
	amount Decimal64(2),
	currency  LowCardinality(String),
	recipient_account String,
	sender_name String,
	description String
) ENGINE = MergeTree
ORDER BY (transaction_type, currency, timestamp)
PARTITION BY toYYYYMM(timestamp);

CREATE TABLE daily_summary (
	day DateTime,
	transaction_type LowCardinality(String),
	currency  LowCardinality(String),
	total AggregateFunction(sum, Decimal64(2)),
	count AggregateFunction(count, UInt64)
) ENGINE = AggregatingMergeTree()
ORDER BY (day, transaction_type, currency);