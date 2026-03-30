# EIA Data Pipeline

## Overview

This project builds a data pipeline for Energy Information Administration (EIA) data using:

* Apache Airflow (orchestration)
* dbt (transformations)
* PostgreSQL (metadata backend)
* Cosmos (Airflow + dbt integration)
* Terraform (infrastructure)



## Project Structure

```
├── airflow/               # Airflow
│   ├── dags/              
│   ├── logs/              
├── dbt/                   # dbt
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   ├── macros/
│   ├── seeds/
│   └── dbt_project.yml
│   └── profiles.yml
├── terraform/.            # Terraform
│   └── main.tf
│   └── variables.tf   
├── docker-compose.yml     # Docker services
├── Dockerfile             # Dockerfile
└── .env            
└── up.sh                  # Start Docker services
```



## Setup

```
git clone https://github.com/mushroomsandchai/eia.git
cd eia
docker compose build
chmod +x up.sh
./up.sh
```


## Notes

* Uses Cosmos to run dbt inside Airflow
* Designed for local development with Docker
* Extendable to cloud warehouses