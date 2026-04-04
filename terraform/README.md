# Terraform

Provisions the GCP infrastructure required by the EIA data pipeline — a GCS bucket (data lake) and a BigQuery dataset (data warehouse).

## File Structure

```
terraform/
├── main.tf         # configuration and resource definitions
└── variables.tf    # variable declarations
```

## Resources Provisioned

| Resource | Type | Description |
|----------|------|-------------|
| `google_storage_bucket.no-age-enabled` | GCS Bucket | Data lake for intermediate storage. Blobs are automatically deleted after **3 days**. |
| `google_bigquery_dataset.dataset` | BigQuery Dataset | Data warehouse where dbt mart tables are written and queried by the Streamlit dashboard. |

> ⚠️ Both resources are configured with `force_destroy` / `delete_contents_on_destroy = true` — destroying the Terraform stack will permanently delete all data inside them.

## Variables

All four variables are required. Set them before running any Terraform commands.

| Variable | Description |
|----------|-------------|
| `project_id` | GCP Project ID |
| `project_location` | GCP region/location (e.g. `US`, `europe-west2`) |
| `bucket_name` | Name for the GCS data lake bucket |
| `dataset_name` | Name for the BigQuery dataset |

Variables can be provided in a `terraform.tfvars` file (recommended) or passed via the CLI:

```hcl
# terraform.tfvars
project_id       = "your-gcp-project-id"
project_location = "US"
bucket_name      = "your-bucket-name"
dataset_name     = "your-dataset-name"
```

## Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/install) installed
- GCP credentials configured — either via `gcloud auth application-default login` or a service account key exported as `GOOGLE_APPLICATION_CREDENTIALS`
- The target GCP project must exist and have the **Cloud Storage** and **BigQuery** APIs enabled

## Usage

```bash
cd terraform

# Initialise providers
terraform init

# Preview changes
terraform plan

# Apply infrastructure
terraform apply

# Tear down all resources (destructive — deletes all data)
terraform destroy
```

## Notes

- The GCS bucket has a lifecycle rule that deletes objects older than 3 days, keeping the data lake lean and avoiding unnecessary storage costs.
- The BigQuery dataset location should match `DATASET_LOCATION` in your root `.env` to avoid cross-region query charges.