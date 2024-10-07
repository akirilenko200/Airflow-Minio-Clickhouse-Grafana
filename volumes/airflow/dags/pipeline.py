import logging
import pendulum
from faker import Faker
import random
import pandas as pd
from datetime import datetime
from airflow.models import Variable
from airflow.decorators import dag, task
from clickhouse_driver import Client

logger = logging.getLogger("airflow.task")

NUMBER_OF_SAMPLES = 50000
MINIO_BUCKET = 'raw'

@dag(
        schedule='*/5 * * * *',
        start_date=pendulum.datetime(2024,10,1, tz="UTC"),
        catchup=False,
        is_paused_upon_creation=False
)
def pipeline_dag():
    """
    DAG to generate fake transactions data, upload them to s3, and then insert into CH
    Variables are defined in .env
    """
    minio_host = Variable.get('minio_host')
    minio_access_key = Variable.get('minio_access_key')
    minio_secret_key = Variable.get('minio_secret_key')

    ch_user = Variable.get('ch_user')
    ch_password = Variable.get('ch_password')
    ch_host = Variable.get('ch_host')
    ch_port = Variable.get('ch_port')
    ch_scheme = Variable.get('ch_schema')

    @task()
    def load_to_s3(*, ts_nodash):
        fake = Faker()
        def generate_transaction():
            return {
                "transaction_id": fake.uuid4(),
                "timestamp": fake.date_time_between_dates(datetime_start=datetime(2020,1,1)),
                "bank_country": random.choice(["CHE", "USA", "GBR", "NZD", "CAN", "AUS", "DEU", "AUS", "NZL", "AUT", "FRA", "NLD"]),
                "account_number": fake.bban(),  
                "transaction_type": random.choice(["deposit", "withdrawal", "transfer"]),
                "amount": round(random.lognormvariate(10, 0.7), 2), 
                "currency": random.choice(["AUS", "USD", "EUR","USD", "EUR","USD", "EUR","USD", "EUR","CAD", "CHF", "CHF", "GBP", "GBP", "NZD", "GBP"]),
                "recipient_account": fake.bban(),
                "sender_name": fake.name(),
                "description": fake.sentence(nb_words=5),
            }
        df = pd.DataFrame([generate_transaction() for _ in range(NUMBER_OF_SAMPLES)])

        file_name = f"{ts_nodash}.csv.gz"
        s3_file_path = f"s3://{MINIO_BUCKET}/transactions/{file_name}"
        df.to_csv(
            s3_file_path,
            index=False,
            storage_options={
                "key": minio_access_key,
                "secret": minio_secret_key,
                "endpoint_url": minio_host
            }
        )
        return file_name

    @task()
    def s3_to_clickhouse(file_name):
        ch_client = Client(host=ch_host, port=ch_port, database=ch_scheme, user=ch_user, password=ch_password)

        query = f"""
            INSERT INTO transactions_raw settings date_time_input_format='best_effort', max_partitions_per_insert_block=50000
            SELECT * FROM 
            s3('{minio_host}/raw/transactions/{file_name}',
                '{minio_access_key}',
                '{minio_secret_key}',
                'CSVWithNames'
                )
            """
        
        ch_client.execute(query)


    s3_to_clickhouse(load_to_s3())

pipeline_dag()