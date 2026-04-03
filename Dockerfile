FROM apache/airflow:3.1.6-python3.12

USER root
# Basic build essentials for dbt-bigquery and git
RUN apt-get update && apt-get install -y --no-install-recommends \
    git gcc python3-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

USER airflow

# Install Cosmos into the main Airflow 3.1.6 env
# We use --upgrade to ensure it handles the new Airflow provider structures
RUN pip install --no-cache-dir --upgrade astronomer-cosmos openpyxl streamlit altair

# Create the lightweight dbt-bigquery bubble
RUN python -m venv /opt/airflow/.dbt_venv && \
    /opt/airflow/.dbt_venv/bin/pip install --no-cache-dir \
    dbt-core \
    dbt-bigquery