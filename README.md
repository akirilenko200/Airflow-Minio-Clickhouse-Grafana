# Airflow-Minio-Clickhouse-Grafana

A preconfigured open-source data pipeline with an easy setup using Docker.

## Quickstart
- Run `docker compose up -d` in each of the service directories.
- Check environment variables for credentials and connection settings.

## Flow
1. Upon startup, Minio buckets and Clickhouse tables and materialized view are created.
1. (DAG)[volumes/airflow/dags/pipeline.py] is run every 5 minutes:
    - Fake transactions data is generated and uploaded to a Minio s3 bucket.
    - Data is inserted from s3 bucket into Clickhouse raw table.
    - Materiazlized view in Clickhouse populated an aggregate table on inserts.
1. Monitor the pipeline:
    - Access Airflow UI at http://localhost:8080 with `airflow/airflow`
    - Access Grafana UI at http://localhost:3000 with `admin/admin`
    - Access Minio UI at http://localhost:9001 with `minio/minio123`
