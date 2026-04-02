from datetime import datetime, timedelta
from airflow.sdk import task, dag, get_current_context

default_args = {
    'retries': 10,
    'retry_delay': timedelta(minutes = 1)
}

@dag(
    dag_id = 'monthly_historical_data',
    description = """Fetch hourly electricity generation, interchange between balancing authorities,\
                        demand forecast and demand by subregion data by month from EIA API and store in GCP bucket.\
                        This dag does not load it to the data warehouse to be efficient with data warehouse's compute usage.\
                        Once the end date i.e last day of Feb 28th of 2026 is met, it'll unpause the load_historical_data dag,\
                        which loads our datalake data to the data warehouse. If we were to load the historical data by month,\
                        we would inccur upwards of 10GB of byte usage from data warehouse.\
                        This way, all the data gets loaded at once and is ready for daily consumption of API values.""",
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
        from calendar import monthrange

        logical_date = get_current_context()['logical_date']
        
        start_date = logical_date.strftime('%Y-%m-%dT00')

        end_day = monthrange(logical_date.year, logical_date.month)[1]
        end_date = datetime(logical_date.year, logical_date.month, end_day)
        end_date = end_date.strftime('%Y-%m-%dT23')

        print(start_date)
        print(end_date)

        endpoints = points(start_date, end_date, logical_date)
        return(endpoints)


    @task
    def ingest(endpoint: dict):
        from helpers.api_call import api_call
        from helpers.load import upload_blob

        buffer = api_call(endpoint)
        gcp_file_path = f"{endpoint['directory'].rstrip('/')}.parquet"

        upload_blob(buffer, gcp_file_path)

    @task.short_circuit
    def should_load_tables():
        # Loads tables to big query if the total number of parquet files in the bucket is equal to 4 parquet files per month
        # from start date to end date
        context = get_current_context()
        start_date = context['dag'].start_date.date()
        end_date = context['dag'].end_date.date()
        num_months = ((end_date.year - start_date.year) * 12) + ((end_date.month - start_date.month) + 1)
        file_needed = num_months * 4

        from helpers.file_count import count
        count = count()

        return file_needed == count

    @task
    def load(endpoint: dict):
        from helpers.load import load_table
        load_table(type = endpoint['type'], interval = 'batch_load')


    from cosmos import DbtTaskGroup
    from cosmos.config import RenderConfig
    from helpers.dbt_configuration import dbt_objects

    PROFILE, PROJECT, EXECUTION = dbt_objects()

    dbt_models = DbtTaskGroup(
        profile_config = PROFILE,
        project_config = PROJECT,
        execution_config = EXECUTION,
        render_config = RenderConfig(
            select = ["path:models/staging+", "path:models/intermediate+"] 
        ),
        operator_args={
            "vars": {
                "run_date": "{{ ds }}"
            }
        }
    )

    endpoints = get_endpoints()
    ingestion = ingest.expand(endpoint = endpoints)
    loader = load.expand(endpoint = endpoints)
    should_load = should_load_tables()

    ingestion >> should_load >> loader >> dbt_models

main()