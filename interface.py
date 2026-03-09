import streamlit as st
import pandas as pd
import plotly.express as px

st.image("CCRLogo.png", width=200)
st.title("CCR GmbH : RF Plasma Source Comparison Dashboard")

# Read Excel file
data = pd.read_excel("plasma_sources.xlsx")
data.columns = data.columns.str.strip().str.lower()

st.sidebar.header("Filters (Flexible)")

# Flexible multi-selects
selected_types = st.sidebar.multiselect(
    "Select Plasma Source Type",
    options=data["source_type"].unique(),
    default=data["source_type"].unique()
)

selected_designs = st.sidebar.multiselect(
    "Select Design",
    options=data[data["source_type"].isin(selected_types)]["design"].unique(),
    default=data[data["source_type"].isin(selected_types)]["design"].unique()
)

selected_versions = st.sidebar.multiselect(
    "Select Version",
    options=data[
        (data["source_type"].isin(selected_types)) &
        (data["design"].isin(selected_designs))
    ]["version"].unique(),
    default=data[
        (data["source_type"].isin(selected_types)) &
        (data["design"].isin(selected_designs))
    ]["version"].unique()
)

selected_sources = st.sidebar.multiselect(
    "Select Source ID(s)",
    options=data[
        (data["source_type"].isin(selected_types)) &
        (data["design"].isin(selected_designs)) &
        (data["version"].isin(selected_versions))
    ]["source_id"].unique(),
    default=data[
        (data["source_type"].isin(selected_types)) &
        (data["design"].isin(selected_designs)) &
        (data["version"].isin(selected_versions))
    ]["source_id"].unique()
)

# Filter the data based on all selections
filtered_data = data[
    (data["source_type"].isin(selected_types)) &
    (data["design"].isin(selected_designs)) &
    (data["version"].isin(selected_versions)) &
    (data["source_id"].isin(selected_sources))
]

st.subheader("Filtered Dataset")
st.dataframe(filtered_data)

# Plot selection
st.sidebar.header("Select Plots")
plot_options = st.sidebar.multiselect(
    "Choose plots",
    options=[
        "ICD vs Pressure",
        "IE vs Pressure",
        "ICD vs RF Power",
        "IE vs RF Power"
    ],
    default=[
        "ICD vs Pressure",
        "IE vs Pressure",
        "ICD vs RF Power",
        "IE vs RF Power"
    ]
)

# Dynamic plots
if "ICD vs Pressure" in plot_options:
    st.subheader("ICD vs Pressure")
    fig = px.scatter(
        filtered_data,
        x="pressure_mbar",
        y="ion_current_density",
        color="source_id",
        hover_data=["rf_power_w", "primary_steps", "secondary_steps"]
    )
    # Exponential x-axis, standard y-axis
    fig.update_xaxes(range=[1e-5, 1e-2], type="log")
    fig.update_yaxes(range=[0, filtered_data["ion_current_density"].max()*1.1])
    st.plotly_chart(fig)

if "IE vs Pressure" in plot_options:
    st.subheader("Ion Energy vs Pressure")
    fig = px.scatter(
        filtered_data,
        x="pressure_mbar",
        y="ion_energy_ev",
        color="source_id",
        hover_data=["rf_power_w", "primary_steps", "secondary_steps"]
    )
    fig.update_xaxes(range=[1e-5, 1e-2], type="log")
    fig.update_yaxes(range=[0, filtered_data["ion_energy_ev"].max()*1.1])
    st.plotly_chart(fig)

if "ICD vs RF Power" in plot_options:
    st.subheader("ICD vs RF Power")
    fig = px.scatter(
        filtered_data,
        x="rf_power_w",
        y="ion_current_density",
        color="source_id",
        hover_data=["pressure_mbar", "primary_steps", "secondary_steps"]
    )
    fig.update_yaxes(range=[0, filtered_data["ion_current_density"].max()*1.1])
    st.plotly_chart(fig)

if "IE vs RF Power" in plot_options:
    st.subheader("Ion Energy vs RF Power")
    fig = px.scatter(
        filtered_data,
        x="rf_power_w",
        y="ion_energy_ev",
        color="source_id",
        hover_data=["pressure_mbar", "primary_steps", "secondary_steps"]
    )
    fig.update_yaxes(range=[0, filtered_data["ion_energy_ev"].max()*1.1])
    st.plotly_chart(fig)
