from datetime import datetime, timedelta
from airflow.sdk import task, dag, get_current_context
from airflow.operators.empty import EmptyOperator

default_args = {
    'retries': 2,
    'retry_delay': timedelta(minutes = 1)
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
            endpoints = points(logical_date, type = 'refresh')
        else:
            endpoints = points(logical_date)
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
    def load_tables(endpoint):
        from helpers.load import load_table
        import os
        
        uri = f"{endpoint['directory']}{endpoint['dtobject'].day:02d}.parquet"
        load_table(endpoint['type'], uri, interval = 'daily')


    @task.branch
    def decide_branch():
        from datetime import datetime
        context = get_current_context()
        logical_date = context['logical_date'].date()

        if logical_date == datetime.now().date():
            return "run_dbt"
        else:
            return "skip_dbt"

    from cosmos import DbtTaskGroup
    from cosmos.config import RenderConfig
    from helpers.dbt_configuration import dbt_objects

    PROFILE, PROJECT, EXECUTION = dbt_objects()

    dbt_merge = DbtTaskGroup(
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

    endpoints = get_endpoints()
    ingestion = ingest.expand(endpoint = endpoints)    
    loader = load_tables.expand(endpoint = endpoints)


    run_dbt = EmptyOperator(task_id="run_dbt")
    skip_dbt = EmptyOperator(task_id="skip_dbt")

    branch = decide_branch()

    ingestion >> loader >> branch
    branch >> run_dbt >> dbt_merge
    branch >> skip_dbt

main()