import pandas as pd
import altair as alt
import streamlit as st
from charts import plot_generation, plot_energy_distribution, plot_demand, plot_interchange, load_data

st.set_page_config(layout="wide")

generation, demand, interchange, status = load_data()

footnote_lines = []
for table, source in status.items():
    table_name = table.replace("_", " ").capitalize()
    source_name = source.upper() if source.lower() != "csv" else "CSV"
    footnote_lines.append(f"{table_name} data loaded from {source_name}")

# Join lines with HTML line breaks
footnote_text = "<br>".join(footnote_lines)

# Display footnote at the top
st.markdown(
    f"<p style='font-size:1.2em; color:grey; margin-bottom:0.1em'>File source for the following graphs:</p>",
    unsafe_allow_html=True)
st.markdown(
    f"<p style='font-size:0.8em; color:gray; margin-bottom:0.5em'>{footnote_text}</p>",
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)


with col1:
    st.title("Electricity Generation")
    fuels = st.multiselect(
        "Choose fuel types",
        sorted(generation["fuel"].unique()),
        default=["Solar", "Petroleum", "Natural gas", "Nuclear", "Wind", "Coal"]
    )
    view_mode = st.radio("View mode", ["Absolute Generation", "Share of Total (%)"], horizontal=True)

    if fuels:
        plot_generation(generation, fuels, view_mode)

with col2:
    st.markdown("# Energy Distrubution")
    st.markdown("#### Renewable v Non-renewable")

    plot_energy_distribution(generation)


st.markdown("## Demand, Demand Forecast and Net Generation over last 30 days.")
plot_demand(demand)

st.markdown("## Cross-border Electricity Interchange")
plot_interchange(interchange)