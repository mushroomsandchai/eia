from airflow.sdk import task, dag
from airflow.providers.standard.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime
import os

@dag(
    dag_id = 'seed_lookup_tables',
    description = 'This dag runs only once to populate the data warehouse with the required lookup tables to enrich our dataset.',
    start_date = datetime(2019, 1, 1),
    schedule = '@once',
    catchup = True,
    tags = ['dbt', 'seeds', 'lookup_tables']
)
def seed():
    @task.bash
    def wget():
        return('curl -Lf https://www.eia.gov/electricity/930-content/EIA930_Reference_Tables.xlsx -o /tmp/eia_930_reference_tables.xlsx')
    
    @task
    def make_tables():
        from helpers.fetch_seed_files import make_csv
        make_csv()

    @task.bash
    def seed_and_clean():
        activator = os.environ.get('DBT_VIRTUAL_ENVIRONMENT_PATH').rstrip('dbt') + 'activate'
        return(f"""source {activator} \
                    && cd {os.environ.get('DBT_PROJECT_PATH')} \
                    && dbt seed \
                    && rm -rf /tmp/eia_930_reference_tables.xlsx""")

    extract = wget()
    create = make_tables()
    seed = seed_and_clean()

    extract >> create >> seed

seed()