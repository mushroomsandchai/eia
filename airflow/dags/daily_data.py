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
        logical_date = get_current_context()['logical_date']

        if logical_date.date() == datetime.now().date():
            import os
            window_days = int(os.environ.get('WINDOW_DAYS', 7))

            end_date_dt = logical_date - timedelta(days=1)

            all_endpoints = []

            for i in range(window_days):
                run_date = end_date_dt - timedelta(days=i)

                start_date = run_date.strftime('%Y-%m-%dT00')
                end_date = run_date.strftime('%Y-%m-%dT23')

                daily_endpoints = points(start_date, end_date, run_date)
                all_endpoints.extend(daily_endpoints)

            start_date = logical_date.strftime('%Y-%m-%dT00')
            end_date = logical_date.strftime('%Y-%m-%dT23')
            forecast = points(start_date, end_date, logical_date)
            for point in forecast:
                if point['type'] == 'demand_forecast':
                    all_endpoints.append(point)
                    
            return all_endpoints
        else:
            run_date = logical_date - timedelta(days = 1)
            start_date = run_date.strftime('%Y-%m-%dT00')
            end_date = run_date.strftime('%Y-%m-%dT23')
            endpoints = points(start_date, end_date, logical_date)
            return(endpoints)


    @task
    def ingest(endpoint: dict):
        from helpers.api_call import api_call
        from helpers.load import upload_blob

        buffer = api_call(endpoint)

        if buffer:
            gcp_file_path = f"{endpoint['directory']}{endpoint['dtobject'].day:02d}.parquet"

            upload_blob(buffer, gcp_file_path)
    

    @task
    def load_tables():
        from helpers.load import load_table
        import os

        logical_date = get_current_context()['logical_date']
        types = ['generation', 'demand_forecast', 'demand_by_subregion', 'interchange']
        
        if logical_date.date() == datetime.now().date():
            start_date = logical_date - timedelta(days = int(os.environ.get('WINDOW_DAYS', 7)))
            end_date = logical_date - timedelta(days = 1)
        else:
            start_date, end_date = logical_date, logical_date
        for type in types:
            load_table(type, start_date, end_date, interval = 'daily')


    from cosmos import DbtTaskGroup
    from cosmos.config import RenderConfig
    from helpers.dbt_configuration import dbt_objects

    PROFILE, PROJECT, EXECUTION = dbt_objects()

    dbt_merge = DbtTaskGroup(
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
    loader = load_tables()

    ingestion >> loader >> dbt_merge

main()