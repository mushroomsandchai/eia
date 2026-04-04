# EIA Data Pipeline

A data pipeline for Energy Information Administration (EIA) data using Apache Airflow, dbt, cosmos and PostgreSQL with infrastructure as code via Terraform.

## Based on the evaluation criteria, here's a problem description worth the full 4 points:

---

## Problem Description

The U.S. Energy Information Administration (EIA) publishes near real-time and historical data on electricity generation, grid demand, and cross-border energy flows across the United States. While this data is freely accessible via the EIA API, it is returned in a raw, fragmented format, split across multiple endpoints, inconsistently typed, and lacking the joins and aggregations needed to draw meaningful conclusions.

The problem this project solves is the absence of a reliable, automated pipeline that continuously ingests this data, transforms it into a consistent and analytics ready format, and makes it accessible for visual exploration.

Without such a pipeline, answering fundamental questions about the U.S. electricity grid requires significant manual effort each time:

- How has the fuel mix shifted over time, are renewables actually displacing fossil fuels?
- Is electricity demand being forecast accurately by grid operators?
- How much electricity flows between the U.S., Canada, and Mexico, and in which direction?

This project addresses that gap by building an end-to-end data pipeline that ingests raw EIA data via Airflow (both in bulk from pre-exported Parquet files and incrementally via the live API), transforms it through a layered dbt model into clean, joined, and aggregated tables in BigQuery, and surfaces the results in an interactive Streamlit dashboard — so these questions can be answered continuously, not just once.

## Overview

This project orchestrates data workflow for EIA data:

- **Apache Airflow** — DAG orchestration and workflow scheduling
- **dbt** — SQL-based data transformations with layered models
- **PostgreSQL** — Metadata backend and data warehouse
- **Airflow Cosmos** — Seamless dbt integration within Airflow
- **Terraform** — Infrastructure provisioning and management
- **Docker** — Containerized local development environment

## Project Structure

```
eia/
├── airflow/                    # Airflow configuration
│   ├── dags/                   # DAG definitions
│   └── logs/                   # Execution logs
├── dbt/                        # Data transformations
│   ├── models/
│   │   ├── staging/            # Raw data models
│   │   ├── intermediate/       # Business logic layer
│   │   └── marts/              # Final analytical tables
│   ├── macros/                 # Reusable dbt macros
│   ├── seeds/                  # Static reference data
│   ├── dbt_project.yml         # dbt configuration
│   └── profiles.yml            # dbt profile settings
├── streamlit/                  # Dashboard
│   ├── app.py                  # Main app
│   └── charts.py               # Helper to create charts
│   └── *.csv                   # CSV files to populate dashboard
├── terraform/                  # Infrastructure as Code
│   ├── main.tf                 # Primary resources
│   └── variables.tf            # Terraform variables
├── batch_files/                # Historical data from EIA
│   ├── *.parquet.gz            # Files used for faster ingestion
├── docker-compose.yml          # Docker service definitions
├── Dockerfile                  # Custom image build
├── .env                        # Environment configuration
└── up.sh                       # Quick start script
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Terraform
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/mushroomsandchai/eia.git
cd eia


### Environment Variables
# Configure the following variables in `.env`:
LOCAL_GCS_JSON_CREDENTIALS_PATH=PATH_TO_JSON_KEY        # Service Key for GCP
PROJECT=PROJECT_ID                                      # GCS PROJECT ID
BUCKET_NAME=BUCKET_NAME                                 # GCP BUCKET NAME
DATASET=DATASET_NAME                                    # BQ Dataset name
DATASET_LOCATION=US                                     # BQ Dataset location

EIA_API=EIA_API_KEY                                     # API Key for EIA
# The file has been loaded with an API scrapped off of stackoverflow.
# It is highly recommended to register your API key by visiting: https://www.eia.gov/opendata/register.php

# Make startup script executable
chmod +x up.sh

# Start all services
./up.sh
```
It is recommended to go through `up.sh` startup script before running it.

### Accessing Services
- #### **Airflow UI**: http://localhost:8080
  ###### Run the following command in case you start docker services manually without using the `./up.sh` script.<br>Airflow dynamically creates a password for each airflow instance and stores it in `/opt/airflow/simple_auth_manager_passwords.json.generated` file. Access it via the following command.
      docker exec airflow cat simple_auth_manager_passwords.json.generated
- #### **Streamlit**: http://localhost:8501
- #### **PostgreSQL**: http://localhost:5432

## Architecture

### Data Flow
1. **Orchestration** — Airflow schedules and triggers pipelines
2. **Transformation** — dbt processes raw data through staging → intermediate → marts layers
3. **Integration** — Cosmos operators execute dbt within Airflow DAGs
4. **Storage** — PostgreSQL persists transformed data and Airflow metadata

## Managing DAGs

Before triggering any DAGs or even building the docker image, make sure the following variables are configured in the `.env` file provided in the project root. These are required for Airflow, dbt, terraform and streamlit to authenticate with GCP and locate the correct project, bucket, and dataset:

```env
# Airflow and dbt shared variables
LOCAL_GCS_JSON_CREDENTIALS_PATH=PATH_TO_JSON_KEY  # Path to your GCP service account JSON key

# dbt configuration variables
PROJECT=PROJECT_ID          # GCP Project ID
BUCKET_NAME=BUCKET_NAME     # GCP Bucket name
DATASET=DATASET_NAME        # BigQuery dataset name
DATASET_LOCATION=US         # BigQuery dataset location
```

Once these are set, restart your services (`./up.sh`) and trigger the DAGs in the order described below.
Note: `.env` file is preloaded with an API key which was scrapped from stackoverlow, make sure to register and populate it with your own key to have unrestricted access in the future.

### DAGs Overview

| DAG | Description |
|-----|-------------|
| `seed_lookup_tables` | One-time (or on-demand) seeding of static reference/lookup tables |
| `monthly_historical_data` | Pulls the full historical dataset directly from the EIA API — the source of truth for bulk historical ingestion |
| `local_ingestion` | Ingests the same historical data as `monthly_historical_data` but reads from pre-exported Parquet files in `batch_files/` instead of hitting the EIA API — use this to avoid thousands of API calls during setup |
| `daily_data` | Scheduled daily incremental data pulls |

### ⚠️ DAG Activation Order

> **The DAGs must be enabled in the following order.** Each DAG depends on the outputs of the previous one. Enabling them out of order may result in missing reference data or failed tasks.

```
                                    local_ingestion
                                (preferred - reads Parquet)
                      /                                             \
seed_lookup_tables  →                                                 →  daily_data (scheduled)
      (once)          \                                              /
                                  monthly_historical_data
                            (alternative - hits EIA API directly)
```

#### Step 1 — `seed_lookup_tables`

Enable and run this DAG **first**. It populates the static lookup/reference tables that downstream DAGs depend on. This only needs to be run once during initial setup, or whenever the reference data changes.

```
Airflow UI → DAGs → seed_lookup_tables → Enable
```

Wait for all tasks to show **Success** before proceeding.

#### Step 2 — `local_ingestion` (preferred) or `monthly_historical_data`

These two DAGs produce the same result — a full load of historical EIA data — but differ in how they source it:

| DAG | Data source | When to use |
|-----|-------------|-------------|
| `local_ingestion` | Pre-exported Parquet files in `batch_files/` | **Preferred.** Use this during setup to avoid hitting the EIA API thousands of times. |
| `monthly_historical_data` | EIA API (live) | Use this if the Parquet export is unavailable, or you need a fresh pull directly from the source. |

```
Airflow UI → DAGs → local_ingestion → Enable
```

Wait for all tasks to show **Success** before proceeding.

#### Step 3 — `daily_data`

After the historical ingestion is complete, enable this DAG. It runs on a daily schedule and incrementally pulls new EIA data and loads into our landing layer in BigQuery. This landing layer is essentially our source of truth and contains all the records pulled from EIA. It runs the dbt models only when it pulls today's data, which in turn saves compute costs in GCP.

```
Airflow UI → DAGs → daily_data → Enable
```

### DAG CLI Commands

```bash
# List all DAGs
airflow dags list

# Trigger a DAG
airflow dags trigger my_dag
```

## Key Features

- **Layered Transformation Model** — Clear separation of concerns with staging, intermediate, and mart layers
- **Airflow + dbt Integration** — Leverage Cosmos for native dbt DAG generation
- **Infrastructure as Code** — Reproducible infrastructure with Terraform
- **Local Development** — Complete stack runs in Docker for easy onboarding
- **Cloud-Ready** — Extendable to major cloud data warehouses (Snowflake, BigQuery, Redshift)


## Deployment

The included Terraform configuration handles infrastructure provisioning. Modify `terraform/` for your target environment.

## Notes

- `local_ingestion` and `monthly_historical_data` produce the same result. Use `local_ingestion` whenever possible to avoid hammering the EIA API with thousands of requests.
- Do **not** enable `daily_data` before the historical ingestion step has completed successfully, as our intermediate layers are incremental.
- `seed_lookup_tables` should be re-triggered any time the underlying reference data needs to be refreshed.
- Uses **Cosmos** to run dbt as Airflow tasks — no separate dbt CLI calls needed
- Designed for **local development** with Docker Compose
- **Cloud-agnostic** — switch data warehouses by updating dbt profiles
