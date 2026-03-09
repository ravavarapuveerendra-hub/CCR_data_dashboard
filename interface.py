import streamlit as st
import pandas as pd
import plotly.express as px

st.image("CCRLogo.png", width=200)
st.title("CCR GmbH : RF Plasma Source Comparison Dashboard")

# Read Excel file
data = pd.read_excel("plasma_sources.xlsx")
data.columns = data.columns.str.strip().str.lower()

# Sidebar filters
st.sidebar.header("Filters")

# Filter 1: Source Type
source_types = data["source_type"].unique()
selected_type = st.sidebar.selectbox("Select Plasma Source Type", source_types)

# Filter 2: Design (dependent on Type)
designs = data[data["source_type"] == selected_type]["design"].unique()
selected_design = st.sidebar.selectbox("Select Design", designs)

# Filter 3: Version (dependent on Design)
versions = data[(data["source_type"] == selected_type) & 
                (data["design"] == selected_design)]["version"].unique()
selected_version = st.sidebar.selectbox("Select Version", versions)

# Filter 4: Source ID (dependent on Version)
source_ids = data[(data["source_type"] == selected_type) & 
                  (data["design"] == selected_design) & 
                  (data["version"] == selected_version)]["source_id"].unique()
selected_source = st.sidebar.multiselect("Select Source ID(s)", source_ids, default=source_ids)

# Filter data
filtered_data = data[(data["source_type"] == selected_type) & 
                     (data["design"] == selected_design) &
                     (data["version"] == selected_version) &
                     (data["source_id"].isin(selected_source))]

# Show filtered dataset
st.subheader("Filtered Dataset")
st.dataframe(filtered_data)

# Example plot: Ion Energy vs Current Density
st.subheader("Ion Energy vs Current Density")
fig = px.scatter(
    filtered_data,
    x="ion_energy_ev",
    y="current_density_macm2",
    color="source_id",
    hover_data=["pressure_mbar", "rf_power_w", "primary_steps", "secondary_steps"]
)
st.plotly_chart(fig)

