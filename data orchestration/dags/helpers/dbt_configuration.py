from cosmos.config import ProfileConfig, ProjectConfig, ExecutionConfig, ExecutionMode
from cosmos.profiles import GoogleCloudServiceAccountFileProfileMapping
import os

def dbt_objects():
    execution = ExecutionConfig(
        dbt_executable_path = os.environ.get("DBT_VIRTUAL_ENVIRONMENT_PATH"),
        execution_mode = ExecutionMode.WATCHER,
    )

    gcp = GoogleCloudServiceAccountFileProfileMapping(
        conn_id = "GCP_CONNECTION",
        profile_args = {
                            "project": os.environ.get("PROJECT"), 
                            "dataset": os.environ.get("DATASET"), 
                            "location": os.environ.get("DATASET_LOCATION"), 
                            "keyfile": os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
                        },
    )

    profile = ProfileConfig(
        profile_name = "default",
        target_name = "dev",
        profile_mapping = gcp,
    )

    project = ProjectConfig(
        dbt_project_path = os.environ.get("DBT_PROJECT_PATH"),
        dbt_vars={"interval": "{{ 'daily' if data_interval_start.date() == macros.datetime.utcnow().date() else 'backfill' }}"},
        manifest_path = os.environ.get("DBT_MANIFEST_PATH"),
        models_relative_path = "models",
        seeds_relative_path = "seeds",
        snapshots_relative_path = "snapshots",
    )

    return(profile, project, execution)