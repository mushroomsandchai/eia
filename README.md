# EIA Data Pipeline

A modern data pipeline for Energy Information Administration (EIA) data using Apache Airflow, dbt, and PostgreSQL with infrastructure as code via Terraform.

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
├── terraform/                  # Infrastructure as Code
│   ├── main.tf                 # Primary resources
│   └── variables.tf            # Terraform variables
├── docker-compose.yml          # Docker service definitions
├── Dockerfile                  # Custom image build
├── .env                        # Environment configuration
└── up.sh                       # Quick start script
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/mushroomsandchai/eia.git
cd eia


### Environment Variables
# Configure `.env` for:
# - Database credentials
# - Airflow settings
# - EIA API keys
# - Cloud provider credentials

# Configure terraform/variables.tf for:
# - GCP Bucket
# - GCP Dataset
# - GCP Project-ID

# Build Docker images
docker compose build

# Make startup script executable
chmod +x up.sh

# Start all services
./up.sh
```

### Accessing Services
- #### **Airflow UI**: http://localhost:8080
      docker exec airflow cat simple_auth_manager_passwords.json.generated
- #### **PostgreSQL**: localhost:5432

## Architecture

### Data Flow
1. **Orchestration** — Airflow schedules and triggers pipelines
2. **Transformation** — dbt processes raw data through staging → intermediate → marts layers
3. **Integration** — Cosmos operators execute dbt within Airflow DAGs
4. **Storage** — PostgreSQL persists transformed data and Airflow metadata


## Key Features

- **Layered Transformation Model** — Clear separation of concerns with staging, intermediate, and mart layers
- **Airflow + dbt Integration** — Leverage Cosmos for native dbt DAG generation
- **Infrastructure as Code** — Reproducible infrastructure with Terraform
- **Local Development** — Complete stack runs in Docker for easy onboarding
- **Cloud-Ready** — Extendable to major cloud data warehouses (Snowflake, BigQuery, Redshift)


## Development

### Running dbt Locally
```bash
cd dbt
dbt debug           # Verify connections
dbt run             # Execute all models
dbt test            # Run data quality tests
dbt docs generate   # Build documentation
```

### Managing DAGs
```bash
# List all DAGs
airflow dags list

# Trigger a DAG
airflow dags trigger my_dag
```

## Deployment

The included Terraform configuration handles infrastructure provisioning. Modify `terraform/` for your target environment.

## Notes

- Uses **Cosmos** to run dbt as Airflow tasks — no separate dbt CLI calls needed
- Designed for **local development** with Docker Compose
- **Cloud-agnostic** — switch data warehouses by updating dbt profiles
- PostgreSQL backend suitable for dev/test; consider managed databases for production