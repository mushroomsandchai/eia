from datetime import datetime, timedelta
from airflow.sdk import task, dag, get_current_context

default_args = {
    'retries': 10,
    'retry_delay': timedelta(minutes = 1)
}

@dag(
    dag_id = 'monthly_historical_data',
    description = """Fetch hourly electricity generation, interchange between balancing authorities,\
                        demand forecast and demand by subregion data by month from EIA API and store in GCP bucket.""",
    schedule = "@monthly",
    start_date = datetime(2019, 1, 1),
    end_date = datetime(2026, 2, 28),
    catchup = True,
    max_active_runs = 4,
    default_args = default_args,
    tags = ['project', 'datalake', 'raw', 'generation', 'demand forecast', 'demand by subregion', 'interchange', 'monthly', 'historical']
)
def main():
    @task
    def get_endpoints():
        from helpers.fetch_endpoints import points
        
        logical_date = get_current_context()['logical_date']
        endpoints = points(logical_date, type = 'monthly')

        return(endpoints)


    @task
    def ingest(endpoint: dict):
        from helpers.api_call import api_call
        from helpers.load import upload_blob

        buffer = api_call(endpoint)
        gcp_file_path = f"{endpoint['directory'].rstrip('/')}.parquet"

        upload_blob(buffer, gcp_file_path)

    @task
    def load(endpoint: dict):
        from helpers.load import load_table
        load_table(type = endpoint['type'], interval = 'batch_load')


    endpoints = get_endpoints()
    ingestion = ingest.expand(endpoint = endpoints)
    loader = load.expand(endpoint = endpoints)

    ingestion >> loader

main()
