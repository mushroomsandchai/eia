from airflow.sdk import task, dag
from datetime import datetime

@dag(
    dag_id = 'local_ingestion',
    start_date = datetime(2019, 1, 1),
    schedule = '@once',
    catchup = True
)
def main():
    @task.bash
    def unzip():
        return("gzip -d /tmp/historical_data/*")
    
    @task
    def bucket():
        from google.cloud import storage
        import os

        bucket_name = os.environ.get('BUCKET_NAME')
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        
        for file in os.listdir('/tmp/historical_data/'):
            blob = bucket.blob(f'batch/{file}')
            blob.upload_from_filename(f'/tmp/historical_data/{file}')

    @task
    def table():
        from google.cloud import bigquery, storage
        import os
        
        project = os.environ.get('PROJECT')
        dataset = os.environ.get('DATASET')
        bucket = os.environ.get('BUCKET_NAME')
        tables = ['generation', 'interchange', 'demand_forecast', 'demand_by_subregion']

        client = bigquery.Client()
        storage_client = storage.Client()
        gcpbucket = storage_client.bucket(bucket)


        for table in tables:
            table_id = f'{project}.{dataset}.landing_{table}'

            if table == 'generation':
                cluster = ['respondent', 'fueltype']
            elif table == 'interchange':
                cluster = ['fromba', 'toba']
            elif table == 'demand_forecast':
                cluster = ['respondent', 'type']
            elif table == 'demand_by_subregion':
                cluster = ['parent', 'subba']

            job_config = bigquery.LoadJobConfig(
                                source_format = bigquery.SourceFormat.PARQUET,
                                time_partitioning = bigquery.TimePartitioning(
                                    type_ = bigquery.TimePartitioningType.DAY,
                                    field = 'partition_date',
                                    expiration_ms = None,
                                ),
                                clustering_fields = cluster,
                                write_disposition = bigquery.WriteDisposition.WRITE_APPEND,
                            )
            
            source_uri = f'gs://{bucket}/batch/{table}.parquet'

            blob = gcpbucket.blob(source_uri)

            if blob:
                load_job = client.load_table_from_uri(
                    source_uris = source_uri,
                    destination = table_id,
                    job_config = job_config
                )
            else:
                raise FileNotFoundError("File not found.")
            
            load_job.result()
            
    @task.bash
    def gzip():
        return("gzip /tmp/historical_data/*")
    
    from cosmos import DbtTaskGroup
    from cosmos.config import RenderConfig
    from helpers.dbt_configuration import dbt_objects

    PROFILE, PROJECT, EXECUTION = dbt_objects()

    dbt_models = DbtTaskGroup(
        profile_config = PROFILE,
        project_config = PROJECT,
        execution_config = EXECUTION,
        render_config = RenderConfig(
            select = ["path:models/+"]
        ),
        operator_args={
            "vars": {
                "run_date": "{{ ds }}"
            }
        }
    )

    unzipper = unzip()
    loader = bucket()
    ingest = table()
    zipper = gzip()

    unzipper >> loader >> ingest >> dbt_models >> zipper

main()