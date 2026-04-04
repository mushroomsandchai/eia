# Streamlit Dashboard

An interactive dashboard for visualising U.S. electricity generation, demand, and cross-border interchange data. It pulls from BigQuery mart tables produced by the dbt pipeline, with a CSV fallback in offline use.

## File Structure

```
streamlit/
├── app.py              # Streamlit app
├── charts.py           # chart rendering functions
├── generation.csv      # CSV fallback for generation data
├── forecast.csv        # CSV fallback for forecast/demand data
└── interchange.csv     # CSV fallback for interchange data
```

## Dashboard Sections

### 1. Electricity Generation
A stacked area chart showing annual electricity generation by fuel type (Coal, Natural gas, Nuclear, Wind, Solar, etc.).

- **Fuel filter** — multiselect to include/exclude specific fuel types
- **View mode** — toggle between absolute generation (millions of units) and share of total (%)

### 2. Energy Distribution — Renewable vs Non-Renewable
A normalised stacked area chart comparing the share of renewable vs non-renewable generation over time. Includes an expandable data table below the chart.

### 3. Demand, Forecast & Net Generation
A line chart plotting three series over the last 30 days:
- **Actual Demand**
- **Demand Forecast**
- **Net Generation**

### 4. Cross-border Electricity Interchange
A line chart showing electricity interchange (MW) between the U.S., Canada, and Mexico over time.

## Data Loading

Data is loaded via `load_data()` in `charts.py`. For each of the three mart tables (`marts_generation`, `marts_forecast`, `marts_interchange`), it:

1. Attempts to query BigQuery using the `PROJECT` and `DATASET` environment variables
2. Falls back to the corresponding CSV file if BigQuery is unavailable

The data source for each table is displayed at the top of the dashboard so it is always clear whether live or fallback data is being shown. Results are cached for **1 hour** via `@st.cache_data`.

## Environment Variables

The following variables must be set for BigQuery connectivity (same as the root `.env`):

```env
PROJECT=PROJECT_ID      # GCP Project ID
DATASET=DATASET_NAME    # BigQuery dataset containing the mart tables
```

If these are not set or BigQuery is unreachable, the app will silently fall back to the CSV files.

## Running Locally

The dashboard runs as part of the Docker Compose stack. It is served from within the Airflow container and expects the CSV fallback files to be available at `/opt/airflow/streamlit/`.

To run standalone outside Docker:

```bash
pip install streamlit google-cloud-bigquery pandas altair
streamlit run app.py
```

> Ensure `PROJECT` and `DATASET` are exported in your shell, or the app will fall back to CSV data.