from datetime import datetime, timedelta
from airflow.sdk import task, dag, get_current_context
from airflow.exceptions import AirflowSkipException

default_args = {
    'retries': 2,
    'retry_delay': timedelta(minutes = 0)
}

@dag(
    dag_id = 'daily_data',
    description = """Fetch hourly electricity generation, interchange between balancing authorities,\
                        demand forecast and demand by subregion data by day from EIA API and store in GCP bucket.""",
    schedule = "@daily",
    start_date = datetime(2026, 3, 1),
    catchup = True,
    max_active_runs = 1,
    default_args = default_args,
    tags = ['project', 'datalake', 'raw', 'generation', 'demand forecast', 'demand by subregion', 'interchange']
)
def main():

    @task
    def get_endpoints():
        from helpers.fetch_endpoints import points
        import os
        logical_date = get_current_context()['logical_date']
        lag_days = int(os.environ.get('LAG_DAYS', 3))
        run_date = logical_date - timedelta(days = lag_days)

        start_date = run_date.strftime('%Y-%m-%dT00')
        end_date = run_date.strftime('%Y-%m-%dT23')

        endpoints = points(start_date, end_date, run_date)
        return(endpoints)


    @task
    def ingest(endpoint: dict):
        from helpers.api_call import api_call
        from helpers.load import upload_blob, load_table

        buffer = api_call(endpoint)
        gcp_file_path = f"{endpoint['directory']}{endpoint['dtobject'].day:02d}.parquet"

        upload_blob(buffer, gcp_file_path)
        load_table(type = endpoint['type'], buffer = buffer, interval = 'daily')


    from cosmos import DbtTaskGroup
    from cosmos.config import RenderConfig
    from helpers.dbt_configuration import dbt_objects

    PROFILE, PROJECT, EXECUTION = dbt_objects()

    dbt_merge = DbtTaskGroup(
        profile_config = PROFILE,
        project_config = PROJECT,
        execution_config = EXECUTION,
        render_config = RenderConfig(
            select = ["path:models/staging+"] 
        ),
    )


    endpoints = get_endpoints()
    ingestion = ingest.expand(endpoint = endpoints)


    ingestion >> dbt_merge

main()