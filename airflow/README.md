# Airflow DAGs

This directory contains the Apache Airflow DAGs for the EIA data pipeline. The pipeline ingests data from the U.S. Energy Information Administration (EIA), populates lookup/reference tables, and runs scheduled daily data pulls.

---

## DAGs Overview

| DAG | Description |
|-----|-------------|
| `seed_lookup_tables` | One-time (or on-demand) seeding of static reference/lookup tables |
| `monthly_historical_data` | Pulls the full historical dataset directly from the EIA API — the source of truth for bulk historical ingestion |
| `local_ingestion` | Ingests the same historical data as `monthly_historical_data` but reads from a pre-exported Parquet file instead of hitting the EIA API — use this to avoid thousands of API calls during setup |
| `daily_data` | Scheduled daily incremental data pulls |

---

## ⚠️ DAG Activation Order

> **The DAGs must be enabled in the following order.** Each DAG depends on the outputs of the previous one. Enabling them out of order may result in missing reference data or failed tasks.

### Step 1 — `seed_lookup_tables`

Enable and run this DAG **first**. It populates the static lookup/reference tables that downstream DAGs depend on. This only needs to be run once during initial setup, or whenever the reference data changes.

```
Airflow UI → DAGs → seed_lookup_tables → Enable → Trigger DAG
```

Wait for all tasks to show **Success** before proceeding.

---

### Step 2 — `local_ingestion` (preferred) or `monthly_historical_data`

These two DAGs are functionally equivalent — they load the same historical EIA dataset — but differ in their data source:

| DAG | Data source | When to use |
|-----|-------------|-------------|
| `local_ingestion` | Pre-exported Parquet file | **Preferred.** Use this during setup to avoid hitting the EIA API thousands of times. |
| `monthly_historical_data` | EIA API (live) | Use this if the Parquet export is unavailable, or you need a fresh pull directly from the source. |

In most cases, run `local_ingestion`:

```
Airflow UI → DAGs → local_ingestion → Enable → Trigger DAG
```

Wait for all tasks to show **Success** before proceeding.

---

### Step 3 — `daily_data`

After the historical ingestion is complete, enable this DAG. It runs on a daily schedule and incrementally pulls new EIA data.

```
Airflow UI → DAGs → daily_data → Enable
```

This DAG will then run automatically on its configured schedule.

---

## Summary

```
                          local_ingestion        ← preferred (reads Parquet)
                        /                  \
seed_lookup_tables  →                       →  daily_data (scheduled)
      (once)          \                  /
                        monthly_           ← alternative (hits EIA API directly)
                        historical_data
```

---

## Notes

- `local_ingestion` and `monthly_historical_data` produce the same result. Use `local_ingestion` whenever possible to avoid hammering the EIA API with thousands of requests.
- Do **not** enable `daily_data` before the historical ingestion step has completed successfully, as it relies on the data state established by that run.
- `seed_lookup_tables` should be re-triggered any time the underlying reference data needs to be refreshed.
- All DAGs should be monitored via the Airflow UI for task failures, especially during the initial setup sequence.