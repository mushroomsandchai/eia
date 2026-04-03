import os
import uuid
import pandas as pd
import altair as alt
import streamlit as st
from google.cloud import bigquery

# cache for 1 hour
@st.cache_data(ttl=3600)
def fetch_table(table_name, csv_path, project, dataset):
    """
    Try to fetch table from BigQuery, fallback to CSV if it fails.
    Returns: (dataframe, source)
    """
    client = bigquery.Client()
    job_id = f"streamlit_query_{uuid.uuid4().hex}"  # unique per call

    try:
        query_job = client.query(
            f"SELECT * FROM `{project}.{dataset}.{table_name}`",
            job_id=job_id
        )
        df = query_job.result().to_dataframe()

        if "total_generation" in df.columns:
            df["total_generation"] = pd.to_numeric(df["total_generation"], errors="coerce")
        if "year" in df.columns:
            df["year"] = pd.to_numeric(df["year"], errors="coerce")
        if "energy_type" in df.columns:
            df["energy_type"] = df["energy_type"].fillna("Unknown").astype(str)
        if "fuel" in df.columns:
            df["fuel"] = df["fuel"].astype(str)
        if "recorded_date" in df.columns:
            df["recorded_date"] = pd.to_datetime(df["recorded_date"].astype(str).str.replace(".", "", regex=False))
        if "interchange" in df.columns:
            df["interchange"] = pd.to_numeric(df["interchange"], errors="coerce")

        return df, "BigQuery"
    except Exception:
        df = pd.read_csv(csv_path)
        return df, "CSV"


def load_data():
    project = os.environ.get("PROJECT")
    dataset = os.environ.get("DATASET")
    
    tables = {
        "generation": "/opt/airflow/streamlit/generation.csv",
        "forecast": "/opt/airflow/streamlit/forecast.csv",
        "interchange": "/opt/airflow/streamlit/interchange.csv"
    }
    
    data = {}
    status = {}
    
    for key, path in tables.items():
        df, source = fetch_table(f"marts_{key}", path, project, dataset)
        data[key] = df
        status[key] = source
    
    return data["generation"], data["forecast"], data["interchange"], status

def plot_generation(generation, fuels, view_mode):
    data = generation[generation["fuel"].isin(fuels)].copy()

    # Normalize if needed
    if view_mode == "Share of Total (%)":
        total_per_year = data.groupby("year")["total_generation"].transform("sum")
        data["value"] = (data["total_generation"] / total_per_year) * 100
        y_title = "Share (%)"
    else:
        data["value"] = data["total_generation"] / 1_000_000
        y_title = "Generation (Millions)"

    data = data.rename(columns={"fuel": "Fuel", "year": "Year"})

    color_scale = alt.Scale(
        domain=[
            "Coal", "Natural gas", "Petroleum", "Nuclear", "Wind", "Solar",
            "Hydro and pumped storage", "Geothermal", "Battery storage",
            "Wind with integrated battery storage", "Solar with integrated battery storage",
            "Pumped storage", "Other energy storage", "Unknown energy storage",
            "Other", "All energy sources"
        ],
        range=[
            "#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F", "#EDC948",
            "#B07AA1", "#FF9DA7", "#9D7660", "#86BCB6", "#F1CE63", "#BAB0AC",
            "#D7B5A6", "#CFCFCF", "#8CD17D", "#000000"
        ]
    )

    chart = (
        alt.Chart(data)
        .mark_area(opacity=0.85)
        .encode(
            x=alt.X("Year:O", title="Year"),
            y=alt.Y("value:Q", title=y_title, stack="normalize" if view_mode == "Share of Total (%)" else "zero"),
            color=alt.Color("Fuel:N", scale=color_scale, legend=alt.Legend(title="Fuel Type")),
            tooltip=[
                alt.Tooltip("Year"),
                alt.Tooltip("Fuel:N"),
                alt.Tooltip("value:Q", format=".2f")
            ],
        )
        .properties(height=420)
    )
    st.altair_chart(chart, use_container_width=True)

def plot_energy_distribution(generation):
    energy_mix = generation.groupby(["year", "energy_type"])["total_generation"].sum().reset_index()

    color_scale_category = alt.Scale(
        domain=["renewable", "non-renewable"],
        range=["#59A14F", "#F28E2B"]
    )

    chart = (
        alt.Chart(energy_mix)
        .mark_area(opacity=0.8)
        .encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("total_generation:Q", title="Net Generation", stack="normalize"),
            color=alt.Color("energy_type:N", scale=color_scale_category, legend=alt.Legend(title="Energy Type")),
            tooltip=[
                alt.Tooltip("year:O", title="Year"),
                alt.Tooltip("energy_type:N", title="Source"),
                alt.Tooltip("total_generation:Q", title="Generation", format=",")
            ]
        )
    )
    st.altair_chart(chart, use_container_width=True)

    with st.expander("View data table", expanded=False):
        st.dataframe(energy_mix.sort_values(["year", "energy_type"]).reset_index(drop=True), use_container_width=True)

def plot_demand(demand):
    demand["recorded_date"] = pd.to_datetime(demand["recorded_date"].astype(str).str.replace(".", "", regex=False))
    demand["datetime"] = demand["recorded_date"] + pd.to_timedelta(demand["recorded_hour"], unit="h")

    color_scale = alt.Scale(
        domain=["Actual Demand", "Demand Forecast", "Net Generation"],
        range=["#4E79A7", "#F28E2B", "#59A14F"]
    )

    chart = (
        alt.Chart(demand)
        .mark_line()
        .encode(
            x=alt.X("datetime:T", title="Time"),
            y=alt.Y("value:Q", title="MW"),
            color=alt.Color("demand_type:N", scale=color_scale, legend=alt.Legend(title="Series")),
            tooltip=[
                alt.Tooltip("datetime:T", title="Time"),
                alt.Tooltip("demand_type:N", title="Type"),
                alt.Tooltip("value:Q", title="Value", format=",.0f")
            ]
        )
        .properties(height=400)
    )

    st.altair_chart(chart, use_container_width=True)

def plot_interchange(interchange):
    interchange['provider_country'] = interchange['provider_country'].replace('United States of America', 'USA')
    interchange['recipient_country'] = interchange['recipient_country'].replace('United States of America', 'USA')
    interchange["recorded_date"] = pd.to_datetime(interchange["recorded_date"])
    interchange["interchange"] = pd.to_numeric(interchange["interchange"], errors="coerce")

    color_scale = alt.Scale(
        domain=["Canada", "Mexico"],
        range=["#F65F5F", "#006847"]  # red for Canada, green for Mexico
    )

    interchange["flow"] = (
        interchange["provider_country"] + " → " + interchange["recipient_country"]
    )
    
    flows = st.multiselect(
        "Select flows",
        sorted(interchange["provider_country"].unique() + " → " + interchange["recipient_country"].unique()),
        default=interchange["provider_country"].unique()[:2] + " → " + interchange["recipient_country"].unique()[:2]
    )

    interchange = interchange[interchange["flow"].isin(flows)]

    chart = (
        alt.Chart(interchange)
        .mark_line(strokeWidth=2)
        .encode(
            x=alt.X("recorded_date:T", title="Year", axis=alt.Axis(format="%Y")),
            y=alt.Y("interchange:Q", title="Interchange (MW)"),
            color=alt.Color("recipient_country:N", scale=color_scale, legend=alt.Legend(title="Country")),
            tooltip=[
                alt.Tooltip("recorded_date:T", title="Date"),
                alt.Tooltip("provider_country:N", title="Provider"),
                alt.Tooltip("recipient_country:N", title="Recipient"),
                alt.Tooltip("interchange:Q", title="MW", format=",.0f")
            ]
        )
        .properties(height=400)
    )

    st.altair_chart(chart, use_container_width=True)

def generation_query(project, dataset, table):
    return(f"select * from `{project}.{dataset}.{table};")